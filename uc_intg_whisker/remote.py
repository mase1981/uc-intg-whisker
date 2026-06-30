"""
Whisker remote entity.

Aggregates a robot's discrete commands into a single Remote entity so they can
be driven from Remote activities and custom UI pages. The command set and UI
adapt to the robot model (Litter-Robot 3/4 vs Feeder-Robot).

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ucapi import StatusCodes, remote
from ucapi.ui import Buttons, Size, UiPage, create_btn_mapping, create_ui_text
from ucapi_framework import RemoteEntity

from uc_intg_whisker.const import (
    CMD_GIVE_SNACK,
    CMD_GRAVITY_OFF,
    CMD_GRAVITY_ON,
    CMD_NIGHT_LIGHT_OFF,
    CMD_NIGHT_LIGHT_ON,
    CMD_PANEL_LOCK_OFF,
    CMD_PANEL_LOCK_ON,
    CMD_POWER_OFF,
    CMD_POWER_ON,
    CMD_RESET,
    CMD_RESET_DRAWER,
    CMD_SLEEP_MODE_OFF,
    CMD_SLEEP_MODE_ON,
    CMD_START_CLEAN,
    FEEDER_REMOTE_COMMANDS,
    LITTER_REMOTE_COMMANDS,
)

if TYPE_CHECKING:
    from uc_intg_whisker.config import WhiskerConfig
    from uc_intg_whisker.device import WhiskerDevice

_LOG = logging.getLogger(__name__)


class WhiskerRemote(RemoteEntity):
    """Remote control surface for a single robot (model-aware)."""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        self._kind = meta["kind"]

        if self._kind == "feeder":
            commands, ui_items, features, mapping = self._build_feeder()
        else:
            commands, ui_items, features, mapping = self._build_litter(meta)

        entity_id = f"remote.{device_config.identifier}.{self._key}"
        super().__init__(
            entity_id,
            f"{meta['name']} Remote",
            features,
            {remote.Attributes.STATE: remote.States.UNKNOWN},
            simple_commands=commands,
            button_mapping=mapping,
            ui_pages=[UiPage("main", "Controls", grid=Size(4, 6), items=ui_items)],
            cmd_handler=self._handle_command,
        )
        self.subscribe_to_device(device)

    def _build_litter(self, meta: dict[str, Any]):
        commands = list(LITTER_REMOTE_COMMANDS)
        reset_cmd = CMD_RESET if meta["kind"] == "lr4" else CMD_RESET_DRAWER
        reset_label = "Reset" if meta["kind"] == "lr4" else "Reset Waste Drawer"
        commands.append(reset_cmd)
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
            create_ui_text(reset_label, 0, 5, size=Size(4, 1), cmd=reset_cmd),
        ]
        features = [
            remote.Features.ON_OFF,
            remote.Features.TOGGLE,
            remote.Features.SEND_CMD,
        ]
        mapping = [
            create_btn_mapping(Buttons.POWER, short=CMD_POWER_ON),
            create_btn_mapping(Buttons.GREEN, short=CMD_START_CLEAN),
        ]
        return commands, ui_items, features, mapping

    def _build_feeder(self):
        commands = list(FEEDER_REMOTE_COMMANDS)
        ui_items = [
            create_ui_text("Give Snack", 0, 0, size=Size(4, 1), cmd=CMD_GIVE_SNACK),
            create_ui_text("Night Light On", 0, 1, size=Size(2, 1), cmd=CMD_NIGHT_LIGHT_ON),
            create_ui_text("Night Light Off", 2, 1, size=Size(2, 1), cmd=CMD_NIGHT_LIGHT_OFF),
            create_ui_text("Panel Lock On", 0, 2, size=Size(2, 1), cmd=CMD_PANEL_LOCK_ON),
            create_ui_text("Panel Lock Off", 2, 2, size=Size(2, 1), cmd=CMD_PANEL_LOCK_OFF),
            create_ui_text("Gravity On", 0, 3, size=Size(2, 1), cmd=CMD_GRAVITY_ON),
            create_ui_text("Gravity Off", 2, 3, size=Size(2, 1), cmd=CMD_GRAVITY_OFF),
        ]
        features = [remote.Features.SEND_CMD]
        mapping = [create_btn_mapping(Buttons.GREEN, short=CMD_GIVE_SNACK)]
        return commands, ui_items, features, mapping

    async def sync_state(self) -> None:
        snap = self._device.robot_snapshot(self._key)
        if self._device.state == "UNAVAILABLE" or snap is None or not snap["online"]:
            self.update({remote.Attributes.STATE: remote.States.UNAVAILABLE})
            return
        if self._kind == "feeder":
            self.update({remote.Attributes.STATE: remote.States.ON})
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
        if command == CMD_RESET:
            return await dev.reset(key)
        if command == CMD_GIVE_SNACK:
            return await dev.give_snack(key)
        if command == CMD_GRAVITY_ON:
            return await dev.set_gravity_mode(key, True)
        if command == CMD_GRAVITY_OFF:
            return await dev.set_gravity_mode(key, False)
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
