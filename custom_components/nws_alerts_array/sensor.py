import logging

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from . import AlertsDataUpdateCoordinator
from .const import ATTRIBUTION
from .const import CONF_INTERVAL
from .const import CONF_TIMEOUT
from .const import CONF_ZONE_ID
from .const import COORDINATOR
from .const import DEFAULT_ICON
from .const import DEFAULT_INTERVAL
from .const import DEFAULT_NAME
from .const import DEFAULT_TIMEOUT
from .const import DOMAIN

# ---------------------------------------------------------
# API Documentation
# ---------------------------------------------------------
# https://www.weather.gov/documentation/services-web-api
# https://forecast-v3.weather.gov/documentation
# ---------------------------------------------------------

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ZONE_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_INTERVAL, default=DEFAULT_INTERVAL): int,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Configuration from yaml"""
    if DOMAIN not in hass.data.keys():
        hass.data.setdefault(DOMAIN, {})
        config.entry_id = slugify(f"{config.get(CONF_ZONE_ID)}")
        config.data = config
    else:
        config.entry_id = slugify(f"{config.get(CONF_ZONE_ID)}")
        config.data = config

    # Setup the data coordinator
    coordinator = AlertsDataUpdateCoordinator(
        hass,
        config,
        config[CONF_TIMEOUT],
        config[CONF_INTERVAL],
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN][config.entry_id] = {
        COORDINATOR: coordinator,
    }
    async_add_entities([NWSAlertArraySensor(hass, config)], True)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup the sensor platform."""
    async_add_entities([NWSAlertArraySensor(hass, entry)], True)


class NWSAlertArraySensor(CoordinatorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(hass.data[DOMAIN][entry.entry_id][COORDINATOR])
        self._config = entry
        self._name = entry.data[CONF_NAME]
        self._icon = DEFAULT_ICON
        self._state = 0
        self._alerts_url = None
        self._title = None
        self._alert_url = None
        self._id = None
        self._message_type = None
        self._status = None
        self._severity = None
        self._certainty = None
        self._headline = None
        self._description = None
        self._spoken = None
        self._instruction = None
        self._expires = None
        self._zone_id = entry.data[CONF_ZONE_ID].replace(" ", "")
        self.coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
        _LOGGER.debug("Raw Coordinator Data: %s" % (self.coordinator.data))

    @property
    def unique_id(self):
        """
        Return a unique, Home Assistant friendly identifier for this entity.
        """
        return f"{slugify(self._name)}_{self._config.entry_id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        elif "state" in self.coordinator.data.keys():
            return self.coordinator.data["state"]
        else:
            return None

    @property
    def extra_state_attributes(self):
        _LOGGER.debug("Extra State Attributes Raw Data: %s" % (self.coordinator.data))
        """Return the state message."""
        attrs = {}

        if self.coordinator.data is None or not self.coordinator.data:
            _LOGGER.debug("Self Coordinator Data is blank")
            return attrs

        attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
        attrs["title"] = self.coordinator.data["title"]
        attrs["alerts_url"] = self.coordinator.data["alerts_url"]
        attrs["alert_url"] = self.coordinator.data["alert_url"]
        attrs["id"] = self.coordinator.data["id"]
        attrs["message_type"] = self.coordinator.data["message_type"]
        attrs["status"] = self.coordinator.data["status"]
        attrs["severity"] = self.coordinator.data["severity"]
        attrs["certainty"] = self.coordinator.data["certainty"]
        attrs["headline"] = self.coordinator.data["headline"]
        attrs["description"] = self.coordinator.data["description"]
        attrs["spoken"] = self.coordinator.data["spoken"]
        attrs["instruction"] = self.coordinator.data["instruction"]
        attrs["expires"] = self.coordinator.data["expires"]
        _LOGGER.debug("Raw Attrs Data: %s" % (attrs))
        return attrs

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
