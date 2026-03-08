"""Binary sensor platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SunshineDataUpdateCoordinator
from .entity import SunshineEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class SunshineBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Sunshine binary sensor entity."""

    is_on_fn: Callable[[dict], bool | None] | None = None


BINARY_SENSOR_TYPES: list[SunshineBinarySensorEntityDescription] = [
    SunshineBinarySensorEntityDescription(
        key="online",
        name="Online",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        is_on_fn=lambda d: d.get("online"),
    ),
    SunshineBinarySensorEntityDescription(
        key="alarm_triggered",
        name="Alarm Triggered",
        device_class=BinarySensorDeviceClass.SAFETY,
        icon="mdi:alarm-light",
        is_on_fn=lambda d: d.get("alarm_triggered"),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sunshine Scooter binary sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]

    entities: list[SunshineBinarySensor] = []

    for scooter_id in coordinator.data:
        for description in BINARY_SENSOR_TYPES:
            entities.append(
                SunshineBinarySensor(coordinator, scooter_id, description)
            )

    async_add_entities(entities)


class SunshineBinarySensor(SunshineEntity, BinarySensorEntity):
    """Representation of a Sunshine Scooter binary sensor."""

    entity_description: SunshineBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: SunshineDataUpdateCoordinator,
        scooter_id: str,
        description: SunshineBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, scooter_id)
        self.entity_description = description
        self._attr_unique_id = f"{scooter_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if scooter_data := self.coordinator.data.get(self.scooter_id):
            if self.entity_description.is_on_fn:
                return self.entity_description.is_on_fn(scooter_data)
        return None
