"""SolisCloud integration for Home Assistant."""

from __future__ import annotations

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
    DEFAULT_API_URL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import SolisDataCoordinator

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SolisCloud from a config entry."""
    session = async_get_clientsession(hass)
    api = SolisCloudApi(
        session=session,
        base_url=entry.data.get(CONF_PORTAL_DOMAIN, DEFAULT_API_URL),
        key_id=entry.data[CONF_KEY_ID],
        secret=entry.data[CONF_SECRET],
        station_id=entry.data[CONF_PLANT_ID],
    )
    coordinator = SolisDataCoordinator(
        hass,
        api,
        int(entry.data.get(CONF_REFRESH_OK, DEFAULT_SCAN_INTERVAL)),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "name": entry.data.get(CONF_NAME, DEFAULT_NAME),
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a SolisCloud config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return unloaded
