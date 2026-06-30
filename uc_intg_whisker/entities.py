"""
Entity factory for the Whisker integration.

Builds a model-appropriate set of entities for every robot discovered on the
account, mirroring the per-model coverage of the Home Assistant Litter-Robot
integration (Litter-Robot 3, Litter-Robot 4, Feeder-Robot).

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ucapi import Entity

from uc_intg_whisker.button import (
    GiveSnackButton,
    ResetButton,
    ResetDrawerButton,
    StartCleaningButton,
)
from uc_intg_whisker.remote import WhiskerRemote
from uc_intg_whisker.select import (
    MealInsertSizeSelect,
    NightLightBrightnessSelect,
    NightLightModeSelect,
    PanelBrightnessSelect,
    WaitTimeSelect,
)
from uc_intg_whisker.sensor import (
    CycleCountSensor,
    FoodLevelSensor,
    HopperStatusSensor,
    LastFeedingSensor,
    LastSeenSensor,
    LitterLevelSensor,
    NextFeedingSensor,
    PetWeightSensor,
    SleepEndSensor,
    SleepModeSensor,
    SleepStartSensor,
    StatusSensor,
    WasteDrawerSensor,
)
from uc_intg_whisker.switch import (
    GravityModeSwitch,
    NightLightSwitch,
    PanelLockSwitch,
    PowerSwitch,
    SleepModeSwitch,
)

if TYPE_CHECKING:
    from uc_intg_whisker.config import WhiskerConfig
    from uc_intg_whisker.device import WhiskerDevice

_LOG = logging.getLogger(__name__)


def _litter_entities(cfg, dev, meta, is_lr4: bool) -> list[Entity]:
    ents: list[Entity] = [
        WhiskerRemote(cfg, dev, meta),
        # Sensors (all litter robots)
        StatusSensor(cfg, dev, meta),
        WasteDrawerSensor(cfg, dev, meta),
        CycleCountSensor(cfg, dev, meta),
        SleepModeSensor(cfg, dev, meta),
        SleepStartSensor(cfg, dev, meta),
        SleepEndSensor(cfg, dev, meta),
        LastSeenSensor(cfg, dev, meta),
        # Switches (all litter robots)
        PowerSwitch(cfg, dev, meta),
        PanelLockSwitch(cfg, dev, meta),
        SleepModeSwitch(cfg, dev, meta),
        # Buttons / selects (all litter robots)
        StartCleaningButton(cfg, dev, meta),
        WaitTimeSelect(cfg, dev, meta),
    ]
    if is_lr4:
        # Litter-Robot 4 extras
        ents.append(LitterLevelSensor(cfg, dev, meta))
        ents.append(PetWeightSensor(cfg, dev, meta))
        ents.append(HopperStatusSensor(cfg, dev, meta))
        ents.append(ResetButton(cfg, dev, meta))
        ents.append(NightLightModeSelect(cfg, dev, meta))
        ents.append(NightLightBrightnessSelect(cfg, dev, meta))
        ents.append(PanelBrightnessSelect(cfg, dev, meta))
    else:
        # Litter-Robot 3: simple night light switch + waste drawer reset
        ents.append(NightLightSwitch(cfg, dev, meta))
        ents.append(ResetDrawerButton(cfg, dev, meta))
    return ents


def _feeder_entities(cfg, dev, meta) -> list[Entity]:
    return [
        WhiskerRemote(cfg, dev, meta),
        FoodLevelSensor(cfg, dev, meta),
        LastFeedingSensor(cfg, dev, meta),
        NextFeedingSensor(cfg, dev, meta),
        NightLightSwitch(cfg, dev, meta),
        PanelLockSwitch(cfg, dev, meta),
        GravityModeSwitch(cfg, dev, meta),
        GiveSnackButton(cfg, dev, meta),
        MealInsertSizeSelect(cfg, dev, meta),
    ]


def build_entities(
    device_config: WhiskerConfig, device: WhiskerDevice
) -> list[Entity]:
    """Create model-appropriate entities for every robot on the account.

    Reads the robot metadata persisted in the config (not the live device), so
    entities can be created immediately on startup before the cloud connection
    is established. This is what makes entities survive a Remote reboot.
    """
    metas = device_config.robots or []
    entities: list[Entity] = []
    for meta in metas:
        kind = meta["kind"]
        if kind == "feeder":
            entities.extend(_feeder_entities(device_config, device, meta))
        else:
            entities.extend(
                _litter_entities(device_config, device, meta, is_lr4=(kind == "lr4"))
            )

    _LOG.info("Built %d entities for %d robot(s)", len(entities), len(metas))
    return entities
