"""Constants for Zigbee Battery Monitor."""

DOMAIN = "zigbee_battery_monitor"
NAME = "Zigbee Battery Monitor"

# Config keys
CONF_THRESHOLD_CRITICAL = "threshold_critical"
CONF_THRESHOLD_LOW = "threshold_low"
CONF_THRESHOLD_WARNING = "threshold_warning"
CONF_NOTIFY_SERVICES = "notify_services"
CONF_NOTIFY_CRITICAL = "notify_critical"
CONF_NOTIFY_DAILY = "notify_daily"
CONF_NOTIFY_WEEKLY = "notify_weekly"
CONF_NOTIFY_TIME_DAILY = "notify_time_daily"
CONF_NOTIFY_TIME_WEEKLY = "notify_time_weekly"
CONF_NOTIFY_WEEKDAY = "notify_weekday"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_THRESHOLD_CRITICAL = 10
DEFAULT_THRESHOLD_LOW = 20
DEFAULT_THRESHOLD_WARNING = 30
DEFAULT_SCAN_INTERVAL = 30  # minutes
DEFAULT_NOTIFY_TIME_DAILY = "09:00"
DEFAULT_NOTIFY_TIME_WEEKLY = "08:00"
DEFAULT_NOTIFY_WEEKDAY = "mon"

# Battery levels
BATTERY_LEVEL_CRITICAL = "critical"
BATTERY_LEVEL_LOW = "low"
BATTERY_LEVEL_WARNING = "warning"
BATTERY_LEVEL_OK = "ok"
BATTERY_LEVEL_UNAVAILABLE = "unavailable"

WEEKDAYS = {
    "mon": "Maandag",
    "tue": "Dinsdag",
    "wed": "Woensdag",
    "thu": "Donderdag",
    "fri": "Vrijdag",
    "sat": "Zaterdag",
    "sun": "Zondag",
}
