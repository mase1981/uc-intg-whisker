"""
Whisker Litter-Robot switch entities.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ucapi import StatusCodes, switch
from ucapi_framework import SwitchEntity

if TYPE_CHECKING:
    from uc_intg_whisker.config import WhiskerConfig
    from uc_intg_whisker.device import WhiskerDevice

_LOG = logging.getLogger(__name__)


class _WhiskerSwitch(SwitchEntity):
    """Base switch bound to a single robot snapshot field."""

    _suffix = ""
    _label = "Switch"
    _field = ""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        entity_id = f"switch.{device_config.identifier}.{self._key}_{self._suffix}"
        super().__init__(
            entity_id,
            f"{meta['name']} {self._label}",
            [switch.Features.ON_OFF, switch.Features.TOGGLE],
            {switch.Attributes.STATE: switch.States.UNKNOWN},
            device_class=switch.DeviceClasses.SWITCH,
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def _apply(self, on: bool) -> bool:
        raise NotImplementedError

    async def sync_state(self) -> None:
        snap = self._device.robot_snapshot(self._key)
        if self._device.state == "UNAVAILABLE" or snap is None or not snap["online"]:
            self.update({switch.Attributes.STATE: switch.States.UNAVAILABLE})
            return
        self.update(
            {
                switch.Attributes.STATE: switch.States.ON
                if snap[self._field]
                else switch.States.OFF
            }
        )

    async def _handle_command(
        self, entity: switch.Switch, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id == switch.Commands.ON:
            ok = await self._apply(True)
        elif cmd_id == switch.Commands.OFF:
            ok = await self._apply(False)
        elif cmd_id == switch.Commands.TOGGLE:
            snap = self._device.robot_snapshot(self._key)
            current = bool(snap[self._field]) if snap else False
            ok = await self._apply(not current)
        else:
            return StatusCodes.NOT_IMPLEMENTED
        return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR


class NightLightSwitch(_WhiskerSwitch):
    _suffix = "night_light"
    _label = "Night Light"
    _field = "night_light"

    async def _apply(self, on: bool) -> bool:
        return await self._device.set_night_light(self._key, on)


class PanelLockSwitch(_WhiskerSwitch):
    _suffix = "panel_lock"
    _label = "Panel Lock"
    _field = "panel_lock"

    async def _apply(self, on: bool) -> bool:
        return await self._device.set_panel_lockout(self._key, on)


class PowerSwitch(_WhiskerSwitch):
    _suffix = "power"
    _label = "Power"
    _field = "power"

    async def _apply(self, on: bool) -> bool:
        return await self._device.set_power(self._key, on)


class SleepModeSwitch(_WhiskerSwitch):
    _suffix = "sleep_mode"
    _label = "Sleep Mode"
    _field = "sleep_mode"

    async def _apply(self, on: bool) -> bool:
        return await self._device.set_sleep_mode(self._key, on)


class GravityModeSwitch(_WhiskerSwitch):
    _suffix = "gravity_mode"
    _label = "Gravity Mode"
    _field = "gravity_mode"

    async def _apply(self, on: bool) -> bool:
        return await self._device.set_gravity_mode(self._key, on)
