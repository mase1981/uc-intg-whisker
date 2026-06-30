"""
Whisker Litter-Robot configuration for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from dataclasses import dataclass

from ucapi_framework import BaseConfigManager


@dataclass
class WhiskerConfig:
    """Whisker account configuration."""

    identifier: str = ""
    name: str = ""
    username: str = ""
    password: str = ""


class WhiskerConfigManager(BaseConfigManager[WhiskerConfig]):
    pass
