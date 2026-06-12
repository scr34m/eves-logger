import sys
import asyncio
import json
import paho.mqtt.client as mqtt
import re

sys.path.insert(0, "/home/kerge/1")
from pysolarman import Solarman

MQTT_BROKER = "192.168.1.15"
MQTT_PORT = 1883
MQTT_PREFIX = "evse/"
EVSE_LOGGER_IP = "192.168.1.179"
EVSE_LOGGER_PORT = 8899
EVSE_LOGGER_TRANSPORT = "tcp"
EVSE_LOGGER_SERIAL_NUMBER = 1224117709
EVSE_LOGGER_SLAVE_ID = 3

DISCOVERY_PREFIX = "homeassistant"

client = mqtt.Client()
client.reconnect_delay_set(min_delay=1,max_delay=60)
client.connect_async(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

modbus = Solarman(EVSE_LOGGER_IP, EVSE_LOGGER_PORT, EVSE_LOGGER_TRANSPORT, EVSE_LOGGER_SERIAL_NUMBER, EVSE_LOGGER_SLAVE_ID, 10)

registers = [
    {'title': 'Device Serial Number', 'registers': [0x0002, 0x0003, 0x0004, 0x0005, 0x0006], 'icon': 'mdi:identifier'},
    {'title': 'Device Firmware Version', 'registers': [0x0007], 'icon': 'mdi:identifier'},
    {'title': 'Device Protocol Version', 'registers': [0x0001], 'icon': 'mdi:identifier'},
    {'title': 'Device Public Group Number', 'registers': [0x0009], 'icon': 'mdi:identifier'},
    {'title': 'LoRa Inverter Link', 'registers': [0x0014], 'icon': 'mdi:link-variant'},
    {'title': 'Device Specification', 'registers': [0x0013], 'mask': 0xFF00, 'values': {0x0000: "22 kW EV Charger", 0x0100: "11 kW EV Charger"}, 'icon': 'mdi:identifier'},
    {'title': 'Communication Mode', 'registers': [0x0015], 'mask': 0xFF00, 'values': {0x0000: "WiFi", 0x0100: "LoRa"}, 'icon': 'mdi:identifier'},
    {'title': 'Charging Control State', 'registers': [0x0039], 'mask': 0xFF00, 'values': {0x0000: "Standalone", 0x0100: "Authorized", 0x0200: "Limited", 0x0300: "Authorized + Limited"}, 'icon': 'mdi:identifier'},
    {'title': 'Charging Operational State', 'registers': [0x0039], 'mask': 0x007F, 'values': {0x0001: "Available", 0x0002: "Finishing", 0x0004: "Preparing", 0x0008: "SuspendedEV", 0x0010: "SuspendedEVSE", 0x0020: "Charging", 0x0040: "Faulted"}, 'icon': 'mdi:identifier'},
    {'title': 'Grid Voltage L1', 'registers': [0x0029], 'scale': 0.1, 'unit': 'V', 'device_class': 'voltage', 'state_class': 'measurement', 'icon': "mdi:sine-wave"},
    {'title': 'Grid Voltage L2', 'registers': [0x002A], 'scale': 0.1, 'unit': 'V', 'device_class': 'voltage', 'state_class': 'measurement', 'icon': "mdi:sine-wave"},
    {'title': 'Grid Voltage L3', 'registers': [0x002B], 'scale': 0.1, 'unit': 'V', 'device_class': 'voltage', 'state_class': 'measurement', 'icon': "mdi:sine-wave"},
    {'title': 'Charger Fault', 'registers': [0x0036], 'bit_values': {0: "Overcurrent", 1: "Overvoltage", 2: "Undervoltage", 3: "Control Pilot", 4: "Communication Timeout", 5: "Cable", 6: "Stuck Relay", 7: "Overtemperature", 8: "Undertemperature", 9: "Residual Current", 10: "Protective Earth"}, 'device_class': 'problem', 'icon': 'mdi:identifier'},
    {'title': 'Charging Power L1', 'registers': [0x0026], 'scale': 10, 'unit': 'W', 'device_class': 'power', 'state_class': 'measurement', 'icon': 'mdi:lightning-bolt'},
    {'title': 'Charging Power L2', 'registers': [0x0027], 'scale': 10, 'unit': 'W', 'device_class': 'power', 'state_class': 'measurement', 'icon': 'mdi:lightning-bolt'},
    {'title': 'Charging Power L3', 'registers': [0x0028], 'scale': 10, 'unit': 'W', 'device_class': 'power', 'state_class': 'measurement', 'icon': 'mdi:lightning-bolt'},
    {'title': 'Charging Voltage L1', 'registers': [0x002C], 'scale': 0.1, 'unit': 'V', 'device_class': 'voltage', 'state_class': 'measurement', 'icon': "mdi:sine-wave"},
    {'title': 'Charging Voltage L2', 'registers': [0x002D], 'scale': 0.1, 'unit': 'V', 'device_class': 'voltage', 'state_class': 'measurement', 'icon': "mdi:sine-wave"},
    {'title': 'Charging Voltage L3', 'registers': [0x002E], 'scale': 0.1, 'unit': 'V', 'device_class': 'voltage', 'state_class': 'measurement', 'icon': "mdi:sine-wave"},
    {'title': 'Charging Current L1', 'registers': [0x002F], 'scale': 0.1, 'unit': 'A', 'device_class': 'current', 'state_class': 'measurement', 'icon': "mdi:current-ac"},
    {'title': 'Charging Current L2', 'registers': [0x0030], 'scale': 0.1, 'unit': 'A', 'device_class': 'current', 'state_class': 'measurement', 'icon': "mdi:current-ac"},
    {'title': 'Charging Current L3', 'registers': [0x0031], 'scale': 0.1, 'unit': 'A', 'device_class': 'current', 'state_class': 'measurement', 'icon': "mdi:current-ac"},
    {'title': 'Relay Temperature 1', 'registers': [0x001D], 'mask': 0x00FF, 'offset': 50, 'icon': "mdi:thermometer"},
    {'title': 'Relay Temperature 2', 'registers': [0x001D], 'mask': 0xFF00, 'offset': 12800, 'divide': 256, 'icon': "mdi:thermometer"},
    {'title': 'Total EV Charge', 'registers': [0x0022], 'unit': 'kWh', 'device_class': 'energy', 'state_class': 'total_increasing', 'icon': 'mdi:ev-station'},
    {'title': 'Today EV Charge', 'registers': [0x0023], 'scale': 0.1, 'unit': 'kWh', 'device_class': 'energy', 'state_class': 'total', 'icon': 'mdi:ev-station'},
]

def publish(topic, value):
    state_topic = f"{MQTT_PREFIX}{topic}"
    print(f"Publishing to {MQTT_PREFIX + topic}: {value}")
    client.publish(state_topic, value)

def publish_discovery(reg):
    topic = topic_name(reg["title"])
    unique_id = f"evse_{topic}"
    config_topic = f"{DISCOVERY_PREFIX}/sensor/{unique_id}/config"
    state_topic = f"{MQTT_PREFIX}{topic}"

    payload = {
        "name": reg["title"],
        "unique_id": unique_id,
        "state_topic": state_topic,
        "device": {
            "identifiers": [EVSE_LOGGER_SERIAL_NUMBER],
            "name": "EVSE Charger",
            "manufacturer": "Solarman",
            "model": "EV Charger"
        }
    }

    if "icon" in reg:
        payload["icon"] = reg["icon"]

    if "unit" in reg:
        payload["unit_of_measurement"] = reg["unit"]

    if "device_class" in reg:
        payload["device_class"] = reg["device_class"]

    if "state_class" in reg:
        payload["state_class"] = reg["state_class"]

    client.publish(config_topic, json.dumps(payload), qos=1,retain=True)

def topic_name(title):
    return re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')

async def main():
    for reg in registers:
        publish_discovery(reg)    

    try:
        while True:
            try:
                for reg in registers:
                    raw_values = await modbus.execute(3, reg['registers'][0], count=len(reg['registers']))
                    if len(reg['registers']) == 1:
                        value = raw_values[0]
                        if 'mask' in reg:
                            value = value & reg['mask']
                        if 'scale' in reg:
                            value = value * reg['scale']
                        if 'offset' in reg:
                            value = value - reg['offset']
                        if 'divide' in reg:
                            value = value // reg['divide']

                        if 'values' in reg:
                            value = reg['values'].get(value, f"Unknown ({value})")
                        if 'bit_values' in reg:
                            value = json.dumps([reg['bit_values'].get(i, f"Unknown ({i})") for i in range(16) if value & (1 << i)])
                    else:
                        value = json.dumps(raw_values)

                    topic = topic_name(reg['title'])
                    publish(topic, value)
            except Exception as e:
                print(f"Error: {e}")
            await asyncio.sleep(60)
    finally:
        client.loop_stop()
        client.disconnect()
        modbus.close()

asyncio.run(main())