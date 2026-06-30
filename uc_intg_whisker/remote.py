"""
Whisker Litter-Robot remote entity.

Aggregates a robot's discrete commands into a single Remote entity so they can
be driven from Remote activities and custom UI pages.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ucapi import StatusCodes, remote
from ucapi.ui import Size, UiPage, create_btn_mapping, create_ui_text
from ucapi.ui import Buttons
from ucapi_framework import RemoteEntity

from uc_intg_whisker.const import (
    BASE_REMOTE_COMMANDS,
    CMD_NIGHT_LIGHT_OFF,
    CMD_NIGHT_LIGHT_ON,
    CMD_PANEL_LOCK_OFF,
    CMD_PANEL_LOCK_ON,
    CMD_POWER_OFF,
    CMD_POWER_ON,
    CMD_RESET_DRAWER,
    CMD_SLEEP_MODE_OFF,
    CMD_SLEEP_MODE_ON,
    CMD_START_CLEAN,
)

if TYPE_CHECKING:
    from uc_intg_whisker.config import WhiskerConfig
    from uc_intg_whisker.device import WhiskerDevice

_LOG = logging.getLogger(__name__)


class WhiskerRemote(RemoteEntity):
    """Remote control surface for a single Litter-Robot."""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]

        commands = list(BASE_REMOTE_COMMANDS)
        if meta["has_reset"]:
            commands.append(CMD_RESET_DRAWER)

        ui_items = [
            create_ui_text("Power On", 0, 0, size=Size(2, 1), cmd=CMD_POWER_ON),
            create_ui_text("Power Off", 2, 0, size=Size(2, 1), cmd=CMD_POWER_OFF),
            create_ui_text("Start Clean Cycle", 0, 1, size=Size(4, 1), cmd=CMD_START_CLEAN),
            create_ui_text("Night Light On", 0, 2, size=Size(2, 1), cmd=CMD_NIGHT_LIGHT_ON),
            create_ui_text("Night Light Off", 2, 2, size=Size(2, 1), cmd=CMD_NIGHT_LIGHT_OFF),
            create_ui_text("Panel Lock On", 0, 3, size=Size(2, 1), cmd=CMD_PANEL_LOCK_ON),
            create_ui_text("Panel Lock Off", 2, 3, size=Size(2, 1), cmd=CMD_PANEL_LOCK_OFF),
            create_ui_text("Sleep Mode On", 0, 4, size=Size(2, 1), cmd=CMD_SLEEP_MODE_ON),
            create_ui_text("Sleep Mode Off", 2, 4, size=Size(2, 1), cmd=CMD_SLEEP_MODE_OFF),
        ]
        if meta["has_reset"]:
            ui_items.append(
                create_ui_text(
                    "Reset Waste Drawer", 0, 5, size=Size(4, 1), cmd=CMD_RESET_DRAWER
                )
            )

        entity_id = f"remote.{device_config.identifier}.{self._key}"
        super().__init__(
            entity_id,
            f"{meta['name']} Remote",
            [remote.Features.ON_OFF, remote.Features.TOGGLE, remote.Features.SEND_CMD],
            {remote.Attributes.STATE: remote.States.UNKNOWN},
            simple_commands=commands,
            button_mapping=[
                create_btn_mapping(Buttons.POWER, short=CMD_POWER_ON),
                create_btn_mapping(Buttons.GREEN, short=CMD_START_CLEAN),
            ],
            ui_pages=[
                UiPage("main", "Litter-Robot", grid=Size(4, 6), items=ui_items),
            ],
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        snap = self._device.robot_snapshot(self._key)
        if self._device.state == "UNAVAILABLE" or snap is None or not snap["online"]:
            self.update({remote.Attributes.STATE: remote.States.UNAVAILABLE})
            return
        self.update(
            {
                remote.Attributes.STATE: remote.States.ON
                if snap["power"]
                else remote.States.OFF
            }
        )

    async def _run(self, command: str) -> bool:
        key = self._key
        dev = self._device
        if command == CMD_POWER_ON:
            return await dev.set_power(key, True)
        if command == CMD_POWER_OFF:
            return await dev.set_power(key, False)
        if command == CMD_START_CLEAN:
            return await dev.start_cleaning(key)
        if command == CMD_NIGHT_LIGHT_ON:
            return await dev.set_night_light(key, True)
        if command == CMD_NIGHT_LIGHT_OFF:
            return await dev.set_night_light(key, False)
        if command == CMD_PANEL_LOCK_ON:
            return await dev.set_panel_lockout(key, True)
        if command == CMD_PANEL_LOCK_OFF:
            return await dev.set_panel_lockout(key, False)
        if command == CMD_SLEEP_MODE_ON:
            return await dev.set_sleep_mode(key, True)
        if command == CMD_SLEEP_MODE_OFF:
            return await dev.set_sleep_mode(key, False)
        if command == CMD_RESET_DRAWER:
            return await dev.reset_waste_drawer(key)
        return False

    async def _handle_command(
        self, entity: remote.Remote, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id == remote.Commands.ON:
            ok = await self._device.set_power(self._key, True)
        elif cmd_id == remote.Commands.OFF:
            ok = await self._device.set_power(self._key, False)
        elif cmd_id == remote.Commands.TOGGLE:
            snap = self._device.robot_snapshot(self._key)
            current = bool(snap["power"]) if snap else False
            ok = await self._device.set_power(self._key, not current)
        elif cmd_id == remote.Commands.SEND_CMD:
            command = params.get("command", "") if params else ""
            if not command:
                return StatusCodes.BAD_REQUEST
            ok = await self._run(command)
        else:
            return StatusCodes.NOT_IMPLEMENTED
        return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
