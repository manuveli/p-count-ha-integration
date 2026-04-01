"""Sensor platform for P-Count Parking."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import ParkingData, ParkingSection
from .const import DOMAIN
from homeassistant.config_entries import ConfigEntry

from .coordinator import PCountCoordinator


@dataclass(frozen=True, kw_only=True)
class PCountSectionSensorDescription(SensorEntityDescription):
    """Describes a P-Count section sensor."""

    value_fn: Callable[[ParkingSection], Any]


SECTION_SENSORS: tuple[PCountSectionSensorDescription, ...] = (
    PCountSectionSensorDescription(
        key="free_spots",
        translation_key="free_spots",
        native_unit_of_measurement="Plätze",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:car-parking-lights",
        value_fn=lambda section: section.free_spots,
    ),
    PCountSectionSensorDescription(
        key="occupied_spots",
        translation_key="occupied_spots",
        native_unit_of_measurement="Plätze",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:car",
        value_fn=lambda section: section.occupied_spots,
    ),
    PCountSectionSensorDescription(
        key="total_spots",
        translation_key="total_spots",
        native_unit_of_measurement="Plätze",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:parking",
        value_fn=lambda section: section.total_spots,
    ),
    PCountSectionSensorDescription(
        key="occupancy_percent",
        translation_key="occupancy_percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:chart-donut",
        value_fn=lambda section: section.occupancy_percent,
    ),
)


@dataclass(frozen=True, kw_only=True)
class PCountTotalSensorDescription(SensorEntityDescription):
    """Describes a P-Count total sensor."""

    value_fn: Callable[[ParkingData], Any]


TOTAL_SENSORS: tuple[PCountTotalSensorDescription, ...] = (
    PCountTotalSensorDescription(
        key="total_free",
        translation_key="total_free",
        native_unit_of_measurement="Plätze",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:car-parking-lights",
        value_fn=lambda data: data.total_free,
    ),
    PCountTotalSensorDescription(
        key="total_occupied",
        translation_key="total_occupied",
        native_unit_of_measurement="Plätze",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:car",
        value_fn=lambda data: data.total_occupied,
    ),
    PCountTotalSensorDescription(
        key="total_spots",
        translation_key="total_all_spots",
        native_unit_of_measurement="Plätze",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:parking",
        value_fn=lambda data: data.total_spots,
    ),
    PCountTotalSensorDescription(
        key="last_updated",
        translation_key="last_updated",
        icon="mdi:clock-outline",
        value_fn=lambda data: data.measured_at.isoformat(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up P-Count sensors from a config entry."""
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = []

    # Create total sensors
    for description in TOTAL_SENSORS:
        entities.append(
            PCountTotalSensor(coordinator, description, entry)
        )

    # Create per-section sensors
    if coordinator.data and coordinator.data.sections:
        for section in coordinator.data.sections:
            for description in SECTION_SENSORS:
                entities.append(
                    PCountSectionSensor(
                        coordinator, description, entry, section.short_name
                    )
                )

    async_add_entities(entities)


class PCountTotalSensor(CoordinatorEntity[PCountCoordinator], SensorEntity):
    """Sensor for total parking data across all sections."""

    _attr_has_entity_name = True
    entity_description: PCountTotalSensorDescription

    def __init__(
        self,
        coordinator: PCountCoordinator,
        description: PCountTotalSensorDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Steinberg Verkehrstechnik",
            "model": "P-Count",
            "entry_type": "service",
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)


class PCountSectionSensor(CoordinatorEntity[PCountCoordinator], SensorEntity):
    """Sensor for a specific parking section."""

    _attr_has_entity_name = True
    entity_description: PCountSectionSensorDescription

    def __init__(
        self,
        coordinator: PCountCoordinator,
        description: PCountSectionSensorDescription,
        entry: ConfigEntry,
        section_short_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._section_short_name = section_short_name
        self._attr_unique_id = (
            f"{entry.entry_id}_{section_short_name}_{description.key}"
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Steinberg Verkehrstechnik",
            "model": "P-Count",
            "entry_type": "service",
        }
        self._attr_name = f"{section_short_name} {description.key.replace('_', ' ').title()}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        for section in self.coordinator.data.sections:
            if section.short_name == self._section_short_name:
                return self.entity_description.value_fn(section)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}
        for section in self.coordinator.data.sections:
            if section.short_name == self._section_short_name:
                return {
                    "long_name": section.long_name,
                    "short_name": section.short_name,
                }
        return {}
