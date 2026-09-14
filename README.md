# HA SolisCloud

A Home Assistant custom integration for the SolisCloud user API, maintained by **Kasun Indika**.

The project is designed as a backward-compatible continuation for existing `solis` installations. Its primary goal is to keep existing Home Assistant entity IDs, Recorder history, automations, Energy Dashboard references, and Grafana/MariaDB queries working while tracking SolisCloud API changes.

> **Beta:** test on a Home Assistant backup first. The monitoring API is the initial focus. Experimental inverter-control entities from the older project are not included in this first beta.

## Why this project exists

SolisCloud moved the user API endpoint from:

```text
https://www.soliscloud.com:13333
```

to:

```text
https://v3.soliscloud.com:13333
```

Older released integrations can therefore fail with a generic `Cannot login with provided URL and credentials` message even when the API Key ID, Secret and Station ID are valid.

HA SolisCloud uses the current v3 endpoint by default and automatically migrates an existing config entry that still contains the old `www.soliscloud.com:13333` endpoint.

## Backward compatibility

The integration intentionally keeps the Home Assistant domain:

```text
solis
```

and uses the same legacy unique-ID formula:

```text
<inverter serial><integration name> <sensor label>
```

with spaces changed to underscores. It also keeps the legacy device identity:

```text
Solis_Inverter_<serial>
```

This is important because Home Assistant can reconnect the entities to existing entity-registry entries instead of creating a second set of sensors.

Examples of compatible entity IDs include:

```text
sensor.solis_inverter_<serial>_solis_dc_power_pv1
sensor.solis_inverter_<serial>_solis_dc_power_pv2
sensor.solis_inverter_<serial>_solis_battery_power
sensor.solis_inverter_<serial>_solis_remaining_battery_capacity
sensor.solis_inverter_<serial>_solis_total_consumption_power
sensor.solis_inverter_<serial>_solis_energy_today
sensor.solis_inverter_<serial>_solis_energy_this_month
sensor.solis_inverter_<serial>_solis_daily_energy_charged
sensor.solis_inverter_<serial>_solis_daily_energy_discharged
sensor.solis_inverter_<serial>_solis_daily_grid_energy_used
sensor.solis_inverter_<serial>_solis_temperature
```

PV voltage/current/power sensors are supported for PV1 through PV24 when SolisCloud returns those fields.

## Installation with HACS

Until the repository is accepted into the default HACS catalog:

1. Open **HACS**.
2. Open the menu and choose **Custom repositories**.
3. Add:

   ```text
   https://github.com/kasundigital/ha-soliscloud
   ```

4. Select **Integration** as the category.
5. Install **HA SolisCloud**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services**.

If you are migrating from `hultenvp/solis-sensor`, make a Home Assistant backup before replacing the integration. Do not rename your existing Solis entities.

## Configuration

You need:

- SolisCloud portal username/email
- API Key ID
- API Secret
- Station ID

The default API URL is:

```text
https://v3.soliscloud.com:13333
```

The integration validates the API before saving the config entry and distinguishes between authentication errors, connection errors, API errors and a valid account that returns no inverter for the supplied Station ID.

## Diagnostics

Home Assistant diagnostics are supported. API Secret, API Key ID and portal username are redacted from the generated diagnostics payload.

## Supported monitoring data

Sensors are created only when the corresponding field is returned by SolisCloud. Supported groups include:

- inverter state, AC output, frequency and temperature
- today/month/year/lifetime solar energy
- battery power, voltage, current, SOC and SOH
- battery charge/discharge energy totals and daily/monthly/yearly counters
- grid import/export energy and grid power
- household consumption/load power
- backup-load power and energy
- phase power, apparent power and reactive power
- meter phase voltage/current values
- PV1–PV24 voltage, current and power

## Troubleshooting

Enable debug logging in Home Assistant if setup fails:

```yaml
logger:
  logs:
    custom_components.solis: debug
```

Then reproduce the problem and check **Settings → System → Logs**. Do not publish API secrets in an issue.

## Project status / roadmap

Planned work includes improved station discovery, richer diagnostics, tests against additional inverter models, multi-station UX, optional control support, translations and HACS-default submission.

## Credits

This project was created to preserve compatibility with the entity naming and SolisCloud API behaviour used by [`hultenvp/solis-sensor`](https://github.com/hultenvp/solis-sensor). That project is Apache-2.0 licensed. Relevant upstream ideas and compatibility behaviour are acknowledged in `NOTICE`.

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.
