"""Async client for the official SolisCloud user API."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any

from aiohttp import ClientError, ClientSession


class SolisApiError(Exception):
    """Base SolisCloud API error."""


class SolisAuthError(SolisApiError):
    """Authentication/signature error."""


class SolisConnectionError(SolisApiError):
    """Network or HTTP error."""


class SolisNoInvertersError(SolisApiError):
    """No inverters were returned for the station."""


@dataclass(slots=True)
class SolisInverter:
    serial: str
    device_id: str
    data: dict[str, Any]


class SolisCloudApi:
    """Small SolisCloud API client using API key signing."""

    INVERTER_LIST = "/v1/api/inverterList"
    INVERTER_DETAIL = "/v1/api/inverterDetail"
    STATION_DETAIL = "/v1/api/stationDetail"

    def __init__(
        self,
        session: ClientSession,
        base_url: str,
        key_id: str,
        secret: str,
        station_id: str,
    ) -> None:
        self._session = session
        self.base_url = base_url.rstrip("/")
        self.key_id = key_id.strip()
        self._secret = secret.encode("utf-8")
        self.station_id = str(station_id).strip()

    def _headers(self, body: dict[str, Any], resource: str) -> dict[str, str]:
        payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
        content_md5 = base64.b64encode(hashlib.md5(payload).digest()).decode("utf-8")
        content_type = "application/json"
        date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        signing = f"POST\n{content_md5}\n{content_type}\n{date}\n{resource}"
        signature = base64.b64encode(
            hmac.new(self._secret, signing.encode("utf-8"), hashlib.sha1).digest()
        ).decode("utf-8")
        return {
            "Content-MD5": content_md5,
            "Content-Type": content_type,
            "Date": date,
            "Authorization": f"API {self.key_id}:{signature}",
        }

    async def _post(self, resource: str, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}{resource}"
        try:
            async with self._session.post(
                url,
                json=body,
                headers=self._headers(body, resource),
                timeout=15,
            ) as response:
                text = await response.text()
                if response.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                    raise SolisAuthError(f"SolisCloud returned HTTP {response.status}")
                if response.status != HTTPStatus.OK:
                    raise SolisConnectionError(
                        f"SolisCloud returned HTTP {response.status}: {text[:250]}"
                    )
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError as err:
                    raise SolisConnectionError("SolisCloud returned invalid JSON") from err
        except SolisApiError:
            raise
        except (ClientError, TimeoutError) as err:
            raise SolisConnectionError(str(err)) from err

        code = str(payload.get("code", ""))
        if code and code != "0":
            msg = payload.get("msg") or payload.get("message") or "Unknown API error"
            # Signature/key problems are commonly returned as API payload errors.
            lowered = str(msg).lower()
            if any(term in lowered for term in ("auth", "sign", "key", "permission")):
                raise SolisAuthError(f"SolisCloud API {code}: {msg}")
            raise SolisApiError(f"SolisCloud API {code}: {msg}")
        return payload

    async def async_get_inverters(self) -> dict[str, str]:
        payload = await self._post(self.INVERTER_LIST, {"stationId": self.station_id})
        records = (((payload.get("data") or {}).get("page") or {}).get("records") or [])
        result: dict[str, str] = {}
        for record in records:
            serial = record.get("sn")
            device_id = record.get("id")
            if serial and device_id:
                result[str(serial)] = str(device_id)
        if not result:
            raise SolisNoInvertersError(
                "SolisCloud returned no inverters for this Station ID. Check the Station ID and API permissions."
            )
        return result

    async def async_get_station_detail(self) -> dict[str, Any]:
        payload = await self._post(self.STATION_DETAIL, {"id": self.station_id})
        return dict(payload.get("data") or {})

    async def async_get_inverter_detail(self, serial: str, device_id: str) -> dict[str, Any]:
        payload = await self._post(
            self.INVERTER_DETAIL,
            {"id": device_id, "sn": serial},
        )
        return dict(payload.get("data") or {})

    async def async_validate(self) -> dict[str, str]:
        return await self.async_get_inverters()

    async def async_get_all(self) -> dict[str, dict[str, Any]]:
        """Return merged inverter + station data keyed by inverter serial."""
        inverters = await self.async_get_inverters()
        station = await self.async_get_station_detail()
        result: dict[str, dict[str, Any]] = {}

        for serial, device_id in inverters.items():
            inverter = await self.async_get_inverter_detail(serial, device_id)
            merged = dict(station)
            merged.update(inverter)
            merged["serial"] = serial
            merged["deviceId"] = device_id
            self._normalise_units(merged)
            self._normalise_battery_sign(merged)
            result[serial] = merged
        return result

    @staticmethod
    def _convert_unit(data: dict[str, Any], value_key: str, unit_key: str) -> None:
        if value_key not in data or unit_key not in data:
            return
        try:
            value = float(data[value_key])
        except (TypeError, ValueError):
            return
        unit = str(data[unit_key])
        if unit == "kW":
            data[value_key] = value * 1000
        elif unit == "MWh":
            data[value_key] = value * 1000
        elif unit == "GWh":
            data[value_key] = value * 1_000_000

    @classmethod
    def _normalise_units(cls, data: dict[str, Any]) -> None:
        pairs = (
            ("pac", "pacStr"),
            ("batteryPower", "batteryPowerStr"),
            ("storageBatteryCurrent", "storageBatteryCurrentStr"),
            ("storageBatteryVoltage", "storageBatteryVoltageStr"),
            ("batteryTodayChargeEnergy", "batteryTodayChargeEnergyStr"),
            ("batteryTodayDischargeEnergy", "batteryTodayDischargeEnergyStr"),
            ("batteryMonthChargeEnergy", "batteryMonthChargeEnergyStr"),
            ("batteryMonthDischargeEnergy", "batteryMonthDischargeEnergyStr"),
            ("batteryYearChargeEnergy", "batteryYearChargeEnergyStr"),
            ("batteryYearDischargeEnergy", "batteryYearDischargeEnergyStr"),
            ("batteryTotalChargeEnergy", "batteryTotalChargeEnergyStr"),
            ("batteryTotalDischargeEnergy", "batteryTotalDischargeEnergyStr"),
            ("gridPurchasedTotalEnergy", "gridPurchasedTotalEnergyStr"),
            ("gridSellTotalEnergy", "gridSellTotalEnergyStr"),
            ("homeLoadTotalEnergy", "homeLoadTotalEnergyStr"),
            ("psum", "psumStr"),
            ("familyLoadPower", "familyLoadPowerStr"),
            ("bypassLoadPower", "bypassLoadPowerStr"),
            ("eMonth", "eMonthStr"),
            ("eYear", "eYearStr"),
            ("eTotal", "eTotalStr"),
            ("gridPurchasedDayEnergy", "gridPurchasedDayEnergyStr"),
            ("gridPurchasedMonthEnergy", "gridPurchasedMonthEnergyStr"),
            ("gridPurchasedYearEnergy", "gridPurchasedYearEnergyStr"),
            ("gridSellDayEnergy", "gridSellDayEnergyStr"),
            ("gridSellMonthEnergy", "gridSellMonthEnergyStr"),
            ("gridSellYearEnergy", "gridSellYearEnergyStr"),
            ("homeLoadEnergy", "homeLoadEnergyStr"),
        )
        for value_key, unit_key in pairs:
            cls._convert_unit(data, value_key, unit_key)

    @staticmethod
    def _normalise_battery_sign(data: dict[str, Any]) -> None:
        """Keep legacy sign convention: charging positive, discharging negative."""
        try:
            power = abs(float(data["batteryPower"]))
            current = float(data["storageBatteryCurrent"])
        except (KeyError, TypeError, ValueError):
            return
        data["batteryPower"] = power if current >= 0 else -power
