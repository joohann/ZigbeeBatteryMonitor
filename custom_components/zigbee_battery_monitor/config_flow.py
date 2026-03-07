"""Config flow for Zigbee Battery Monitor."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
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


def _build_schema(defaults: dict) -> vol.Schema:
    return vol.Schema({
        vol.Required(
            CONF_THRESHOLD_CRITICAL,
            default=defaults.get(CONF_THRESHOLD_CRITICAL, DEFAULT_THRESHOLD_CRITICAL),
        ): vol.All(int, vol.Range(min=1, max=50)),
        vol.Required(
            CONF_THRESHOLD_LOW,
            default=defaults.get(CONF_THRESHOLD_LOW, DEFAULT_THRESHOLD_LOW),
        ): vol.All(int, vol.Range(min=1, max=50)),
        vol.Required(
            CONF_THRESHOLD_WARNING,
            default=defaults.get(CONF_THRESHOLD_WARNING, DEFAULT_THRESHOLD_WARNING),
        ): vol.All(int, vol.Range(min=1, max=80)),
        vol.Optional(
            CONF_NOTIFY_SERVICES,
            default=defaults.get(CONF_NOTIFY_SERVICES, ""),
        ): str,
        vol.Required(
            CONF_NOTIFY_CRITICAL,
            default=defaults.get(CONF_NOTIFY_CRITICAL, True),
        ): bool,
        vol.Required(
            CONF_NOTIFY_DAILY,
            default=defaults.get(CONF_NOTIFY_DAILY, True),
        ): bool,
        vol.Required(
            CONF_NOTIFY_TIME_DAILY,
            default=defaults.get(CONF_NOTIFY_TIME_DAILY, DEFAULT_NOTIFY_TIME_DAILY),
        ): str,
        vol.Required(
            CONF_NOTIFY_WEEKLY,
            default=defaults.get(CONF_NOTIFY_WEEKLY, True),
        ): bool,
        vol.Required(
            CONF_NOTIFY_TIME_WEEKLY,
            default=defaults.get(CONF_NOTIFY_TIME_WEEKLY, DEFAULT_NOTIFY_TIME_WEEKLY),
        ): str,
        vol.Required(
            CONF_NOTIFY_WEEKDAY,
            default=defaults.get(CONF_NOTIFY_WEEKDAY, DEFAULT_NOTIFY_WEEKDAY),
        ): vol.In(list(WEEKDAYS.keys())),
        vol.Required(
            CONF_SCAN_INTERVAL,
            default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ): vol.All(int, vol.Range(min=5, max=1440)),
    })


class ZigbeeBatteryMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zigbee Battery Monitor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Only allow one instance
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}

        if user_input is not None:
            if not _validate_thresholds(user_input):
                errors["base"] = "invalid_thresholds"
            else:
                return self.async_create_entry(title=NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input or {}),
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/jouw-gebruikersnaam/zigbee-battery-monitor"
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

        if user_input is not None:
            if not _validate_thresholds(user_input):
                errors["base"] = "invalid_thresholds"
            else:
                return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(current),
            errors=errors,
        )


def _validate_thresholds(data: dict) -> bool:
    """Validate that critical < low < warning."""
    c = data.get(CONF_THRESHOLD_CRITICAL, DEFAULT_THRESHOLD_CRITICAL)
    l = data.get(CONF_THRESHOLD_LOW, DEFAULT_THRESHOLD_LOW)
    w = data.get(CONF_THRESHOLD_WARNING, DEFAULT_THRESHOLD_WARNING)
    return c < l < w
