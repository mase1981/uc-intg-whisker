"""
Whisker Litter-Robot sensor entities.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ucapi import sensor
from ucapi_framework import SensorEntity

from uc_intg_whisker.const import CYCLES_UNIT, PERCENT_UNIT

if TYPE_CHECKING:
    from uc_intg_whisker.config import WhiskerConfig
    from uc_intg_whisker.device import WhiskerDevice

_LOG = logging.getLogger(__name__)


class _WhiskerSensor(SensorEntity):
    """Base sensor bound to a single robot snapshot field."""

    _suffix = ""
    _label = "Sensor"
    _unit = ""

    def __init__(
        self, device_config: WhiskerConfig, device: WhiskerDevice, meta: dict[str, Any]
    ) -> None:
        self._device = device
        self._key = meta["key"]
        entity_id = f"sensor.{device_config.identifier}.{self._key}_{self._suffix}"
        super().__init__(
            entity_id,
            f"{meta['name']} {self._label}",
            [],
            {
                sensor.Attributes.STATE: sensor.States.UNKNOWN,
                sensor.Attributes.VALUE: "",
            },
            device_class=sensor.DeviceClasses.CUSTOM,
            options={sensor.Options.CUSTOM_UNIT: self._unit},
        )
        self.subscribe_to_device(device)

    def _value(self, snap: dict[str, Any]) -> Any:
        raise NotImplementedError

    async def sync_state(self) -> None:
        snap = self._device.robot_snapshot(self._key)
        if self._device.state == "UNAVAILABLE" or snap is None or not snap["online"]:
            self.update({sensor.Attributes.STATE: sensor.States.UNAVAILABLE})
            return
        value = self._value(snap)
        self.update(
            {
                sensor.Attributes.STATE: sensor.States.ON,
                sensor.Attributes.VALUE: "N/A" if value is None else str(value),
            }
        )


class StatusSensor(_WhiskerSensor):
    _suffix = "status"
    _label = "Status"
    _unit = ""

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["status_text"]


class WasteDrawerSensor(_WhiskerSensor):
    _suffix = "waste"
    _label = "Waste Drawer"
    _unit = PERCENT_UNIT

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["waste_level"]


class LitterLevelSensor(_WhiskerSensor):
    _suffix = "litter"
    _label = "Litter Level"
    _unit = PERCENT_UNIT

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["litter_level"]


class CycleCountSensor(_WhiskerSensor):
    _suffix = "cycles"
    _label = "Cycle Count"
    _unit = CYCLES_UNIT

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["cycle_count"]


class SleepModeSensor(_WhiskerSensor):
    _suffix = "sleep"
    _label = "Sleep Mode"
    _unit = ""

    def _value(self, snap: dict[str, Any]) -> Any:
        if snap["is_sleeping"]:
            return "Sleeping"
        if snap["sleep_mode"]:
            return "Scheduled"
        return "Off"


class SleepStartSensor(_WhiskerSensor):
    _suffix = "sleep_start"
    _label = "Sleep Start"
    _unit = ""

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["sleep_start"]


class SleepEndSensor(_WhiskerSensor):
    _suffix = "sleep_end"
    _label = "Sleep End"
    _unit = ""

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["sleep_end"]


class LastSeenSensor(_WhiskerSensor):
    _suffix = "last_seen"
    _label = "Last Seen"
    _unit = ""

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["last_seen"]


class PetWeightSensor(_WhiskerSensor):
    _suffix = "pet_weight"
    _label = "Pet Weight"
    _unit = "lb"

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["pet_weight"]


class HopperStatusSensor(_WhiskerSensor):
    _suffix = "hopper"
    _label = "Hopper Status"
    _unit = ""

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["hopper_status"]


class FoodLevelSensor(_WhiskerSensor):
    _suffix = "food"
    _label = "Food Level"
    _unit = PERCENT_UNIT

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["food_level"]


class LastFeedingSensor(_WhiskerSensor):
    _suffix = "last_feeding"
    _label = "Last Feeding"
    _unit = ""

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["last_feeding"]


class NextFeedingSensor(_WhiskerSensor):
    _suffix = "next_feeding"
    _label = "Next Feeding"
    _unit = ""

    def _value(self, snap: dict[str, Any]) -> Any:
        return snap["next_feeding"]
