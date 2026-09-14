"""Diagnostics support for SolisCloud."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_KEY_ID, CONF_SECRET, CONF_USERNAME, DOMAIN

TO_REDACT = {CONF_SECRET, CONF_KEY_ID, CONF_USERNAME}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime["coordinator"]
    return {
        "config": async_redact_data(dict(entry.data), TO_REDACT),
        "last_update_success": coordinator.last_update_success,
        "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
        "inverters": {
            serial: sorted(values.keys())
            for serial, values in (coordinator.data or {}).items()
        },
    }
