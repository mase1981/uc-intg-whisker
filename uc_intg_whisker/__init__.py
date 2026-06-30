"""
Whisker Litter-Robot integration for Unfolded Circle Remote.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import json
import logging
import os
from pathlib import Path

try:
    _driver_path = Path(__file__).parent.parent / "driver.json"
    with open(_driver_path, "r", encoding="utf-8") as f:
        __version__ = json.load(f).get("version", "0.0.0")
except (FileNotFoundError, json.JSONDecodeError):
    __version__ = "0.0.0"

__all__ = ["__version__"]


async def _migrate_configs(config_manager, log):
    """Populate config.robots for any account configured before robot metadata
    was persisted (e.g. upgrades from <=1.0.2). Runs before the driver registers
    entities so they are built from a complete config and survive reboots."""
    from uc_intg_whisker.device import discover_robot_metas

    for cfg in list(config_manager.all()):
        if getattr(cfg, "robots", None):
            continue
        if not getattr(cfg, "username", "") or not getattr(cfg, "password", ""):
            continue
        log.info("Migrating config %s: discovering robots", cfg.identifier)
        try:
            metas = await asyncio.wait_for(
                discover_robot_metas(cfg.username, cfg.password), timeout=45
            )
        except Exception as err:  # pylint: disable=broad-exception-caught
            log.warning(
                "Config migration for %s failed (will retry next start): %s",
                cfg.identifier,
                err,
            )
            continue
        if metas:
            cfg.robots = metas
            config_manager.update(cfg)
            log.info(
                "Migrated config %s: persisted %d robot(s)",
                cfg.identifier,
                len(metas),
            )


async def main():
    from ucapi import DeviceStates
    from ucapi_framework import BaseConfigManager, get_config_path

    from uc_intg_whisker.config import WhiskerConfig
    from uc_intg_whisker.driver import WhiskerDriver
    from uc_intg_whisker.setup_flow import WhiskerSetupFlow

    level = os.getenv("UC_LOG_LEVEL", "DEBUG").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.DEBUG),
        format="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
    )
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("websockets.server").setLevel(logging.CRITICAL)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("pylitterbot").setLevel(logging.INFO)

    _LOG = logging.getLogger(__name__)
    _LOG.info("Starting Whisker Litter-Robot Integration v%s", __version__)

    driver = WhiskerDriver()
    config_path = get_config_path(driver.api.config_dir_path or "")
    config_manager = BaseConfigManager(
        config_path,
        add_handler=driver.on_device_added,
        remove_handler=driver.on_device_removed,
        config_class=WhiskerConfig,
    )
    driver.config_manager = config_manager

    # Auto-migrate older configs (pre-robot-metadata) BEFORE the driver goes up,
    # so entities are registered from a complete config before the Remote
    # re-subscribes after a reboot/upgrade.
    await _migrate_configs(config_manager, _LOG)

    setup_handler = WhiskerSetupFlow.create_handler(driver)
    driver_path = os.path.join(os.path.dirname(__file__), "..", "driver.json")
    await driver.api.init(os.path.abspath(driver_path), setup_handler)
    await driver.register_all_device_instances(connect=False)

    device_count = len(list(config_manager.all()))
    await driver.api.set_device_state(
        DeviceStates.CONNECTED if device_count > 0 else DeviceStates.DISCONNECTED
    )
    _LOG.info(
        "Whisker Litter-Robot integration started - %d account(s) configured",
        device_count,
    )
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
