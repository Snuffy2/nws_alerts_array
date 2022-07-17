""" NWS Alerts """
import logging
from datetime import timedelta

import aiohttp
from async_timeout import timeout
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_ENDPOINT,
    CONF_INTERVAL,
    CONF_TIMEOUT,
    CONF_ZONE_ID,
    COORDINATOR,
    DEFAULT_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    USER_AGENT,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Load the saved entities."""
    # Print startup message
    _LOGGER.info(
        "Version %s is starting, if you have any issues please report" " them here: %s",
        VERSION,
        ISSUE_URL,
    )
    hass.data.setdefault(DOMAIN, {})

    if entry.unique_id is not None:
        hass.config_entries.async_update_entry(entry, unique_id=None)

        ent_reg = async_get(hass)
        for entity in async_entries_for_config_entry(ent_reg, entry.entry_id):
            ent_reg.async_update_entity(entity.entity_id, new_unique_id=entry.entry_id)

    # Setup the data coordinator
    coordinator = AlertsDataUpdateCoordinator(
        hass,
        entry.data,
        entry.data.get(CONF_TIMEOUT),
        entry.data.get(CONF_INTERVAL),
    )

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.info("Successfully removed sensor from the " + DOMAIN + " integration")
    except ValueError:
        pass
    return True


async def update_listener(hass, entry):
    """Update listener."""
    entry.data = entry.options
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "sensor"))


async def async_migrate_entry(hass, config_entry):
    """Migrate an old config entry."""
    version = config_entry.version

    # 1-> 2: Migration format
    if version == 1:
        _LOGGER.debug("Migrating from version %s", version)
        updated_config = config_entry.data.copy()

        if CONF_INTERVAL not in updated_config.keys():
            updated_config[CONF_INTERVAL] = DEFAULT_INTERVAL
        if CONF_TIMEOUT not in updated_config.keys():
            updated_config[CONF_TIMEOUT] = DEFAULT_TIMEOUT

        if updated_config != config_entry.data:
            hass.config_entries.async_update_entry(config_entry, data=updated_config)

        config_entry.version = 2
        _LOGGER.debug("Migration to version %s complete", config_entry.version)

    return True


class AlertsDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NWS Alert data."""

    def __init__(self, hass, config, the_timeout: int, interval: int):
        """Initialize."""
        self.interval = timedelta(minutes=interval)
        self.name = config[CONF_NAME]
        self.timeout = the_timeout
        self.config = config
        self.hass = hass

        _LOGGER.debug("Data will be updated every %s", self.interval)

        super().__init__(hass, _LOGGER, name=self.name, update_interval=self.interval)

    async def _async_update_data(self):
        """Fetch data"""
        async with timeout(self.timeout):
            try:
                data = await update_alerts(self.config)
            except Exception as error:
                raise UpdateFailed(error) from error
            return data


async def update_alerts(config) -> dict:
    """Fetch new state data for the sensor.
    This is the only method that should fetch new data for Home Assistant.
    """

    data = await async_get_state(config)
    return data


async def async_get_state(config) -> dict:
    """Query API for status."""

    values = {}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/ld+json"}
    data = None
    url = "%s/alerts/active/count" % API_ENDPOINT
    zone_id = config[CONF_ZONE_ID]
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            _LOGGER.debug("getting state for %s from %s" % (zone_id, url))
            if r.status == 200:
                data = await r.json()
    #_LOGGER.debug("Raw State Data: %s" % (data))
    if data is not None:
        # Reset values before reassigning
        values = {
            "state": 0,
            "alerts_url": None,
            "title": None,
            "alert_url": None,
            "id": None,
            "message_type": None,
            "status": None,
            "severity": None,
            "certainty": None,
            "description": None,
            "spoken": None,
            "headline": None,
            "instruction": None,
            "expires": None,
        }
        if "zones" in data:
            for zone in zone_id.split(","):
                if zone in data["zones"]:
                    values = await async_get_alerts(zone_id)
                    break

    return values


async def async_get_alerts(zone_id: str) -> dict:
    """Query API for Alerts."""

    values = {}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    data = None
    url = "%s/alerts/active?zone=%s" % (API_ENDPOINT, zone_id)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            _LOGGER.debug("getting alert for %s from %s" % (zone_id, url))
            if r.status == 200:
                data = await r.json()
    _LOGGER.debug("Raw Alert Data: %s" % (data))
    if data is not None:
        title = []
        headline = []
        alert_url = []
        id = []
        message_type = []
        status = []
        severity = []
        certainty = []
        description = []
        spoken = []
        instruction = []
        expires = []
        features = data["features"]
        for alert in features:
            if "parameters" in alert["properties"] and "NWSheadline" in alert["properties"]["parameters"] and alert["properties"]["parameters"]["NWSheadline"][0] is not None:
                spoken.append(alert["properties"]["parameters"]["NWSheadline"][0].replace("\n\n","<00temp00>").replace("\n"," ").replace("<00temp00>","\n\n").title())
            else:
                spoken.append(None)
            _LOGGER.debug("spoken appended")
            headline.append(alert["properties"]["headline"])
            _LOGGER.debug("headline appended")
            expires.append(alert["properties"]["expires"])
            _LOGGER.debug("expires appended")
            title.append(alert["properties"]["event"])
            _LOGGER.debug("title appended")
            if "description" in alert["properties"] and alert["properties"]["description"] is not None:
                description.append(alert["properties"]["description"].replace("\n\n","<00temp00>").replace("\n"," ").replace("<00temp00>","\n\n"))
            else:
                description.append(None)
            _LOGGER.debug("description appended")
            alert_url.append(alert["id"])
            _LOGGER.debug("alert_url appended")
            id.append(alert["properties"]["id"])
            _LOGGER.debug("id appended")
            message_type.append(alert["properties"]["messageType"])
            _LOGGER.debug("message_type appended")
            status.append(alert['properties']['status'])
            _LOGGER.debug("status appended")
            severity.append(alert["properties"]["severity"])
            _LOGGER.debug("severity appended")
            certainty.append(alert["properties"]["certainty"])
            _LOGGER.debug("certainty appended")
            if "instruction" in alert["properties"] and alert["properties"]["instruction"] is not None:
                instruction.append(alert["properties"]["instruction"].replace("\n\n","<00temp00>").replace("\n"," ").replace("<00temp00>","\n\n"))
            else:
                instruction.append(None)
            _LOGGER.debug("instruction appended")
        if len(title) > 0:
        #    event_str = []
        #    for item in events:
        #        #if event_str != "":
        #        #    event_str += " - "
        #        event_str.append(item)

            values["state"] = len(title)
            values["alerts_url"] = url
            values["title"] = title
            values["alert_url"] = alert_url
            values["id"] = id
            values["message_type"] = message_type
            values["status"] = status
            values["severity"] = severity
            values["certainty"] = certainty
            values["headline"] = headline
            values["description"] = description
            values["spoken"] = spoken
            values["instruction"] = instruction
            values["expires"] = expires
        else:
            values = {
                "state": 0,
                "alerts_url": url,
                "title": None,
                "alert_url": None,
                "id": None,
                "message_type": None,
                "status": None,
                "severity": None,
                "certainty": None,
                "headline": None,
                "description": None,
                "spoken": None,
                "instruction": None,
                "expires": None,
            }
    _LOGGER.debug("Values: %s" % (values))
    return values
