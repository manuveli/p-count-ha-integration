"""The P-Count Parking integration."""

from __future__ import annotations

import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import PCountApiClient
from .const import CONF_ACCESS_CODE, CONF_SYSTEM_ID
from .coordinator import PCountConfigEntry, PCountCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: PCountConfigEntry) -> bool:
    """Set up P-Count Parking from a config entry."""
    session = async_create_clientsession(hass)
    client = PCountApiClient(
        system_id=entry.data[CONF_SYSTEM_ID],
        access_code=entry.data[CONF_ACCESS_CODE],
        session=session,
    )

    coordinator = PCountCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: PCountConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
