"""
Whisker Litter-Robot setup flow for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from __future__ import annotations

import logging
import ssl
from typing import Any

import aiohttp
import certifi
from pylitterbot import Account, FeederRobot, LitterRobot3, LitterRobot4
from ucapi import RequestUserInput
from ucapi_framework import BaseSetupFlow

from uc_intg_whisker.config import WhiskerConfig

_LOG = logging.getLogger(__name__)


class WhiskerSetupFlow(BaseSetupFlow[WhiskerConfig]):
    """Single-screen email/password setup for the Whisker cloud account."""

    def get_manual_entry_form(self) -> RequestUserInput:
        return RequestUserInput(
            {"en": "Whisker Account"},
            [
                {
                    "id": "info",
                    "label": {"en": "Information"},
                    "field": {
                        "label": {
                            "value": {
                                "en": "Enter the email and password you use for the "
                                "Whisker mobile app. Every Litter-Robot on the account "
                                "will be added automatically."
                            }
                        }
                    },
                },
                {
                    "id": "username",
                    "label": {"en": "Email"},
                    "field": {"text": {"value": ""}},
                },
                {
                    "id": "password",
                    "label": {"en": "Password"},
                    "field": {"password": {"value": ""}},
                },
            ],
        )

    async def query_device(
        self, input_values: dict[str, Any]
    ) -> WhiskerConfig:
        username = input_values.get("username", "").strip()
        password = input_values.get("password", "")

        if not username or not password:
            raise ValueError("Email and password are required")

        _LOG.info("Validating Whisker account for %s", username)

        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_ctx)
        session = aiohttp.ClientSession(connector=connector)
        account = Account(websession=session)

        try:
            try:
                await account.connect(
                    username=username, password=password, load_robots=True
                )
            except Exception as err:  # pylint: disable=broad-exception-caught
                _LOG.error("Whisker login failed: %s", err)
                raise ValueError(
                    "Could not sign in to Whisker. Check the email and password."
                ) from err

            robots = [
                r
                for r in account.robots
                if isinstance(r, (LitterRobot3, LitterRobot4, FeederRobot))
            ]
            if not robots:
                raise ValueError(
                    "No Whisker devices were found on this account."
                )

            user_id = getattr(account, "user_id", "") or username
            identifier = f"whisker_{str(user_id).replace('.', '_').replace('@', '_')}"
            name = (
                robots[0].name
                if len(robots) == 1 and robots[0].name
                else "Whisker Litter-Robot"
            )

            _LOG.info("Whisker account validated - %d robot(s)", len(robots))
            return WhiskerConfig(
                identifier=identifier,
                name=name,
                username=username,
                password=password,
            )
        finally:
            try:
                await account.disconnect()
            except Exception:  # pylint: disable=broad-exception-caught
                pass
            if not session.closed:
                await session.close()
