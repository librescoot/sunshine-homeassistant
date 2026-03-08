"""Sensor platform for Sunshine Scooter integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SunshineDataUpdateCoordinator
from .entity import SunshineEntity

_LOGGER = logging.getLogger(__name__)


def _get_battery_field(data: dict, battery_key: str, field: str) -> Any:
    """Extract a field from a battery object."""
    if batteries := data.get("batteries"):
        if battery := batteries.get(battery_key):
            return battery.get(field)
    return None


def _get_odometer_km(data: dict) -> float | None:
    """Convert odometer from meters to km."""
    value = data.get("odometer")
    if value is None:
        return None
    try:
        return round(float(value) / 1000, 1)
    except (ValueError, TypeError):
        return None


def _get_engine_field(data: dict, field: str) -> Any:
    """Extract a field from the telemetry engine object."""
    if telemetry := data.get("telemetry"):
        if engine := telemetry.get("engine"):
            return engine.get(field)
    return None


def _get_connectivity_field(data: dict, field: str) -> Any:
    """Extract a field from the connectivity telemetry object."""
    if telemetry := data.get("telemetry"):
        if connectivity := telemetry.get("connectivity"):
            return connectivity.get(field)
    return None


@dataclass(frozen=True, kw_only=True)
class SunshineSensorEntityDescription(SensorEntityDescription):
    """Describes a Sunshine sensor entity."""

    value_fn: Callable[[dict], Any] | None = None


SENSOR_TYPES: list[SunshineSensorEntityDescription] = [
    # --- Core ---
    SunshineSensorEntityDescription(
        key="battery_level",
        name="Battery Level",
        native_unit_of_measurement="%",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "battery0", "level"),
    ),
    SunshineSensorEntityDescription(
        key="speed",
        name="Speed",
        native_unit_of_measurement="km/h",
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda d: d.get("speed"),
    ),
    SunshineSensorEntityDescription(
        key="odometer",
        name="Odometer",
        native_unit_of_measurement="km",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        value_fn=_get_odometer_km,
    ),
    SunshineSensorEntityDescription(
        key="state",
        name="Status",
        icon="mdi:information-outline",
        value_fn=lambda d: d.get("state"),
    ),
    # --- Alarm ---
    SunshineSensorEntityDescription(
        key="alarm_state",
        name="Alarm State",
        icon="mdi:shield-alert",
        value_fn=lambda d: d.get("alarm_state_humanized") or d.get("alarm_state"),
    ),
    # --- Vehicle state ---
    SunshineSensorEntityDescription(
        key="kickstand",
        name="Kickstand",
        icon="mdi:scooter",
        value_fn=lambda d: d.get("kickstand"),
    ),
    SunshineSensorEntityDescription(
        key="seatbox",
        name="Seatbox",
        icon="mdi:treasure-chest",
        value_fn=lambda d: d.get("seatbox"),
    ),
    SunshineSensorEntityDescription(
        key="last_seen_at",
        name="Last Seen",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-outline",
        value_fn=lambda d: datetime.fromisoformat(d["last_seen_at"]) if d.get("last_seen_at") else None,
    ),
    # --- Battery 0 details ---
    SunshineSensorEntityDescription(
        key="battery0_voltage",
        name="Battery Voltage",
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "battery0", "voltage"),
    ),
    SunshineSensorEntityDescription(
        key="battery0_soh",
        name="Battery Health",
        native_unit_of_measurement="%",
        icon="mdi:battery-heart-variant",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "battery0", "soh"),
    ),
    SunshineSensorEntityDescription(
        key="battery0_cycle_count",
        name="Battery Cycle Count",
        icon="mdi:battery-sync",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: _get_battery_field(d, "battery0", "cycle_count"),
    ),
    SunshineSensorEntityDescription(
        key="battery0_state",
        name="Battery State",
        icon="mdi:battery-unknown",
        value_fn=lambda d: _get_battery_field(d, "battery0", "state"),
    ),
    # --- Battery 1 ---
    SunshineSensorEntityDescription(
        key="battery1_level",
        name="Battery 1 Level",
        native_unit_of_measurement="%",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "battery1", "level"),
    ),
    SunshineSensorEntityDescription(
        key="battery1_voltage",
        name="Battery 1 Voltage",
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "battery1", "voltage"),
    ),
    SunshineSensorEntityDescription(
        key="battery1_soh",
        name="Battery 1 Health",
        native_unit_of_measurement="%",
        icon="mdi:battery-heart-variant",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "battery1", "soh"),
    ),
    SunshineSensorEntityDescription(
        key="battery1_cycle_count",
        name="Battery 1 Cycle Count",
        icon="mdi:battery-sync",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: _get_battery_field(d, "battery1", "cycle_count"),
    ),
    SunshineSensorEntityDescription(
        key="battery1_state",
        name="Battery 1 State",
        icon="mdi:battery-unknown",
        value_fn=lambda d: _get_battery_field(d, "battery1", "state"),
    ),
    # --- Aux battery ---
    SunshineSensorEntityDescription(
        key="aux_battery_level",
        name="Aux Battery Level",
        native_unit_of_measurement="%",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "aux", "level"),
    ),
    SunshineSensorEntityDescription(
        key="aux_battery_voltage",
        name="Aux Battery Voltage",
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "aux", "voltage"),
    ),
    # --- CBB battery ---
    SunshineSensorEntityDescription(
        key="cbb_battery_level",
        name="CBB Battery Level",
        native_unit_of_measurement="%",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "cbb", "level"),
    ),
    SunshineSensorEntityDescription(
        key="cbb_battery_soh",
        name="CBB Battery Health",
        native_unit_of_measurement="%",
        icon="mdi:battery-heart-variant",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_battery_field(d, "cbb", "soh"),
    ),
    SunshineSensorEntityDescription(
        key="cbb_battery_cycle_count",
        name="CBB Battery Cycle Count",
        icon="mdi:battery-sync",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: _get_battery_field(d, "cbb", "cycle_count"),
    ),
    # --- Engine ---
    SunshineSensorEntityDescription(
        key="engine_temperature",
        name="Engine Temperature",
        native_unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_engine_field(d, "temperature"),
    ),
    SunshineSensorEntityDescription(
        key="engine_rpm",
        name="Motor RPM",
        icon="mdi:engine",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: _get_engine_field(d, "motor_rpm"),
    ),
    # --- Connectivity ---
    SunshineSensorEntityDescription(
        key="signal_quality",
        name="Signal Quality",
        icon="mdi:signal",
        value_fn=lambda d: _get_connectivity_field(d, "signal_quality"),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sunshine Scooter sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]

    entities: list[SunshineSensor] = []

    for scooter_id in coordinator.data:
        for description in SENSOR_TYPES:
            entities.append(
                SunshineSensor(coordinator, scooter_id, description)
            )

    async_add_entities(entities)


class SunshineSensor(SunshineEntity, SensorEntity):
    """Representation of a Sunshine Scooter sensor."""

    entity_description: SunshineSensorEntityDescription

    def __init__(
        self,
        coordinator: SunshineDataUpdateCoordinator,
        scooter_id: str,
        description: SunshineSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, scooter_id)
        self.entity_description = description
        self._attr_unique_id = f"{scooter_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if scooter_data := self.coordinator.data.get(self.scooter_id):
            if self.entity_description.value_fn:
                return self.entity_description.value_fn(scooter_data)
            return scooter_data.get(self.entity_description.key)
        return None
