"""
Whisker Litter-Robot button entities.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ucapi import StatusCodes, button
from ucapi_framework import ButtonEntity

if TYPE_CHECKING:
    from uc_intg_whisker.config import WhiskerConfig
    from uc_intg_whisker.device import WhiskerDevice

_LOG = logging.getLogger(__name__)


class StartCleaningButton(ButtonEntity):
    """Trigger a clean cycle on a robot."""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        entity_id = f"button.{device_config.identifier}.{self._key}_clean"
        super().__init__(
            entity_id,
            f"{meta['name']} Clean Cycle",
            cmd_handler=self._handle_command,
        )

    async def _handle_command(
        self, entity: button.Button, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id == button.Commands.PUSH:
            ok = await self._device.start_cleaning(self._key)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
        return StatusCodes.NOT_IMPLEMENTED


class ResetDrawerButton(ButtonEntity):
    """Reset the waste drawer gauge on a Litter-Robot 3."""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        entity_id = f"button.{device_config.identifier}.{self._key}_reset"
        super().__init__(
            entity_id,
            f"{meta['name']} Reset Waste Drawer",
            cmd_handler=self._handle_command,
        )

    async def _handle_command(
        self, entity: button.Button, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id == button.Commands.PUSH:
            ok = await self._device.reset_waste_drawer(self._key)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
        return StatusCodes.NOT_IMPLEMENTED


class ResetButton(ButtonEntity):
    """Reset a Litter-Robot 4."""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        entity_id = f"button.{device_config.identifier}.{self._key}_reset"
        super().__init__(
            entity_id,
            f"{meta['name']} Reset",
            cmd_handler=self._handle_command,
        )

    async def _handle_command(
        self, entity: button.Button, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id == button.Commands.PUSH:
            ok = await self._device.reset(self._key)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
        return StatusCodes.NOT_IMPLEMENTED


class GiveSnackButton(ButtonEntity):
    """Dispense a snack on a Feeder-Robot."""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        entity_id = f"button.{device_config.identifier}.{self._key}_snack"
        super().__init__(
            entity_id,
            f"{meta['name']} Give Snack",
            cmd_handler=self._handle_command,
        )

    async def _handle_command(
        self, entity: button.Button, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        if cmd_id == button.Commands.PUSH:
            ok = await self._device.give_snack(self._key)
            return StatusCodes.OK if ok else StatusCodes.SERVER_ERROR
        return StatusCodes.NOT_IMPLEMENTED
