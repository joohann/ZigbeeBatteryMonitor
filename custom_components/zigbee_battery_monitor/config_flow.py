"""Config flow for Zigbee Battery Monitor."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    NAME,
    CONF_THRESHOLD_CRITICAL,
    CONF_THRESHOLD_LOW,
    CONF_THRESHOLD_WARNING,
    CONF_NOTIFY_SERVICES,
    CONF_NOTIFY_CRITICAL,
    CONF_NOTIFY_DAILY,
    CONF_NOTIFY_WEEKLY,
    CONF_NOTIFY_TIME_DAILY,
    CONF_NOTIFY_TIME_WEEKLY,
    CONF_NOTIFY_WEEKDAY,
    CONF_SCAN_INTERVAL,
    DEFAULT_THRESHOLD_CRITICAL,
    DEFAULT_THRESHOLD_LOW,
    DEFAULT_THRESHOLD_WARNING,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_NOTIFY_TIME_DAILY,
    DEFAULT_NOTIFY_TIME_WEEKLY,
    DEFAULT_NOTIFY_WEEKDAY,
    WEEKDAYS,
)

_LOGGER = logging.getLogger(__name__)


def _get_notify_services(hass: HomeAssistant) -> list[str]:
    """Dynamically fetch all available notify.* services from HA."""
    services = hass.services.async_services().get("notify", {})
    return sorted([
        f"notify.{service}"
        for service in services
        if service not in ("persistent_notification",)
    ])


def _build_schema(defaults: dict, notify_options: list[str]) -> vol.Schema:
    return vol.Schema({
        vol.Required(
            CONF_THRESHOLD_CRITICAL,
            default=defaults.get(CONF_THRESHOLD_CRITICAL, DEFAULT_THRESHOLD_CRITICAL),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=50, step=1, mode=selector.NumberSelectorMode.SLIDER)
        ),
        vol.Required(
            CONF_THRESHOLD_LOW,
            default=defaults.get(CONF_THRESHOLD_LOW, DEFAULT_THRESHOLD_LOW),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=50, step=1, mode=selector.NumberSelectorMode.SLIDER)
        ),
        vol.Required(
            CONF_THRESHOLD_WARNING,
            default=defaults.get(CONF_THRESHOLD_WARNING, DEFAULT_THRESHOLD_WARNING),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(min=1, max=80, step=1, mode=selector.NumberSelectorMode.SLIDER)
        ),
        vol.Optional(
            CONF_NOTIFY_SERVICES,
            default=defaults.get(CONF_NOTIFY_SERVICES, []),
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=notify_options,
                multiple=True,
                mode=selector.SelectSelectorMode.LIST,
            )
        ),
        vol.Required(
            CONF_NOTIFY_CRITICAL,
            default=defaults.get(CONF_NOTIFY_CRITICAL, True),
        ): selector.BooleanSelector(),
        vol.Required(
            CONF_NOTIFY_DAILY,
            default=defaults.get(CONF_NOTIFY_DAILY, True),
        ): selector.BooleanSelector(),
        vol.Required(
            CONF_NOTIFY_TIME_DAILY,
            default=defaults.get(CONF_NOTIFY_TIME_DAILY, DEFAULT_NOTIFY_TIME_DAILY),
        ): selector.TimeSelector(),
        vol.Required(
            CONF_NOTIFY_WEEKLY,
            default=defaults.get(CONF_NOTIFY_WEEKLY, True),
        ): selector.BooleanSelector(),
        vol.Required(
            CONF_NOTIFY_TIME_WEEKLY,
            default=defaults.get(CONF_NOTIFY_TIME_WEEKLY, DEFAULT_NOTIFY_TIME_WEEKLY),
        ): selector.TimeSelector(),
        vol.Required(
            CONF_NOTIFY_WEEKDAY,
            default=defaults.get(CONF_NOTIFY_WEEKDAY, DEFAULT_NOTIFY_WEEKDAY),
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=[
                    {"value": k, "label": v}
                    for k, v in WEEKDAYS.items()
                ],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
        vol.Required(
            CONF_SCAN_INTERVAL,
            default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(min=5, max=1440, step=5, mode=selector.NumberSelectorMode.BOX, unit_of_measurement="minuten")
        ),
    })


class ZigbeeBatteryMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zigbee Battery Monitor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}
        notify_options = _get_notify_services(self.hass)

        if user_input is not None:
            if not _validate_thresholds(user_input):
                errors["base"] = "invalid_thresholds"
            else:
                return self.async_create_entry(title=NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input or {}, notify_options),
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/joohann/ZigbeeBatteryMonitor"
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return ZigbeeBatteryMonitorOptionsFlow(config_entry)


class ZigbeeBatteryMonitorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        notify_options = _get_notify_services(self.hass)

        if user_input is not None:
            if not _validate_thresholds(user_input):
                errors["base"] = "invalid_thresholds"
            else:
                return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(current, notify_options),
            errors=errors,
        )


def _validate_thresholds(data: dict) -> bool:
    """Validate that critical < low < warning."""
    c = data.get(CONF_THRESHOLD_CRITICAL, DEFAULT_THRESHOLD_CRITICAL)
    l = data.get(CONF_THRESHOLD_LOW, DEFAULT_THRESHOLD_LOW)
    w = data.get(CONF_THRESHOLD_WARNING, DEFAULT_THRESHOLD_WARNING)
    return c < l < w
