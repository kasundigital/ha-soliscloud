"""Config flow for SolisCloud."""

from __future__ import annotations

import logging
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
    DEFAULT_ERROR_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)
OFFICIAL_API_URL = "https://www.soliscloud.com:13333"


class SolisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle SolisCloud configuration."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            portal_domain = str(user_input[CONF_PORTAL_DOMAIN]).strip().rstrip("/")
            if not portal_domain.startswith(("https://", "http://")):
                errors["base"] = "invalid_url"
            else:
                try:
                    api = SolisCloudApi(
                        session=async_get_clientsession(self.hass),
                        base_url=portal_domain,
                        key_id=user_input[CONF_KEY_ID],
                        secret=user_input[CONF_SECRET],
                        station_id=user_input[CONF_PLANT_ID],
                    )
                    await api.async_validate()
                except SolisAuthError as err:
                    _LOGGER.warning("SolisCloud authentication failed: %s", err)
                    errors["base"] = "invalid_auth"
                except SolisNoInvertersError as err:
                    _LOGGER.warning("SolisCloud returned no inverters: %s", err)
                    errors["base"] = "no_inverters"
                except SolisConnectionError as err:
                    _LOGGER.warning("SolisCloud connection failed: %s", err)
                    errors["base"] = "cannot_connect"
                except SolisApiError as err:
                    _LOGGER.warning("SolisCloud API error: %s", err)
                    errors["base"] = "api_error"
                except Exception:  # noqa: BLE001 - config flow must surface a safe error.
                    _LOGGER.exception("Unexpected SolisCloud setup error")
                    errors["base"] = "unknown"
                else:
                    station_id = str(user_input[CONF_PLANT_ID])
                    await self.async_set_unique_id(station_id)
                    self._abort_if_unique_id_configured()
                    data = dict(user_input)
                    data[CONF_PORTAL_DOMAIN] = portal_domain
                    return self.async_create_entry(
                        title=f"SolisCloud {station_id}",
                        data=data,
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
                # Keep this field serializable in Home Assistant config flows.
                vol.Required(CONF_PORTAL_DOMAIN, default=OFFICIAL_API_URL): cv.string,
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
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "SolisOptionsFlow":
        return SolisOptionsFlow()


class SolisOptionsFlow(config_entries.OptionsFlow):
    """Allow refresh interval changes without removing the integration."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        entry = self.config_entry
        if user_input is not None:
            data = dict(entry.data)
            data.update(user_input)
            self.hass.config_entries.async_update_entry(entry, data=data)
            return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_REFRESH_OK,
                    default=entry.data.get(CONF_REFRESH_OK, DEFAULT_SCAN_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
                vol.Required(
                    CONF_REFRESH_NOK,
                    default=entry.data.get(CONF_REFRESH_NOK, DEFAULT_ERROR_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
