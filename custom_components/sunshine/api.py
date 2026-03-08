"""API client for Sunshine Scooter."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import DEFAULT_BASE_URL

_LOGGER = logging.getLogger(__name__)


class SunshineAPI:
    """Sunshine API client."""

    def __init__(self, token: str, base_url: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.token = token
        self.base_url = base_url.rstrip('/')
        self._session = session
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def test_authentication(self) -> bool:
        """Test if the authentication is valid."""
        try:
            await self.get_scooters()
            return True
        except Exception as err:
            _LOGGER.error("Authentication test failed: %s", err)
            raise

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any] | None:
        """Make a request to the API."""
        url = f"{self.base_url}/api/v1{endpoint}"

        async with self._session.request(method, url, headers=self._headers, **kwargs) as response:
            response.raise_for_status()
            if response.status == 204:
                return None
            return await response.json()

    # Scooter list & details

    async def get_scooters(self) -> list[dict[str, Any]]:
        """Get list of all scooters."""
        return await self._request("GET", "/scooters")

    async def get_scooter(self, scooter_id: str) -> dict[str, Any]:
        """Get details of a specific scooter."""
        return await self._request("GET", f"/scooters/{scooter_id}")

    # Control commands

    async def unlock(self, scooter_id: str) -> dict[str, Any]:
        """Unlock a scooter."""
        return await self._request("POST", f"/scooters/{scooter_id}/unlock")

    async def lock(self, scooter_id: str) -> dict[str, Any]:
        """Lock a scooter."""
        return await self._request("POST", f"/scooters/{scooter_id}/lock")

    async def honk(self, scooter_id: str) -> dict[str, Any]:
        """Activate horn/honk sound."""
        return await self._request("POST", f"/scooters/{scooter_id}/honk")

    async def trigger_alarm(self, scooter_id: str, duration: str = "5s") -> dict[str, Any]:
        """Trigger alarm for specified duration."""
        return await self._request(
            "POST",
            f"/scooters/{scooter_id}/alarm",
            json={"duration": duration}
        )

    async def alarm_arm(self, scooter_id: str) -> dict[str, Any]:
        """Arm the alarm system."""
        return await self._request("POST", f"/scooters/{scooter_id}/alarm_arm")

    async def alarm_disarm(self, scooter_id: str) -> dict[str, Any]:
        """Disarm the alarm system."""
        return await self._request("POST", f"/scooters/{scooter_id}/alarm_disarm")

    async def alarm_stop(self, scooter_id: str) -> dict[str, Any]:
        """Stop an active alarm."""
        return await self._request("POST", f"/scooters/{scooter_id}/alarm_stop")

    async def play_sound(self, scooter_id: str, sound: str) -> dict[str, Any]:
        """Play different sound types."""
        return await self._request(
            "POST",
            f"/scooters/{scooter_id}/play_sound",
            json={"sound": sound}
        )

    async def blinkers(self, scooter_id: str, state: str) -> dict[str, Any]:
        """Control turn signal blinkers."""
        return await self._request(
            "POST",
            f"/scooters/{scooter_id}/blinkers",
            json={"state": state}
        )

    async def locate(self, scooter_id: str) -> dict[str, Any]:
        """Trigger location/find feature."""
        return await self._request("POST", f"/scooters/{scooter_id}/locate")

    async def ping(self, scooter_id: str) -> dict[str, Any]:
        """Ping scooter for connectivity check."""
        return await self._request("POST", f"/scooters/{scooter_id}/ping")

    async def get_state(self, scooter_id: str) -> dict[str, Any]:
        """Request fresh telemetry/state from scooter."""
        return await self._request("POST", f"/scooters/{scooter_id}/get_state")

    async def open_seatbox(self, scooter_id: str) -> dict[str, Any]:
        """Open the seat box/storage compartment."""
        return await self._request("POST", f"/scooters/{scooter_id}/open_seatbox")

    async def hibernate(self, scooter_id: str) -> dict[str, Any]:
        """Put scooter into hibernation mode."""
        return await self._request("POST", f"/scooters/{scooter_id}/hibernate")

    # Trips

    async def get_trips(self, scooter_id: str, limit: int = 0, offset: int = 0) -> list[dict[str, Any]]:
        """Get list of trips for a scooter."""
        path = f"/scooters/{scooter_id}/trips"
        params = []
        if limit > 0:
            params.append(f"limit={limit}")
        if offset > 0:
            params.append(f"offset={offset}")
        if params:
            path += "?" + "&".join(params)
        return await self._request("GET", path)

    async def get_trip(self, scooter_id: str, trip_id: int) -> dict[str, Any]:
        """Get details of a specific trip."""
        return await self._request("GET", f"/scooters/{scooter_id}/trips/{trip_id}")

    # Navigation / Destination

    async def get_destination(self, scooter_id: str) -> dict[str, Any] | None:
        """Get the current navigation destination."""
        return await self._request("GET", f"/scooters/{scooter_id}/destination")

    async def set_destination(self, scooter_id: str, latitude: float, longitude: float, address: str = "") -> dict[str, Any]:
        """Set a navigation destination."""
        body = {"latitude": latitude, "longitude": longitude}
        if address:
            body["address"] = address
        return await self._request("PUT", f"/scooters/{scooter_id}/destination", json=body)

    async def clear_destination(self, scooter_id: str) -> None:
        """Clear the current navigation destination."""
        await self._request("DELETE", f"/scooters/{scooter_id}/destination")
