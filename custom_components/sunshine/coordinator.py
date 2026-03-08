"""Data update coordinator for Sunshine Scooter integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from async_timeout import timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SunshineAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class SunshineDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Class to manage fetching Sunshine data from the API."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        api: SunshineAPI,
    ) -> None:
        """Initialize the data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api
        self._delayed_refresh_unsub: CALLBACK_TYPE | None = None

    @callback
    def async_request_delayed_refresh(self, delay: float = 10.0) -> None:
        """Schedule a data refresh after a delay to catch state changes."""
        if self._delayed_refresh_unsub:
            self._delayed_refresh_unsub()

        @callback
        def _async_refresh(_now) -> None:
            self._delayed_refresh_unsub = None
            self.hass.async_create_task(self.async_request_refresh())

        self._delayed_refresh_unsub = async_call_later(self.hass, delay, _async_refresh)

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Update data via API."""
        try:
            async with timeout(30):
                scooters_list = await self.api.get_scooters()
                if not scooters_list:
                    return {}

                # Fetch detailed data for each scooter
                tasks = [self.api.get_scooter(scooter["id"]) for scooter in scooters_list]
                detailed_scooters = await asyncio.gather(*tasks)

                return {
                    scooter["id"]: scooter
                    for scooter in detailed_scooters
                    if "id" in scooter
                }
        except TimeoutError as err:
            raise UpdateFailed(f"Timeout fetching scooter data") from err
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch scooter data: {err}") from err