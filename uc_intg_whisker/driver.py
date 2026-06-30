"""
Whisker Litter-Robot driver for Unfolded Circle Remote.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging

from ucapi_framework import BaseIntegrationDriver

from uc_intg_whisker.config import WhiskerConfig
from uc_intg_whisker.device import WhiskerDevice
from uc_intg_whisker.entities import build_entities

_LOG = logging.getLogger(__name__)


class WhiskerDriver(BaseIntegrationDriver[WhiskerDevice, WhiskerConfig]):
    """Whisker Litter-Robot integration driver."""

    def __init__(self):
        super().__init__(
            device_class=WhiskerDevice,
            entity_classes=[
                lambda cfg, dev: build_entities(cfg, dev),
            ],
            driver_id="whisker",
            require_connection_before_registry=True,
        )
