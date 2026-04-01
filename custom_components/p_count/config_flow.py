"""Config flow for P-Count Parking integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import PCountApiClient, PCountAuthError, PCountConnectionError
from .const import CONF_ACCESS_CODE, CONF_SYSTEM_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SYSTEM_ID): str,
        vol.Required(CONF_ACCESS_CODE): str,
    }
)


class PCountConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for P-Count Parking."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            system_id = user_input[CONF_SYSTEM_ID]
            access_code = user_input[CONF_ACCESS_CODE]

            # Prevent duplicate entries for the same system
            await self.async_set_unique_id(system_id)
            self._abort_if_unique_id_configured()

            # Validate credentials by fetching car park info
            session = async_create_clientsession(self.hass)
            client = PCountApiClient(system_id, access_code, session)

            try:
                info = await client.async_get_carpark_info()
            except PCountAuthError:
                errors["base"] = "invalid_auth"
            except PCountConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=info.title,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauthentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle reauthentication confirmation."""
        errors: dict[str, str] = {}

        if user_input is not None:
            reauth_entry = self._get_reauth_entry()
            system_id = reauth_entry.data[CONF_SYSTEM_ID]
            access_code = user_input[CONF_ACCESS_CODE]

            session = async_create_clientsession(self.hass)
            client = PCountApiClient(system_id, access_code, session)

            try:
                await client.async_get_carpark_info()
            except PCountAuthError:
                errors["base"] = "invalid_auth"
            except PCountConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during reauth")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data_updates={CONF_ACCESS_CODE: access_code},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {vol.Required(CONF_ACCESS_CODE): str}
            ),
            errors=errors,
        )
