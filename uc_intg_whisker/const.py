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
CMD_RESET = "RESET"
CMD_GIVE_SNACK = "GIVE_SNACK"
CMD_GRAVITY_ON = "GRAVITY_ON"
CMD_GRAVITY_OFF = "GRAVITY_OFF"

# Litter-Robot remote commands (LR3 + LR4)
LITTER_REMOTE_COMMANDS = [
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

# Feeder-Robot remote commands
FEEDER_REMOTE_COMMANDS = [
    CMD_GIVE_SNACK,
    CMD_NIGHT_LIGHT_ON,
    CMD_NIGHT_LIGHT_OFF,
    CMD_PANEL_LOCK_ON,
    CMD_PANEL_LOCK_OFF,
    CMD_GRAVITY_ON,
    CMD_GRAVITY_OFF,
]

# Display name <-> pylitterbot enum name maps
NIGHT_LIGHT_MODE_TO_ENUM = {"Off": "OFF", "On": "ON", "Auto": "AUTO"}
NIGHT_LIGHT_MODE_FROM_ENUM = {v: k for k, v in NIGHT_LIGHT_MODE_TO_ENUM.items()}

BRIGHTNESS_TO_ENUM = {"Low": "LOW", "Medium": "MEDIUM", "High": "HIGH"}
BRIGHTNESS_FROM_ENUM = {v: k for k, v in BRIGHTNESS_TO_ENUM.items()}
# BrightnessLevel enum values: LOW=25, MEDIUM=50, HIGH=100
BRIGHTNESS_VALUE_TO_NAME = {25: "Low", 50: "Medium", 100: "High"}

# Feeder meal insert size (cups) <-> display label
MEAL_INSERT_SIZE_LABELS = {0.25: "1/4 cup", 0.125: "1/8 cup"}
