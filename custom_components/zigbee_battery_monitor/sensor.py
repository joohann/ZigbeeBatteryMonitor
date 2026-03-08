"""Sensor platform for Zigbee Battery Monitor."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    BATTERY_LEVEL_CRITICAL,
    BATTERY_LEVEL_LOW,
    BATTERY_LEVEL_WARNING,
    BATTERY_LEVEL_OK,
    BATTERY_LEVEL_UNAVAILABLE,
)
from .coordinator import ZigbeeBatteryCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator: ZigbeeBatteryCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            ZiggeeBatterySummarySensor(
                coordinator,
                BATTERY_LEVEL_CRITICAL,
                "Kritieke Batterijen",
                "mdi:battery-alert",
                "#FF0000",
            ),
            ZiggeeBatterySummarySensor(
                coordinator,
                BATTERY_LEVEL_LOW,
                "Lage Batterijen",
                "mdi:battery-low",
                "#FF8C00",
            ),
            ZiggeeBatterySummarySensor(
                coordinator,
                BATTERY_LEVEL_WARNING,
                "Batterij Waarschuwingen",
                "mdi:battery-medium",
                "#FFD700",
            ),
            ZiggeeBatterySummarySensor(
                coordinator,
                BATTERY_LEVEL_OK,
                "Batterijen OK",
                "mdi:battery-high",
                "#00C853",
            ),
            ZiggeeBatterySummarySensor(
                coordinator,
                BATTERY_LEVEL_UNAVAILABLE,
                "Niet Beschikbaar",
                "mdi:battery-unknown",
                "#808080",
            ),
            ZigbeeBatteryTotalSensor(coordinator),
        ]
    )


class ZiggeeBatterySummarySensor(CoordinatorEntity, SensorEntity):
    """Sensor that counts devices in a specific battery level category."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "apparaten"

    def __init__(
        self,
        coordinator: ZigbeeBatteryCoordinator,
        level: str,
        name: str,
        icon: str,
        color: str,
    ) -> None:
        super().__init__(coordinator)
        self._level = level
        self._attr_name = f"Zigbee Batterij {name}"
        self._attr_unique_id = f"{DOMAIN}_{level}_count"
        self._attr_icon = icon
        self._color = color

    @property
    def native_value(self) -> int:
        """Return count of devices in this level."""
        if self.coordinator.data is None:
            return 0
        return len(self.coordinator.data.get(self._level, []))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return list of affected devices as attributes."""
        if self.coordinator.data is None:
            return {}
        devices = self.coordinator.data.get(self._level, [])
        return {
            "apparaten": [
                {
                    "naam": d["name"],
                    "entity_id": d["entity_id"],
                    "batterij": f"{d['battery_pct']}%"
                    if d["battery_pct"] is not None
                    else d["state"],
                }
                for d in devices
            ],
            "drempel_kritiek": self.coordinator.threshold_critical,
            "drempel_laag": self.coordinator.threshold_low,
            "drempel_waarschuwing": self.coordinator.threshold_warning,
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "zigbee_battery_monitor")},
            "name": "Zigbee Battery Monitor",
            "manufacturer": "Community",
            "model": "Battery Monitor",
        }


class ZigbeeBatteryTotalSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing total monitored devices."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "apparaten"
    _attr_name = "Zigbee Batterijen Totaal"
    _attr_unique_id = f"{DOMAIN}_total_count"
    _attr_icon = "mdi:battery-charging-wireless"

    @property
    def native_value(self) -> int:
        if self.coordinator.data is None:
            return 0
        return self.coordinator.data.get("total", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self.coordinator.data is None:
            return {}
        data = self.coordinator.data
        return {
            "kritiek": len(data.get(BATTERY_LEVEL_CRITICAL, [])),
            "laag": len(data.get(BATTERY_LEVEL_LOW, [])),
            "waarschuwing": len(data.get(BATTERY_LEVEL_WARNING, [])),
            "ok": len(data.get(BATTERY_LEVEL_OK, [])),
            "niet_beschikbaar": len(data.get(BATTERY_LEVEL_UNAVAILABLE, [])),
        }

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "zigbee_battery_monitor")},
            "name": "Zigbee Battery Monitor",
            "manufacturer": "Community",
            "model": "Battery Monitor",
        }
