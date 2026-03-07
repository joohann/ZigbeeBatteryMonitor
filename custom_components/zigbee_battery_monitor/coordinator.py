"""DataUpdateCoordinator for Zigbee Battery Monitor."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    CONF_SCAN_INTERVAL,
    CONF_THRESHOLD_CRITICAL,
    CONF_THRESHOLD_LOW,
    CONF_THRESHOLD_WARNING,
    DEFAULT_THRESHOLD_CRITICAL,
    DEFAULT_THRESHOLD_LOW,
    DEFAULT_THRESHOLD_WARNING,
    BATTERY_LEVEL_CRITICAL,
    BATTERY_LEVEL_LOW,
    BATTERY_LEVEL_WARNING,
    BATTERY_LEVEL_OK,
    BATTERY_LEVEL_UNAVAILABLE,
)

_LOGGER = logging.getLogger(__name__)


class ZigbeeBatteryCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch and classify all battery entities."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.entry = entry
        scan_interval = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval),
        )

    @property
    def threshold_critical(self) -> int:
        return self.entry.options.get(
            CONF_THRESHOLD_CRITICAL,
            self.entry.data.get(CONF_THRESHOLD_CRITICAL, DEFAULT_THRESHOLD_CRITICAL),
        )

    @property
    def threshold_low(self) -> int:
        return self.entry.options.get(
            CONF_THRESHOLD_LOW,
            self.entry.data.get(CONF_THRESHOLD_LOW, DEFAULT_THRESHOLD_LOW),
        )

    @property
    def threshold_warning(self) -> int:
        return self.entry.options.get(
            CONF_THRESHOLD_WARNING,
            self.entry.data.get(CONF_THRESHOLD_WARNING, DEFAULT_THRESHOLD_WARNING),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch battery data from all battery entities in HA."""
        try:
            devices = []
            for state in self.hass.states.async_all():
                if state.attributes.get("device_class") != "battery":
                    continue

                raw = state.state
                if raw in ("unavailable", "unknown", None):
                    devices.append({
                        "entity_id": state.entity_id,
                        "name": state.attributes.get("friendly_name", state.entity_id),
                        "state": raw,
                        "level": BATTERY_LEVEL_UNAVAILABLE,
                        "battery_pct": None,
                        "unit": state.attributes.get("unit_of_measurement", "%"),
                        "device_info": state.attributes,
                    })
                    continue

                try:
                    pct = float(raw)
                except ValueError:
                    continue

                if pct < self.threshold_critical:
                    level = BATTERY_LEVEL_CRITICAL
                elif pct < self.threshold_low:
                    level = BATTERY_LEVEL_LOW
                elif pct < self.threshold_warning:
                    level = BATTERY_LEVEL_WARNING
                else:
                    level = BATTERY_LEVEL_OK

                devices.append({
                    "entity_id": state.entity_id,
                    "name": state.attributes.get("friendly_name", state.entity_id),
                    "state": raw,
                    "level": level,
                    "battery_pct": pct,
                    "unit": state.attributes.get("unit_of_measurement", "%"),
                    "device_info": state.attributes,
                })

            devices.sort(key=lambda d: (d["battery_pct"] is None, d["battery_pct"] or 999))

            summary = {
                BATTERY_LEVEL_CRITICAL: [d for d in devices if d["level"] == BATTERY_LEVEL_CRITICAL],
                BATTERY_LEVEL_LOW: [d for d in devices if d["level"] == BATTERY_LEVEL_LOW],
                BATTERY_LEVEL_WARNING: [d for d in devices if d["level"] == BATTERY_LEVEL_WARNING],
                BATTERY_LEVEL_OK: [d for d in devices if d["level"] == BATTERY_LEVEL_OK],
                BATTERY_LEVEL_UNAVAILABLE: [d for d in devices if d["level"] == BATTERY_LEVEL_UNAVAILABLE],
                "all": devices,
                "total": len(devices),
            }

            return summary

        except Exception as err:
            raise UpdateFailed(f"Fout bij ophalen batterijdata: {err}") from err
