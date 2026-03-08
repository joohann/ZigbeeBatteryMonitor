"""Notification handler for Zigbee Battery Monitor."""
from __future__ import annotations

import logging
from datetime import datetime, time
from typing import Any

from homeassistant.core import HomeAssistant

from .const import (
    CONF_NOTIFY_SERVICES,
    CONF_NOTIFY_CRITICAL,
    CONF_NOTIFY_DAILY,
    CONF_NOTIFY_WEEKLY,
    CONF_NOTIFY_WEEKDAY,
    BATTERY_LEVEL_CRITICAL,
    BATTERY_LEVEL_LOW,
    BATTERY_LEVEL_WARNING,
)
from .coordinator import ZigbeeBatteryCoordinator

_LOGGER = logging.getLogger(__name__)


class ZiggeeBatteryNotifier:
    """Handles all notifications for the battery monitor."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: ZigbeeBatteryCoordinator,
        config: dict[str, Any],
    ) -> None:
        self.hass = hass
        self.coordinator = coordinator
        self.config = config
        self._unsub_listeners: list[Any] = []
        self._last_critical_notified: set[str] = set()

    def get_notify_services(self) -> list[str]:
        """Return notify services list (stored as list via multi-select selector)."""
        raw = self.config.get(CONF_NOTIFY_SERVICES, [])
        if isinstance(raw, list):
            return [s for s in raw if s]
        # Fallback: legacy comma-separated string
        return [s.strip() for s in raw.split(",") if s.strip()]

    async def async_send(self, title: str, message: str, tag: str, color: str = "#3498db") -> None:
        """Send notification to all configured services."""
        services = self.get_notify_services()
        if not services:
            _LOGGER.warning("Geen notify services geconfigureerd")
            return

        for service in services:
            try:
                domain, svc = service.split(".", 1)
                await self.hass.services.async_call(
                    domain,
                    svc,
                    {
                        "title": title,
                        "message": message,
                        "data": {
                            "color": color,
                            "tag": tag,
                        },
                    },
                )
            except Exception as err:
                _LOGGER.error("Fout bij versturen notificatie naar %s: %s", service, err)

    async def async_check_critical(self) -> None:
        """Send immediate notification for newly critical devices."""
        if not self.config.get(CONF_NOTIFY_CRITICAL, True):
            return
        if not self.coordinator.data:
            return

        critical_devices = self.coordinator.data.get(BATTERY_LEVEL_CRITICAL, [])
        newly_critical = [
            d for d in critical_devices
            if d["entity_id"] not in self._last_critical_notified
        ]

        if not newly_critical:
            return

        lines = "\n".join(
            f"• {d['name']}: {d['battery_pct']}%" for d in newly_critical
        )
        await self.async_send(
            title="🔴 Kritieke batterij!",
            message=f"{len(newly_critical)} apparaat/apparaten heeft een kritiek lage batterij:\n{lines}",
            tag="zigbee_critical_battery",
            color="#FF0000",
        )
        self._last_critical_notified = {d["entity_id"] for d in critical_devices}

    async def async_send_daily_report(self, _now=None) -> None:
        """Send daily report for low batteries."""
        if not self.config.get(CONF_NOTIFY_DAILY, True):
            return
        if not self.coordinator.data:
            return

        low = self.coordinator.data.get(BATTERY_LEVEL_LOW, [])
        critical = self.coordinator.data.get(BATTERY_LEVEL_CRITICAL, [])
        all_low = critical + low

        if not all_low:
            return

        lines = "\n".join(f"• {d['name']}: {d['battery_pct']}%" for d in all_low)
        await self.async_send(
            title="🟠 Dagelijks batterij rapport",
            message=f"{len(all_low)} apparaat/apparaten heeft lage batterij:\n{lines}",
            tag="zigbee_daily_battery",
            color="#FF8C00",
        )

    async def async_send_weekly_report(self, _now=None) -> None:
        """Send weekly report for all devices below warning threshold."""
        if not self.config.get(CONF_NOTIFY_WEEKLY, True):
            return
        if not self.coordinator.data:
            return

        now = datetime.now()
        weekday = self.config.get(CONF_NOTIFY_WEEKDAY, "mon")
        weekday_map = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
        if now.weekday() != weekday_map.get(weekday, 0):
            return

        critical = self.coordinator.data.get(BATTERY_LEVEL_CRITICAL, [])
        low = self.coordinator.data.get(BATTERY_LEVEL_LOW, [])
        warning = self.coordinator.data.get(BATTERY_LEVEL_WARNING, [])
        all_warn = critical + low + warning

        if not all_warn:
            await self.async_send(
                title="✅ Wekelijks batterij rapport",
                message=f"Alle {self.coordinator.data.get('total', 0)} Zigbee apparaten hebben voldoende batterij.",
                tag="zigbee_weekly_battery",
                color="#00C853",
            )
            return

        lines = "\n".join(f"• {d['name']}: {d['battery_pct']}%" for d in all_warn)
        await self.async_send(
            title="🟡 Wekelijks batterij rapport",
            message=f"{len(all_warn)} apparaat/apparaten vereist aandacht:\n{lines}",
            tag="zigbee_weekly_battery",
            color="#FFD700",
        )
