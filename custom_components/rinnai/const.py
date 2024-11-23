from collections import namedtuple

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import Platform

DOMAIN = "rinnai"

PRIORITY_DISCRIMINATOR = "HomeAssistant"

CONF_AUTO_PRIORITY = "auto_priority"
CONF_SCAN_INTERVAL_BUS = "scan_interval_bus"
CONF_SCAN_INTERVAL_TELA = "scan_interval_tela"
CONF_SCAN_INTERVAL_CONSUMO = "scan_interval_consumo"

DEFAULT_NAME = "Rinnai"
DEFAULT_HOST = "WIFI-RINNAI"

DEFAULT_AUTO_PRIORITY = False
DEFAULT_SCAN_INTERVAL_BUS = 15
DEFAULT_SCAN_INTERVAL_TELA = 0
DEFAULT_SCAN_INTERVAL_CONSUMO = 60 * 5

Sensor = namedtuple(
    "Sensor", ["name", "coeff", "unit", "platform", "device_class", "enabled", "debug"]
)

STATUS = []
ERROR = []

TEMPERATURES_MAP = {
    "3": 3500,
    "4": 3600,
    "5": 3700,
    "6": 3800,
    "7": 3900,
    "8": 4000,
    "9": 4100,
    "10": 4200,
    "11": 4300,
    "12": 4400,
    "13": 4500,
    "14": 4600,
    "16": 4800,
    "18": 5000,
    "19": 5500,
    "20": 6000,
}

# fmt: off
SENSORS = [
    #      name                               coeff    unit         platform                 device_class                        enabled  debug
    Sensor("status",                          1,       None,        Platform.SENSOR,         None,                               True,    False),
    Sensor("flame",                           None,    None,        Platform.BINARY_SENSOR,  BinarySensorDeviceClass.POWER,      False,   False),
    Sensor("error",                           1,       None,        Platform.SENSOR,         None,                               True,    False),
    Sensor("error_message",                   None,    None,        Platform.SENSOR,         None,                               True,    False),
    Sensor("actuations",                      1,       None,        Platform.SENSOR,         None,                               True,    False),
    Sensor("burning_hours",                   1,       "h",         Platform.SENSOR,         SensorDeviceClass.DURATION,         True,    False),
    Sensor("standby_hours",                   1,       "h",         Platform.SENSOR,         SensorDeviceClass.DURATION,         True,    False),
    Sensor("fan_diagnostic",                  0.1,     None,        Platform.SENSOR,         None,                               False,   True ),
    Sensor("fan_speed",                       0.1,     "Hz",        Platform.SENSOR,         SensorDeviceClass.FREQUENCY,        True,    False),
    Sensor("pov_current",                     0.1,     "mA",        Platform.SENSOR,         SensorDeviceClass.CURRENT,          True,    False),
    Sensor("power",                           0.01,    "kcal/min",  Platform.SENSOR,         SensorDeviceClass.POWER,            True,    False),
    Sensor("water_inlet_temperature",         0.01,    "°C",        Platform.SENSOR,         SensorDeviceClass.TEMPERATURE,      True,    False),
    Sensor("water_outlet_temperature",        0.01,    "°C",        Platform.SENSOR,         SensorDeviceClass.TEMPERATURE,      True,    False),
    Sensor("water_flow",                      0.01,    "L/min",     Platform.SENSOR,         SensorDeviceClass.VOLUME_FLOW_RATE, True,    False),
    Sensor("water_flow_start",                0.01,    "L/min",     Platform.SENSOR,         SensorDeviceClass.VOLUME_FLOW_RATE, True,    False),
    Sensor("water_flow_stop",                 0.01,    "L/min",     Platform.SENSOR,         SensorDeviceClass.VOLUME_FLOW_RATE, True,    False),
    Sensor("target_temperature",              0.01,    "°C",        Platform.SENSOR,         SensorDeviceClass.TEMPERATURE,      True,    False),
    Sensor("device_ip",                       None,    None,        Platform.SENSOR,         None,                               True,    True ),
    Sensor("device_ip_priority",              None,    None,        Platform.SENSOR,         None,                               True,    True ),
    Sensor("target_temperature_raw",          1,       None,        Platform.SENSOR,         None,                               False,   True ),
    Sensor("serial_number",                   None,    None,        Platform.SENSOR,         None,                               False,   True ),
    Sensor("uptime",                          1,       "s",         Platform.SENSOR,         SensorDeviceClass.DURATION,         False,   False),
    Sensor("mac_address",                     None,    None,        Platform.SENSOR,         None,                               False,   True ),
    Sensor("wifi_signal",                     1,       "dB",        Platform.SENSOR,         SensorDeviceClass.SIGNAL_STRENGTH,  True,    True ),

    Sensor("water_usage",                     1,       "L",         Platform.SENSOR,         SensorDeviceClass.WATER,            True,    False),
    Sensor("gas_usage",                       1,       "kcal",      Platform.SENSOR,         SensorDeviceClass.ENERGY,           True,    False),
    Sensor("water_usage_last_week",           1,       "L",         Platform.SENSOR,         SensorDeviceClass.WATER,            True,    False),
    Sensor("gas_usage_last_week",             1,       "kcal",      Platform.SENSOR,         SensorDeviceClass.ENERGY,           True,    False),
]
# fmt: on

SENSORS_BUS_ARRAY = {
    "status": 0,
    "error": 1,
    "error_message": 1,  # duplicate, one is for error code another for error message
    "actuations": 3,
    "burning_hours": 4,
    "standby_hours": 5,
    "fan_diagnostic": 6,
    "fan_speed": 7,
    "pov_current": 8,
    "power": 9,
    "water_inlet_temperature": 10,
    "water_outlet_temperature": 11,
    "water_flow": 12,
    "water_flow_start": 13,
    "water_flow_stop": 14,
    "target_temperature": 15,
    "device_ip": 16,
    "device_ip_priority": 17,
    "target_temperature_raw": 18,
    "serial_number": 19,
    "uptime": 20,
    "mac_address": 25,
    "wifi_signal": 37,
}

SENSORS_TELA_ARRAY = {
    "status": 0,
    "flame": 2,
    "burning_hours": 3,
    "standby_hours": 4,
    "water_flow": 5,
    "device_ip_priority": 6,
    "target_temperature_raw": 7,
    "uptime": 8,
}

SENSORS_CONSUMO_ARRAY = {
    "water_usage": 1,
    "gas_usage": 2,
    "water_usage_last_week": 4,
    "gas_usage_last_week": 5,
}
