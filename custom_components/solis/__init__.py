"""SolisCloud integration for Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SolisCloudApi
from .const import (
    CONF_KEY_ID,
    CONF_PLANT_ID,
    CONF_PORTAL_DOMAIN,
    CONF_REFRESH_OK,
    CONF_SECRET,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import SolisDataCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]
OFFICIAL_API_URL = "https://www.soliscloud.com:13333"
OBSOLETE_API_URLS = {
    "https://v3.soliscloud.com:13333",
    "https://v3.soliscloud.com:13333/",
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SolisCloud from a config entry."""
    data = dict(entry.data)
    configured_url = str(data.get(CONF_PORTAL_DOMAIN, OFFICIAL_API_URL)).rstrip("/")

    # SolisCloud's current user-auth API documentation lists
    # https://www.soliscloud.com:13333 as the base URL. Older beta builds of
    # this integration incorrectly migrated users to v3.soliscloud.com, so
    # migrate those entries back automatically.
    if configured_url in {url.rstrip("/") for url in OBSOLETE_API_URLS}:
        _LOGGER.warning(
            "Migrating obsolete SolisCloud API endpoint %s to %s",
            configured_url,
            OFFICIAL_API_URL,
        )
        configured_url = OFFICIAL_API_URL
        data[CONF_PORTAL_DOMAIN] = OFFICIAL_API_URL
        hass.config_entries.async_update_entry(entry, data=data)

    session = async_get_clientsession(hass)
    api = SolisCloudApi(
        session=session,
        base_url=configured_url,
        key_id=data[CONF_KEY_ID],
        secret=data[CONF_SECRET],
        station_id=data[CONF_PLANT_ID],
    )
    coordinator = SolisDataCoordinator(
        hass,
        api,
        int(data.get(CONF_REFRESH_OK, DEFAULT_SCAN_INTERVAL)),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "name": data.get(CONF_NAME, DEFAULT_NAME),
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a SolisCloud config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded
