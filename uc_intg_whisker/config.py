"""
Whisker Litter-Robot configuration for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from dataclasses import dataclass, field

from ucapi_framework import BaseConfigManager


@dataclass
class WhiskerConfig:
    """Whisker account configuration.

    ``robots`` holds the metadata discovered during setup (one dict per robot:
    key, kind, name, model, valid_wait_times, valid_meal_sizes). Persisting it
    lets entities be created immediately on startup without waiting for the
    cloud connection, which is required for reboot survival.
    """

    identifier: str = ""
    name: str = ""
    username: str = ""
    password: str = ""
    robots: list[dict] = field(default_factory=list)


class WhiskerConfigManager(BaseConfigManager[WhiskerConfig]):
    pass
