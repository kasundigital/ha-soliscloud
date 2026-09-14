"""Data coordinator for SolisCloud."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SolisApiError, SolisCloudApi


class SolisDataCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    """Poll SolisCloud and retain the last good data through temporary failures."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SolisCloudApi,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name="SolisCloud",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, dict]:
        try:
            return await self.api.async_get_all()
        except SolisApiError as err:
            raise UpdateFailed(str(err)) from err
