"""Button platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SunshineDataUpdateCoordinator
from .entity import SunshineEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class SunshineButtonEntityDescription(ButtonEntityDescription):
    """Describes Sunshine button entity."""

    press_fn: Callable[[Any, str], Any] | None = None


BUTTON_TYPES: list[SunshineButtonEntityDescription] = [
    SunshineButtonEntityDescription(
        key="honk",
        name="Honk",
        icon="mdi:bullhorn",
        press_fn=lambda api, sid: api.honk(sid),
    ),
    SunshineButtonEntityDescription(
        key="locate",
        name="Locate",
        icon="mdi:map-marker",
        press_fn=lambda api, sid: api.locate(sid),
    ),
    SunshineButtonEntityDescription(
        key="ping",
        name="Ping",
        icon="mdi:access-point-network",
        press_fn=lambda api, sid: api.ping(sid),
    ),
    SunshineButtonEntityDescription(
        key="open_seatbox",
        name="Open Seatbox",
        icon="mdi:treasure-chest",
        press_fn=lambda api, sid: api.open_seatbox(sid),
    ),
    SunshineButtonEntityDescription(
        key="get_state",
        name="Request State",
        icon="mdi:chart-line",
        press_fn=lambda api, sid: api.get_state(sid),
    ),
    SunshineButtonEntityDescription(
        key="alarm_5s",
        name="Alarm (5s)",
        icon="mdi:alarm-light",
        press_fn=lambda api, sid: api.trigger_alarm(sid, "5s"),
    ),
    SunshineButtonEntityDescription(
        key="alarm_arm",
        name="Arm Alarm",
        icon="mdi:shield-lock",
        press_fn=lambda api, sid: api.alarm_arm(sid),
    ),
    SunshineButtonEntityDescription(
        key="alarm_disarm",
        name="Disarm Alarm",
        icon="mdi:shield-off",
        press_fn=lambda api, sid: api.alarm_disarm(sid),
    ),
    SunshineButtonEntityDescription(
        key="alarm_stop",
        name="Stop Alarm",
        icon="mdi:alarm-off",
        press_fn=lambda api, sid: api.alarm_stop(sid),
    ),
    SunshineButtonEntityDescription(
        key="hibernate",
        name="Hibernate",
        icon="mdi:sleep",
        press_fn=lambda api, sid: api.hibernate(sid),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sunshine Scooter buttons."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]

    entities: list[SunshineButton] = []

    for scooter_id in coordinator.data:
        for description in BUTTON_TYPES:
            entities.append(
                SunshineButton(api, coordinator, scooter_id, description)
            )

    async_add_entities(entities)


class SunshineButton(SunshineEntity, ButtonEntity):
    """Representation of a Sunshine Scooter button."""

    entity_description: SunshineButtonEntityDescription

    def __init__(
        self,
        api,
        coordinator: SunshineDataUpdateCoordinator,
        scooter_id: str,
        description: SunshineButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, scooter_id)
        self.api = api
        self.entity_description = description
        self._attr_unique_id = f"{scooter_id}_{description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            if self.entity_description.press_fn:
                await self.entity_description.press_fn(self.api, self.scooter_id)
                await self.coordinator.async_request_refresh()
                self.coordinator.async_request_delayed_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to press button %s for scooter %s: %s",
                self.entity_description.key,
                self.scooter_id,
                err
            )
