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


def _get_signal_quality(data: dict) -> int | None:
    """Return cellular signal quality as a 0-100 percentage.

    modem-service publishes the ModemManager signal-quality percentage, using
    255 as its "unknown" sentinel; anything outside 0-100 is reported as unknown.
    """
    value = _get_connectivity_field(data, "signal_quality")
    try:
        quality = int(value)
    except (TypeError, ValueError):
        return None
    if not 0 <= quality <= 100:
        return None
    return quality


def _get_connectivity_status_field(data: dict, field: str) -> Any:
    """Extract a field from the scooter connectivity_status object."""
    if status := data.get("connectivity_status"):
        return status.get(field)
    return None


def _get_engine_status_field(data: dict, field: str) -> Any:
    """Extract a field from the scooter engine_status object."""
    if status := data.get("engine_status"):
        return status.get(field)
    return None


def _get_handlebar_field(data: dict, field: str) -> Any:
    """Extract a field from the scooter handlebar_status object."""
    if status := data.get("handlebar_status"):
        return status.get(field)
    return None


def _get_dashboard_field(data: dict, field: str) -> Any:
    """Extract a field from the scooter dashboard_status object."""
    if status := data.get("dashboard_status"):
        return status.get(field)
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
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:signal",
        value_fn=_get_signal_quality,
    ),
    # --- Range & identity ---
    SunshineSensorEntityDescription(
        key="estimated_range",
        name="Estimated Range",
        native_unit_of_measurement="km",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:map-marker-distance",
        value_fn=lambda d: d.get("estimated_range"),
    ),
    SunshineSensorEntityDescription(
        key="license_plate",
        name="License Plate",
        icon="mdi:car-brake-alert",
        value_fn=lambda d: d.get("license_plate"),
    ),
    SunshineSensorEntityDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:memory",
        value_fn=lambda d: d.get("radio_gaga_version"),
    ),
    SunshineSensorEntityDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("temperature"),
    ),
    # --- Connectivity status ---
    SunshineSensorEntityDescription(
        key="internet_status",
        name="Internet Status",
        icon="mdi:access-point-network",
        value_fn=lambda d: _get_connectivity_status_field(d, "internet_status"),
    ),
    SunshineSensorEntityDescription(
        key="cloud_status",
        name="Cloud Status",
        icon="mdi:cloud-outline",
        value_fn=lambda d: _get_connectivity_status_field(d, "cloud_status"),
    ),
    SunshineSensorEntityDescription(
        key="access_tech",
        name="Access Technology",
        icon="mdi:signal-cellular-outline",
        value_fn=lambda d: _get_connectivity_status_field(d, "access_tech"),
    ),
    # --- Engine status ---
    SunshineSensorEntityDescription(
        key="engine_state",
        name="Engine State",
        icon="mdi:engine-outline",
        value_fn=lambda d: _get_engine_status_field(d, "state"),
    ),
    SunshineSensorEntityDescription(
        key="kers_state",
        name="KERS State",
        icon="mdi:battery-charging",
        value_fn=lambda d: _get_engine_status_field(d, "kers_state"),
    ),
    SunshineSensorEntityDescription(
        key="throttle_state",
        name="Throttle State",
        icon="mdi:accelerator",
        value_fn=lambda d: _get_engine_status_field(d, "throttle_state"),
    ),
    # --- Handlebar & dashboard ---
    SunshineSensorEntityDescription(
        key="handlebar_position",
        name="Handlebar Position",
        icon="mdi:motorbike",
        value_fn=lambda d: _get_handlebar_field(d, "position"),
    ),
    SunshineSensorEntityDescription(
        key="dashboard_mode",
        name="Dashboard Mode",
        icon="mdi:gauge",
        value_fn=lambda d: _get_dashboard_field(d, "mode"),
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
