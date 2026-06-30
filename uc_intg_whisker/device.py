"""
Whisker Litter-Robot device implementation for Unfolded Circle integration.

A single Whisker account is modelled as one device. Each Litter-Robot on the
account exposes its own set of entities, created dynamically from the robots
discovered after the cloud connection is established.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import asyncio
import logging
import ssl
from typing import Any, Callable

import aiohttp
import certifi
from pylitterbot import Account, FeederRobot, LitterRobot3, LitterRobot4
from pylitterbot.enums import BrightnessLevel, NightLightMode
from ucapi_framework import DeviceEvents, PollingDevice

from uc_intg_whisker.config import WhiskerConfig
from uc_intg_whisker.const import DEFAULT_WAIT_TIMES, POLL_INTERVAL

_LOG = logging.getLogger(__name__)

_SUPPORTED_TYPES = (LitterRobot3, LitterRobot4, FeederRobot)

KIND_LR3 = "lr3"
KIND_LR4 = "lr4"
KIND_FEEDER = "feeder"


def _robot_kind(robot: Any) -> str | None:
    if isinstance(robot, LitterRobot4):
        return KIND_LR4
    if isinstance(robot, LitterRobot3):
        return KIND_LR3
    if isinstance(robot, FeederRobot):
        return KIND_FEEDER
    return None


def robot_key(robot: Any) -> str:
    """Stable entity-id-safe key for a robot."""
    return str(robot.id).replace(".", "_").replace(" ", "_")


async def discover_robot_metas(username: str, password: str) -> list[dict[str, Any]]:
    """Connect to the Whisker cloud and return persisted metadata for every robot.

    Used by the setup flow and by startup config migration so entities can be
    built from config without a live device connection.
    """
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_ctx)
    session = aiohttp.ClientSession(connector=connector)
    account = Account(websession=session)
    try:
        await account.connect(username=username, password=password, load_robots=True)
        return [m for m in (build_robot_meta(r) for r in account.robots) if m]
    finally:
        try:
            await account.disconnect()
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        if not session.closed:
            await session.close()


def build_robot_meta(robot: Any) -> dict[str, Any] | None:
    """Build the persisted metadata dict for a robot, or None if unsupported.

    Shared by the setup flow (to persist into config) and the device (so the
    entity factory can create entities from config without a live connection).
    """
    kind = _robot_kind(robot)
    if kind is None:
        return None
    default_name = "Feeder-Robot" if kind == KIND_FEEDER else "Litter-Robot"
    return {
        "key": robot_key(robot),
        "kind": kind,
        "name": robot.name or default_name,
        "model": getattr(robot, "model", "") or "",
        "valid_wait_times": list(
            getattr(type(robot), "VALID_WAIT_TIMES", DEFAULT_WAIT_TIMES)
        ),
        "valid_meal_sizes": list(getattr(type(robot), "VALID_MEAL_INSERT_SIZES", [])),
    }


class WhiskerDevice(PollingDevice):
    """Whisker account implementation using PollingDevice."""

    def __init__(self, device_config: WhiskerConfig, **kwargs: Any) -> None:
        super().__init__(device_config, poll_interval=POLL_INTERVAL, **kwargs)
        self._device_config = device_config
        self._connect_lock: asyncio.Lock = asyncio.Lock()
        self._lifecycle_lock: asyncio.Lock = asyncio.Lock()
        self._ssl_ctx = ssl.create_default_context(cafile=certifi.where())

        self._account: Account | None = None
        self._session: aiohttp.ClientSession | None = None
        self._connected: bool = False

        self._state: str = "UNAVAILABLE"
        self._robots: dict[str, Any] = {}
        self._robot_state: dict[str, dict[str, Any]] = {}
        self.robot_metas: list[dict[str, Any]] = []

    @property
    def identifier(self) -> str:
        return self._device_config.identifier

    @property
    def name(self) -> str:
        return self._device_config.name

    @property
    def address(self) -> str | None:
        return None

    @property
    def log_id(self) -> str:
        return f"Whisker ({self._device_config.username})"

    @property
    def state(self) -> str:
        return self._state

    def robot_snapshot(self, key: str) -> dict[str, Any] | None:
        """Return the last polled snapshot for a robot, or None if unknown."""
        return self._robot_state.get(key)

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> bool:
        # Serialize the framework's concurrent connect() calls (device-added +
        # subscribe + r2-connect paths) so only one poll loop is ever started.
        async with self._lifecycle_lock:
            return await super().connect()

    async def establish_connection(self) -> None:
        async with self._connect_lock:
            if self._account is None:
                connector = aiohttp.TCPConnector(ssl=self._ssl_ctx)
                self._session = aiohttp.ClientSession(connector=connector)
                self._account = Account(websession=self._session)

            if not self._connected:
                _LOG.info("[%s] Connecting to Whisker cloud", self.log_id)
                await self._account.connect(
                    username=self._device_config.username,
                    password=self._device_config.password,
                    load_robots=True,
                )
                self._connected = True

            self._build_robots()
            if not self._robots:
                raise ConnectionError(
                    "No Litter-Robot devices found on this Whisker account"
                )

            self._snapshot()
            self._state = "ON"
            self._persist_robot_metas()
            _LOG.info(
                "[%s] Connected - %d Litter-Robot(s)", self.log_id, len(self._robots)
            )
        # Push immediately so subscribed entities sync the moment we connect
        # (coordinator contract) instead of waiting for the first poll.
        self.push_update()

    def _persist_robot_metas(self) -> None:
        """Keep config.robots in sync with discovered robots (self-heals upgrades
        and reflects added/removed robots) so entities survive the next reboot."""
        current = list(getattr(self._device_config, "robots", []) or [])
        if self.robot_metas and self.robot_metas != current:
            try:
                self.update_config(robots=self.robot_metas)
                _LOG.info("[%s] Persisted robot metadata", self.log_id)
            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOG.debug("[%s] Could not persist robot metadata: %s", self.log_id, err)

    async def poll_device(self) -> None:
        if self._account is None:
            return
        try:
            await self._update_state()
            self.push_update()
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.debug("[%s] Poll error: %s", self.log_id, err)
            if self._state != "UNAVAILABLE":
                self._state = "UNAVAILABLE"
                self.events.emit(DeviceEvents.DISCONNECTED, self.identifier)

    async def _update_state(self) -> None:
        try:
            await self._account.refresh_robots()
        except Exception as err:  # pylint: disable=broad-exception-caught
            raise ConnectionError(f"Failed to refresh Whisker account: {err}") from err
        self._build_robots()
        self._snapshot()
        self._state = "ON"

    async def disconnect(self) -> None:
        async with self._connect_lock:
            if self._account is not None:
                try:
                    await self._account.disconnect()
                except Exception as err:  # pylint: disable=broad-exception-caught
                    _LOG.debug("[%s] Disconnect error: %s", self.log_id, err)
                self._account = None
            if self._session is not None and not self._session.closed:
                try:
                    await self._session.close()
                except Exception as err:  # pylint: disable=broad-exception-caught
                    _LOG.debug("[%s] Session close error: %s", self.log_id, err)
                self._session = None
            self._connected = False
            self._robots = {}
        self._state = "UNAVAILABLE"
        await super().disconnect()

    # ------------------------------------------------------------------
    # Robot discovery and state snapshots
    # ------------------------------------------------------------------

    def _build_robots(self) -> None:
        robots: dict[str, Any] = {}
        metas: list[dict[str, Any]] = []
        for robot in self._account.robots:
            meta = build_robot_meta(robot)
            if meta is None:
                continue
            robots[meta["key"]] = robot
            metas.append(meta)
        self._robots = robots
        self.robot_metas = metas

    @staticmethod
    def _status_text(robot: Any) -> str:
        status = getattr(robot, "status", None)
        text = getattr(status, "text", None)
        if text:
            return text
        text = getattr(robot, "status_text", None)
        if text:
            return text
        name = getattr(status, "name", None)
        return name or "Unknown"

    @staticmethod
    def _round(value: Any) -> Any:
        try:
            return round(float(value))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _enum_name(value: Any) -> str | None:
        name = getattr(value, "name", None)
        return str(name) if name else None

    @staticmethod
    def _fmt_time(value: Any) -> str | None:
        if value is None:
            return None
        try:
            return value.strftime("%H:%M")
        except (AttributeError, ValueError):
            return str(value)

    @staticmethod
    def _fmt_datetime(value: Any) -> str | None:
        if value is None:
            return None
        try:
            return value.strftime("%Y-%m-%d %H:%M")
        except (AttributeError, ValueError):
            return str(value)

    @staticmethod
    def _feeding_time(value: Any) -> str | None:
        if not value:
            return None
        if isinstance(value, dict):
            value = value.get("timestamp")
        return WhiskerDevice._fmt_datetime(value)

    def _snapshot(self) -> None:
        states: dict[str, dict[str, Any]] = {}
        for key, robot in self._robots.items():
            kind = _robot_kind(robot)
            snap: dict[str, Any] = {
                "kind": kind,
                "online": bool(getattr(robot, "is_online", True)),
                "power": bool(getattr(robot, "is_on", False)),
                "night_light": bool(getattr(robot, "night_light_mode_enabled", False)),
                "panel_lock": bool(getattr(robot, "panel_lock_enabled", False)),
            }
            if kind in (KIND_LR3, KIND_LR4):
                snap.update(
                    {
                        "status_text": self._status_text(robot),
                        "waste_level": self._round(getattr(robot, "waste_drawer_level", None)),
                        "cycle_count": getattr(robot, "cycle_count", None),
                        "sleep_mode": bool(getattr(robot, "sleep_mode_enabled", False)),
                        "is_sleeping": bool(getattr(robot, "is_sleeping", False)),
                        "sleep_start": self._fmt_time(getattr(robot, "sleep_mode_start_time", None)),
                        "sleep_end": self._fmt_time(getattr(robot, "sleep_mode_end_time", None)),
                        "wait_time": getattr(robot, "clean_cycle_wait_time_minutes", None),
                        "last_seen": self._fmt_datetime(getattr(robot, "last_seen", None)),
                    }
                )
            if kind == KIND_LR4:
                snap.update(
                    {
                        "litter_level": self._round(getattr(robot, "litter_level", None)),
                        "pet_weight": getattr(robot, "pet_weight", None),
                        "hopper_status": self._enum_name(getattr(robot, "hopper_status", None)),
                        "night_light_mode": self._enum_name(getattr(robot, "night_light_mode", None)),
                        "night_light_brightness": getattr(robot, "night_light_brightness", None),
                        "panel_brightness": self._enum_name(getattr(robot, "panel_brightness", None)),
                    }
                )
            if kind == KIND_FEEDER:
                snap.update(
                    {
                        "food_level": self._round(getattr(robot, "food_level", None)),
                        "last_feeding": self._feeding_time(getattr(robot, "last_feeding", None)),
                        "next_feeding": self._fmt_datetime(getattr(robot, "next_feeding", None)),
                        "gravity_mode": bool(getattr(robot, "gravity_mode_enabled", False)),
                        "meal_insert_size": getattr(robot, "meal_insert_size", None),
                    }
                )
            states[key] = snap
        self._robot_state = states

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    async def _command(
        self, key: str, action: Callable[[Any], Any], label: str
    ) -> bool:
        robot = self._robots.get(key)
        if robot is None:
            _LOG.warning("[%s] %s: robot %s not found", self.log_id, label, key)
            return False
        try:
            await action(robot)
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.error("[%s] %s failed for %s: %s", self.log_id, label, key, err)
            return False
        try:
            await robot.refresh()
        except Exception as err:  # pylint: disable=broad-exception-caught
            _LOG.debug("[%s] Refresh after %s failed: %s", self.log_id, label, err)
        self._snapshot()
        self.push_update()
        return True

    async def start_cleaning(self, key: str) -> bool:
        return await self._command(key, lambda r: r.start_cleaning(), "start_cleaning")

    async def reset_waste_drawer(self, key: str) -> bool:
        return await self._command(
            key, lambda r: r.reset_waste_drawer(), "reset_waste_drawer"
        )

    async def reset(self, key: str) -> bool:
        return await self._command(key, lambda r: r.reset(), "reset")

    async def set_night_light(self, key: str, on: bool) -> bool:
        robot = self._robots.get(key)
        # Litter-Robot 4 has no set_night_light(); it only honors the mode command.
        if isinstance(robot, LitterRobot4):
            mode = NightLightMode.ON if on else NightLightMode.OFF
            return await self._command(
                key, lambda r: r.set_night_light_mode(mode), "set_night_light"
            )
        return await self._command(
            key, lambda r: r.set_night_light(on), "set_night_light"
        )

    async def set_panel_lockout(self, key: str, on: bool) -> bool:
        return await self._command(
            key, lambda r: r.set_panel_lockout(on), "set_panel_lockout"
        )

    async def set_power(self, key: str, on: bool) -> bool:
        return await self._command(
            key, lambda r: r.set_power_status(on), "set_power_status"
        )

    async def set_wait_time(self, key: str, minutes: int) -> bool:
        return await self._command(
            key, lambda r: r.set_wait_time(minutes), "set_wait_time"
        )

    async def set_sleep_mode(self, key: str, on: bool) -> bool:
        robot = self._robots.get(key)
        sleep_time = None
        if on and robot is not None:
            start = getattr(robot, "sleep_mode_start_time", None)
            if start is not None:
                try:
                    sleep_time = start.timetz()
                except (AttributeError, ValueError):
                    sleep_time = None
        return await self._command(
            key, lambda r: r.set_sleep_mode(on, sleep_time), "set_sleep_mode"
        )

    async def set_night_light_mode(self, key: str, mode_name: str) -> bool:
        try:
            mode = NightLightMode[mode_name]
        except KeyError:
            _LOG.error("[%s] Unknown night light mode: %s", self.log_id, mode_name)
            return False
        return await self._command(
            key, lambda r: r.set_night_light_mode(mode), "set_night_light_mode"
        )

    async def set_panel_brightness(self, key: str, level_name: str) -> bool:
        try:
            level = BrightnessLevel[level_name]
        except KeyError:
            _LOG.error("[%s] Unknown panel brightness: %s", self.log_id, level_name)
            return False
        return await self._command(
            key, lambda r: r.set_panel_brightness(level), "set_panel_brightness"
        )

    async def set_night_light_brightness(self, key: str, level_name: str) -> bool:
        try:
            level = BrightnessLevel[level_name]
        except KeyError:
            _LOG.error("[%s] Unknown night light brightness: %s", self.log_id, level_name)
            return False
        return await self._command(
            key,
            lambda r: r.set_night_light_brightness(level),
            "set_night_light_brightness",
        )

    async def give_snack(self, key: str) -> bool:
        return await self._command(key, lambda r: r.give_snack(), "give_snack")

    async def set_gravity_mode(self, key: str, on: bool) -> bool:
        return await self._command(
            key, lambda r: r.set_gravity_mode(on), "set_gravity_mode"
        )

    async def set_meal_insert_size(self, key: str, size: float) -> bool:
        return await self._command(
            key, lambda r: r.set_meal_insert_size(size), "set_meal_insert_size"
        )
