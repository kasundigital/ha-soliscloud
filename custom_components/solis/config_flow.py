"""Config flow for SolisCloud."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    SolisApiError,
    SolisAuthError,
    SolisCloudApi,
    SolisConnectionError,
    SolisNoInvertersError,
)
from .const import (
    CONF_KEY_ID,
    CONF_PLANT_ID,
    CONF_PORTAL_DOMAIN,
    CONF_REFRESH_NOK,
    CONF_REFRESH_OK,
    CONF_SECRET,
    CONF_USERNAME,
    DEFAULT_API_URL,
    DEFAULT_ERROR_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class SolisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle SolisCloud configuration."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                api = SolisCloudApi(
                    session=async_get_clientsession(self.hass),
                    base_url=user_input[CONF_PORTAL_DOMAIN],
                    key_id=user_input[CONF_KEY_ID],
                    secret=user_input[CONF_SECRET],
                    station_id=user_input[CONF_PLANT_ID],
                )
                await api.async_validate()
            except SolisAuthError:
                errors["base"] = "invalid_auth"
            except SolisNoInvertersError:
                errors["base"] = "no_inverters"
            except SolisConnectionError:
                errors["base"] = "cannot_connect"
            except SolisApiError:
                errors["base"] = "api_error"
            except Exception:  # Home Assistant shows a safe generic error; details go to logs.
                errors["base"] = "unknown"
            else:
                station_id = str(user_input[CONF_PLANT_ID])
                await self.async_set_unique_id(station_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"SolisCloud {station_id}",
                    data=user_input,
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Required(CONF_PORTAL_DOMAIN, default=DEFAULT_API_URL): cv.url,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_KEY_ID): cv.string,
                vol.Required(CONF_SECRET): cv.string,
                vol.Required(CONF_PLANT_ID): cv.string,
                vol.Required(CONF_REFRESH_OK, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=30, max=3600)
                ),
                vol.Required(CONF_REFRESH_NOK, default=DEFAULT_ERROR_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=30, max=3600)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return SolisOptionsFlow(config_entry)


class SolisOptionsFlow(config_entries.OptionsFlow):
    """Allow refresh interval changes without removing the integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            data = dict(self._entry.data)
            data.update(user_input)
            self.hass.config_entries.async_update_entry(self._entry, data=data)
            return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_REFRESH_OK,
                    default=self._entry.data.get(CONF_REFRESH_OK, DEFAULT_SCAN_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
                vol.Required(
                    CONF_REFRESH_NOK,
                    default=self._entry.data.get(CONF_REFRESH_NOK, DEFAULT_ERROR_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
