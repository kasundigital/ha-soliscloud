"""Sensor platform for SolisCloud."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ALL_SENSORS, DOMAIN, SolisSensorDescription
from .coordinator import SolisDataCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SolisCloud sensors."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator: SolisDataCoordinator = runtime["coordinator"]
    integration_name: str = runtime["name"]

    entities: list[SolisSensor] = []
    for serial, values in (coordinator.data or {}).items():
        for description in ALL_SENSORS:
            if description.key in values and values.get(description.key) is not None:
                entities.append(
                    SolisSensor(coordinator, serial, integration_name, description)
                )
    async_add_entities(entities)


class SolisSensor(CoordinatorEntity[SolisDataCoordinator], SensorEntity):
    """One backward-compatible Solis sensor."""

    _attr_has_entity_name = True
    _attr_entity_registry_enabled_default = True

    def __init__(
        self,
        coordinator: SolisDataCoordinator,
        serial: str,
        integration_name: str,
        description: SolisSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self._serial = serial
        self._description = description
        self._legacy_name = f"{integration_name} {description.name}"

        # This exactly preserves the unique-id formula used by hultenvp/solis-sensor.
        # Existing entity-registry entries therefore keep their entity IDs/history.
        self._attr_unique_id = f"{serial}{self._legacy_name}".replace(" ", "_")
        self._attr_name = self._legacy_name
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class

    @property
    def native_value(self) -> Any:
        """Return the current sensor value."""
        values = (self.coordinator.data or {}).get(self._serial, {})
        value = values.get(self._description.key)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return value
        return value

    @property
    def available(self) -> bool:
        """Keep entities available only when coordinator data is current."""
        values = (self.coordinator.data or {}).get(self._serial, {})
        return self.coordinator.last_update_success and self._description.key in values

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Preserve useful attributes from the previous integration."""
        return {
            "Inverter serial": self._serial,
            "API Name": "SolisCloud",
            "Last updated": self.coordinator.last_update_success_time,
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return the same device identity/name used by the previous integration."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._serial}_SolisCloud")},
            manufacturer="Solis",
            name=f"Solis_Inverter_{self._serial}",
        )
