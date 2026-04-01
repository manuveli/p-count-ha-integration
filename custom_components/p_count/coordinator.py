"""Data update coordinator for P-Count Parking."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PCountApiClient, PCountAuthError, PCountConnectionError, ParkingData
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

type PCountConfigEntry = ConfigEntry[PCountCoordinator]


class PCountCoordinator(DataUpdateCoordinator[ParkingData]):
    """Coordinator to fetch parking data from P-Count."""

    config_entry: PCountConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: PCountApiClient,
        config_entry: PCountConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> ParkingData:
        """Fetch data from API."""
        try:
            data = await self.client.async_get_occupation()
        except PCountAuthError as err:
            raise ConfigEntryAuthFailed(
                f"Authentication failed: {err}"
            ) from err
        except PCountConnectionError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        # Adjust polling interval if the server suggests a different one
        if data.polling_seconds and data.polling_seconds != self.update_interval.total_seconds():
            self.update_interval = timedelta(seconds=data.polling_seconds)
            _LOGGER.debug(
                "Adjusted polling interval to %s seconds", data.polling_seconds
            )

        return data
