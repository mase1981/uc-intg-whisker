"""
Entity factory for the Whisker Litter-Robot integration.

Builds the full set of entities for every Litter-Robot discovered on the
account after the device connection is established.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ucapi import Entity

from uc_intg_whisker.button import ResetDrawerButton, StartCleaningButton
from uc_intg_whisker.remote import WhiskerRemote
from uc_intg_whisker.select import (
    NightLightModeSelect,
    PanelBrightnessSelect,
    WaitTimeSelect,
)
from uc_intg_whisker.sensor import (
    CycleCountSensor,
    LastSeenSensor,
    LitterLevelSensor,
    SleepEndSensor,
    SleepModeSensor,
    SleepStartSensor,
    StatusSensor,
    WasteDrawerSensor,
)
from uc_intg_whisker.switch import (
    NightLightSwitch,
    PanelLockSwitch,
    PowerSwitch,
    SleepModeSwitch,
)

if TYPE_CHECKING:
    from uc_intg_whisker.config import WhiskerConfig
    from uc_intg_whisker.device import WhiskerDevice

_LOG = logging.getLogger(__name__)


def build_entities(
    device_config: WhiskerConfig, device: WhiskerDevice
) -> list[Entity]:
    """Create all entities for every Litter-Robot on the account."""
    entities: list[Entity] = []
    for meta in device.robot_metas:
        # Remote entity (activity-friendly discrete commands)
        entities.append(WhiskerRemote(device_config, device, meta))

        # Sensors
        entities.append(StatusSensor(device_config, device, meta))
        entities.append(WasteDrawerSensor(device_config, device, meta))
        if meta["has_litter_level"]:
            entities.append(LitterLevelSensor(device_config, device, meta))
        entities.append(CycleCountSensor(device_config, device, meta))
        entities.append(SleepModeSensor(device_config, device, meta))
        entities.append(SleepStartSensor(device_config, device, meta))
        entities.append(SleepEndSensor(device_config, device, meta))
        entities.append(LastSeenSensor(device_config, device, meta))

        # Switches
        entities.append(PowerSwitch(device_config, device, meta))
        entities.append(NightLightSwitch(device_config, device, meta))
        entities.append(PanelLockSwitch(device_config, device, meta))
        entities.append(SleepModeSwitch(device_config, device, meta))

        # Buttons
        entities.append(StartCleaningButton(device_config, device, meta))
        if meta["has_reset"]:
            entities.append(ResetDrawerButton(device_config, device, meta))

        # Selects
        entities.append(WaitTimeSelect(device_config, device, meta))
        if meta["is_lr4"]:
            entities.append(NightLightModeSelect(device_config, device, meta))
            entities.append(PanelBrightnessSelect(device_config, device, meta))

    _LOG.info("Built %d entities for %d robot(s)", len(entities), len(device.robot_metas))
    return entities
