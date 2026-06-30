"""
Constants for the Whisker Litter-Robot integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

POLL_INTERVAL = 30

PERCENT_UNIT = "%"
CYCLES_UNIT = "cycles"

DEFAULT_WAIT_TIMES = [3, 7, 15]

WAIT_TIME_SUFFIX = " min"

# Remote entity simple commands (discrete, activity-friendly)
CMD_POWER_ON = "POWER_ON"
CMD_POWER_OFF = "POWER_OFF"
CMD_START_CLEAN = "START_CLEAN"
CMD_NIGHT_LIGHT_ON = "NIGHT_LIGHT_ON"
CMD_NIGHT_LIGHT_OFF = "NIGHT_LIGHT_OFF"
CMD_PANEL_LOCK_ON = "PANEL_LOCK_ON"
CMD_PANEL_LOCK_OFF = "PANEL_LOCK_OFF"
CMD_RESET_DRAWER = "RESET_DRAWER"

CMD_SLEEP_MODE_ON = "SLEEP_MODE_ON"
CMD_SLEEP_MODE_OFF = "SLEEP_MODE_OFF"

BASE_REMOTE_COMMANDS = [
    CMD_POWER_ON,
    CMD_POWER_OFF,
    CMD_START_CLEAN,
    CMD_NIGHT_LIGHT_ON,
    CMD_NIGHT_LIGHT_OFF,
    CMD_PANEL_LOCK_ON,
    CMD_PANEL_LOCK_OFF,
    CMD_SLEEP_MODE_ON,
    CMD_SLEEP_MODE_OFF,
]

# Display name <-> pylitterbot enum name maps
NIGHT_LIGHT_MODE_TO_ENUM = {"Off": "OFF", "On": "ON", "Auto": "AUTO"}
NIGHT_LIGHT_MODE_FROM_ENUM = {v: k for k, v in NIGHT_LIGHT_MODE_TO_ENUM.items()}

PANEL_BRIGHTNESS_TO_ENUM = {"Low": "LOW", "Medium": "MEDIUM", "High": "HIGH"}
PANEL_BRIGHTNESS_FROM_ENUM = {v: k for k, v in PANEL_BRIGHTNESS_TO_ENUM.items()}
