"""Base entity for Sunshine Scooter integration."""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunshineDataUpdateCoordinator


class SunshineEntity(CoordinatorEntity[SunshineDataUpdateCoordinator]):
    """Base class for Sunshine entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SunshineDataUpdateCoordinator, scooter_id: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.scooter_id = scooter_id

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        scooter = self.coordinator.data.get(self.scooter_id, {})

        model_info = scooter.get("model")
        if isinstance(model_info, dict):
            model_name = model_info.get("full_name") or model_info.get("model_name") or "Unknown"
        elif isinstance(model_info, str):
            model_name = model_info or "Unknown"
        else:
            model_name = "Unknown"

        name = scooter.get("name") or f"Scooter {scooter.get('vin', self.scooter_id)}"

        info = {
            "identifiers": {(DOMAIN, self.scooter_id)},
            "name": name,
            "model": model_name,
            "manufacturer": "Sunshine",
        }

        if sw_version := scooter.get("radio_gaga_version"):
            info["sw_version"] = sw_version

        return info
