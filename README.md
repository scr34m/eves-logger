SUN-EVSE22K01-EU - EVSE Charger Modbus - Home Assistant Export
==

This project is an extraction of the Home Assistant Solarman pull request: [feat: Add Deye EV Charger (SUN-EVSE22K01-EU) support)](https://github.com/davidrapan/ha-solarman/pull/1073/changes/235cc10910996874ebca4fd4286b0ebf29feb374#diff-9237befa134dfa14257e7cc8e13e4c88193693f1b9b42ce50045a2fe2409ec5e)

At the time of writing, support for the SUN-EVSE22K01-EU charger is not officially provided by Deye, and the pull request is still pending review and merge.

## Configuration Parameters

| Setting | Description | Value |
|----------|-------------|--------|
| MQTT_BROKER | MQTT broker IP address | `192.168.1.15` |
| MQTT_PORT | MQTT broker port | `1883` |
| MQTT_PREFIX | MQTT topic prefix | `evse/` |
| EVSE_LOGGER_IP | EVSE Logger IP address | `192.168.1.179` |
| EVSE_LOGGER_PORT | EVSE Logger communication port | `8899` |
| EVSE_LOGGER_TRANSPORT | Communication protocol | `tcp` |
| EVSE_LOGGER_SERIAL_NUMBER | EVSE Logger serial number | `1224117709` |
| EVSE_LOGGER_SLAVE_ID | Modbus Slave ID | `3` |
| DISCOVERY_PREFIX | Home Assistant MQTT discovery prefix | `homeassistant` |

Resources
===
- https://github.com/davidrapan/ha-solarman/discussions/731
- https://github.com/DJm00n/ha-solarman/tree/feat/deye-evse