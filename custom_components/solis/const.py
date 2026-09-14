"""Constants and backward-compatible sensor definitions for SolisCloud."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactivePower,
    UnitOfTemperature,
)

DOMAIN = "solis"
DEFAULT_NAME = "Solis"
DEFAULT_API_URL = "https://v3.soliscloud.com:13333"
DEFAULT_SCAN_INTERVAL = 300
DEFAULT_ERROR_INTERVAL = 60

CONF_PORTAL_DOMAIN = "portal_domain"
CONF_USERNAME = "portal_username"
CONF_KEY_ID = "portal_key_id"
CONF_SECRET = "portal_secret"
CONF_PLANT_ID = "portal_plant_id"
CONF_REFRESH_OK = "refresh_ok"
CONF_REFRESH_NOK = "refresh_nok"


@dataclass(frozen=True, slots=True)
class SolisSensorDescription:
    """Description of one legacy-compatible Solis sensor."""

    key: str
    name: str
    unit: str | None = None
    icon: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None


SENSORS: tuple[SolisSensorDescription, ...] = (
    SolisSensorDescription("currentState", "Power State", icon="mdi:power", state_class=SensorStateClass.MEASUREMENT),
    SolisSensorDescription("state", "State", icon="mdi:state-machine", state_class=SensorStateClass.MEASUREMENT),
    SolisSensorDescription("dataTimestamp", "Timestamp Measurements Received", icon="mdi:calendar-clock", state_class=SensorStateClass.MEASUREMENT),
    SolisSensorDescription("status", "Status", icon="mdi:solar-power"),
    SolisSensorDescription("hmiVersionAll", "HMI Version all", icon="mdi:solar-power"),
    SolisSensorDescription("inverterTemperature", "Temperature", UnitOfTemperature.CELSIUS, "mdi:thermometer", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("uAc1", "AC Voltage R", UnitOfElectricPotential.VOLT, "mdi:flash-outline", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("uAc2", "AC Voltage S", UnitOfElectricPotential.VOLT, "mdi:flash-outline", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("uAc3", "AC Voltage T", UnitOfElectricPotential.VOLT, "mdi:flash-outline", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("iAc1", "AC Current R", UnitOfElectricCurrent.AMPERE, "mdi:flash-outline", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("iAc2", "AC Current S", UnitOfElectricCurrent.AMPERE, "mdi:flash-outline", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("iAc3", "AC Current T", UnitOfElectricCurrent.AMPERE, "mdi:flash-outline", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("pac", "AC Output Total Power", UnitOfPower.WATT, "mdi:solar-power", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("fac", "AC Frequency", UnitOfFrequency.HERTZ, "mdi:sine-wave", None, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("eToday", "Energy Today", UnitOfEnergy.KILO_WATT_HOUR, "mdi:flash-outline", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("eMonth", "Energy This Month", UnitOfEnergy.KILO_WATT_HOUR, "mdi:flash-outline", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("eYear", "Energy This Year", UnitOfEnergy.KILO_WATT_HOUR, "mdi:flash-outline", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("eTotal", "Energy Total", UnitOfEnergy.KILO_WATT_HOUR, "mdi:flash-outline", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("batteryPower", "Battery Power", UnitOfPower.WATT, "mdi:battery", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("storageBatteryVoltage", "Battery Voltage", UnitOfElectricPotential.VOLT, "mdi:battery", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("storageBatteryCurrent", "Battery Current", UnitOfElectricCurrent.AMPERE, "mdi:battery", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("batteryCapacitySoc", "Remaining Battery Capacity", PERCENTAGE, "mdi:battery", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("batteryHealthSoh", "Battery State Of Health", PERCENTAGE, "mdi:battery", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("batteryTotalChargeEnergy", "Total Energy Charged", UnitOfEnergy.KILO_WATT_HOUR, "mdi:battery-plus", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("batteryTotalDischargeEnergy", "Total Energy Discharged", UnitOfEnergy.KILO_WATT_HOUR, "mdi:battery-minus", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("batteryTodayChargeEnergy", "Daily Energy Charged", UnitOfEnergy.KILO_WATT_HOUR, "mdi:battery-plus", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("batteryTodayDischargeEnergy", "Daily Energy Discharged", UnitOfEnergy.KILO_WATT_HOUR, "mdi:battery-minus", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("batteryMonthChargeEnergy", "Monthly Energy Charged", UnitOfEnergy.KILO_WATT_HOUR, "mdi:battery-plus", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("batteryMonthDischargeEnergy", "Monthly Energy Discharged", UnitOfEnergy.KILO_WATT_HOUR, "mdi:battery-minus", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("batteryYearChargeEnergy", "Yearly Energy Charged", UnitOfEnergy.KILO_WATT_HOUR, "mdi:battery-plus", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("batteryYearDischargeEnergy", "Yearly Energy Discharged", UnitOfEnergy.KILO_WATT_HOUR, "mdi:battery-minus", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("gridPurchasedDayEnergy", "Daily Grid Energy Purchased", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("homeLoadEnergy", "Daily Grid Energy Used", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("gridSellDayEnergy", "Daily On-grid Energy", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("gridPurchasedMonthEnergy", "Monthly Grid Energy Purchased", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("gridSellMonthEnergy", "Monthly On-grid Energy", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("gridPurchasedYearEnergy", "Yearly Grid Energy Purchased", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("gridSellYearEnergy", "Yearly On-grid Energy", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("gridPurchasedTotalEnergy", "Total Energy Purchased", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("gridSellTotalEnergy", "Total On-grid Energy", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("homeLoadTotalEnergy", "Total Energy Used", UnitOfEnergy.KILO_WATT_HOUR, "mdi:transmission-tower", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("psum", "Power Grid total power", UnitOfPower.WATT, "mdi:home-export-outline", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("familyLoadPower", "Total Consumption power", UnitOfPower.WATT, "mdi:home-import-outline", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("pA", "Grid Phase1 Power", UnitOfPower.WATT, "mdi:home-import-outline", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("pB", "Grid Phase2 Power", UnitOfPower.WATT, "mdi:home-import-outline", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("pC", "Grid Phase3 Power", UnitOfPower.WATT, "mdi:home-import-outline", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("aLookedPower", "Grid Phase1 Apparent Power", UnitOfApparentPower.VOLT_AMPERE, "mdi:home-import-outline", None, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("bLookedPower", "Grid Phase2 Apparent Power", UnitOfApparentPower.VOLT_AMPERE, "mdi:home-import-outline", None, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("cLookedPower", "Grid Phase3 Apparent Power", UnitOfApparentPower.VOLT_AMPERE, "mdi:home-import-outline", None, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("aReactivePower", "Grid Phase1 Reactive Power", UnitOfReactivePower.VOLT_AMPERE_REACTIVE, "mdi:home-import-outline", None, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("bReactivePower", "Grid Phase2 Reactive Power", UnitOfReactivePower.VOLT_AMPERE_REACTIVE, "mdi:home-import-outline", None, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("cReactivePower", "Grid Phase3 Reactive Power", UnitOfReactivePower.VOLT_AMPERE_REACTIVE, "mdi:home-import-outline", None, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("socChargingSet", "Force Charge SOC", PERCENTAGE, "mdi:battery", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("socDischargeSet", "Force Discharge SOC", PERCENTAGE, "mdi:battery", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("bypassLoadPower", "Backup Load Power", UnitOfPower.WATT, "mdi:battery-charging", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("backupTodayEnergy", "Daily Backup Energy", UnitOfEnergy.KILO_WATT_HOUR, "mdi:home-import-outline", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    SolisSensorDescription("iA", "Meter item A current", UnitOfElectricCurrent.AMPERE, "mdi:home-import-outline", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("uA", "Meter item A volt", UnitOfElectricPotential.VOLT, "mdi:home-import-outline", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("iB", "Meter item B current", UnitOfElectricCurrent.AMPERE, "mdi:home-import-outline", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("uB", "Meter item B volt", UnitOfElectricPotential.VOLT, "mdi:home-import-outline", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("iC", "Meter item C current", UnitOfElectricCurrent.AMPERE, "mdi:home-import-outline", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
    SolisSensorDescription("uC", "Meter item C volt", UnitOfElectricPotential.VOLT, "mdi:home-import-outline", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
)

PV_SENSORS: tuple[SolisSensorDescription, ...] = tuple(
    item
    for i in range(1, 25)
    for item in (
        SolisSensorDescription(f"uPv{i}", f"DC Voltage PV{i}", UnitOfElectricPotential.VOLT, "mdi:flash-outline", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT),
        SolisSensorDescription(f"iPv{i}", f"DC Current PV{i}", UnitOfElectricCurrent.AMPERE, "mdi:flash-outline", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT),
        SolisSensorDescription(f"pow{i}", f"DC Power PV{i}", UnitOfPower.WATT, "mdi:solar-power", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    )
)

ALL_SENSORS = SENSORS + PV_SENSORS
SENSOR_BY_KEY = {sensor.key: sensor for sensor in ALL_SENSORS}
