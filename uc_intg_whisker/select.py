"""
Whisker Litter-Robot select entities.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ucapi import StatusCodes, select
from ucapi_framework import SelectEntity

from uc_intg_whisker.const import (
    NIGHT_LIGHT_MODE_FROM_ENUM,
    NIGHT_LIGHT_MODE_TO_ENUM,
    PANEL_BRIGHTNESS_FROM_ENUM,
    PANEL_BRIGHTNESS_TO_ENUM,
    WAIT_TIME_SUFFIX,
)

if TYPE_CHECKING:
    from uc_intg_whisker.config import WhiskerConfig
    from uc_intg_whisker.device import WhiskerDevice

_LOG = logging.getLogger(__name__)


class WaitTimeSelect(SelectEntity):
    """Clean cycle wait time selection for a robot."""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        self._wait_times = [int(t) for t in meta["valid_wait_times"]]
        entity_id = f"select.{device_config.identifier}.{self._key}_wait_time"
        super().__init__(
            entity_id,
            f"{meta['name']} Clean Cycle Wait Time",
            {
                select.Attributes.STATE: select.States.UNKNOWN,
                select.Attributes.OPTIONS: [],
                select.Attributes.CURRENT_OPTION: "",
            },
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    def _options(self) -> list[str]:
        return [f"{t}{WAIT_TIME_SUFFIX}" for t in self._wait_times]

    async def sync_state(self) -> None:
        snap = self._device.robot_snapshot(self._key)
        if self._device.state == "UNAVAILABLE" or snap is None or not snap["online"]:
            self.update({select.Attributes.STATE: select.States.UNAVAILABLE})
            return
        wait_time = snap["wait_time"]
        current = f"{int(wait_time)}{WAIT_TIME_SUFFIX}" if wait_time is not None else ""
        options = self._options()
        if current and current not in options:
            current = ""
        self.update(
            {
                select.Attributes.STATE: select.States.ON,
                select.Attributes.OPTIONS: options,
                select.Attributes.CURRENT_OPTION: current,
            }
        )

    async def _handle_command(
        self, entity: select.Select, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id != select.Commands.SELECT_OPTION:
            return StatusCodes.NOT_IMPLEMENTED
        option = params.get("option", "") if params else ""
        if not option:
            return StatusCodes.BAD_REQUEST
        try:
            minutes = int(option.replace(WAIT_TIME_SUFFIX, "").strip())
        except ValueError:
            return StatusCodes.BAD_REQUEST
        if minutes not in self._wait_times:
            return StatusCodes.BAD_REQUEST
        ok = await self._device.set_wait_time(self._key, minutes)
        return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR


class NightLightModeSelect(SelectEntity):
    """Night light mode (Off / On / Auto) for Litter-Robot 4."""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        entity_id = f"select.{device_config.identifier}.{self._key}_night_light_mode"
        super().__init__(
            entity_id,
            f"{meta['name']} Night Light Mode",
            {
                select.Attributes.STATE: select.States.UNKNOWN,
                select.Attributes.OPTIONS: [],
                select.Attributes.CURRENT_OPTION: "",
            },
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        snap = self._device.robot_snapshot(self._key)
        if self._device.state == "UNAVAILABLE" or snap is None or not snap["online"]:
            self.update({select.Attributes.STATE: select.States.UNAVAILABLE})
            return
        current = NIGHT_LIGHT_MODE_FROM_ENUM.get(snap.get("night_light_mode") or "", "")
        self.update(
            {
                select.Attributes.STATE: select.States.ON,
                select.Attributes.OPTIONS: list(NIGHT_LIGHT_MODE_TO_ENUM.keys()),
                select.Attributes.CURRENT_OPTION: current,
            }
        )

    async def _handle_command(
        self, entity: select.Select, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id != select.Commands.SELECT_OPTION:
            return StatusCodes.NOT_IMPLEMENTED
        option = params.get("option", "") if params else ""
        enum_name = NIGHT_LIGHT_MODE_TO_ENUM.get(option)
        if not enum_name:
            return StatusCodes.BAD_REQUEST
        ok = await self._device.set_night_light_mode(self._key, enum_name)
        return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR


class PanelBrightnessSelect(SelectEntity):
    """Panel brightness (Low / Medium / High) for Litter-Robot 4."""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        entity_id = f"select.{device_config.identifier}.{self._key}_panel_brightness"
        super().__init__(
            entity_id,
            f"{meta['name']} Panel Brightness",
            {
                select.Attributes.STATE: select.States.UNKNOWN,
                select.Attributes.OPTIONS: [],
                select.Attributes.CURRENT_OPTION: "",
            },
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        snap = self._device.robot_snapshot(self._key)
        if self._device.state == "UNAVAILABLE" or snap is None or not snap["online"]:
            self.update({select.Attributes.STATE: select.States.UNAVAILABLE})
            return
        current = PANEL_BRIGHTNESS_FROM_ENUM.get(snap.get("panel_brightness") or "", "")
        self.update(
            {
                select.Attributes.STATE: select.States.ON,
                select.Attributes.OPTIONS: list(PANEL_BRIGHTNESS_TO_ENUM.keys()),
                select.Attributes.CURRENT_OPTION: current,
            }
        )

    async def _handle_command(
        self, entity: select.Select, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id != select.Commands.SELECT_OPTION:
            return StatusCodes.NOT_IMPLEMENTED
        option = params.get("option", "") if params else ""
        enum_name = PANEL_BRIGHTNESS_TO_ENUM.get(option)
        if not enum_name:
            return StatusCodes.BAD_REQUEST
        ok = await self._device.set_panel_brightness(self._key, enum_name)
        return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
