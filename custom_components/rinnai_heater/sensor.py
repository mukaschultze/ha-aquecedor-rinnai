import logging
import re
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, EntityCategory, SensorStateClass, SensorDeviceClass
from homeassistant.const import Platform
from homeassistant.core import callback

from .const import DOMAIN, SENSORS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    heater = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for sensor_info in SENSORS:
        if sensor_info.platform == Platform.SENSOR:
            sensor = RinnaiHeaterSensor(heater, sensor_info)
            entities.append(sensor)

    async_add_entities(entities)
    return True


class RinnaiHeaterSensor(SensorEntity):
    def __init__(self, heater, sensor_info):
        """Initialize the sensor."""
        self._heater = heater
        self._key = sensor_info.name
        self._coeff = sensor_info.coeff

        self._attr_has_entity_name = True
        self._attr_unique_id = self._key
        self._attr_translation_key = self._attr_unique_id
        self._attr_native_unit_of_measurement = sensor_info.unit
        self._attr_device_class = sensor_info.device_class
        self._attr_entity_registry_enabled_default = sensor_info.enabled
        self._attr_icon = sensor_info.icon
        self._attr_options = sensor_info.options
        self._attr_entity_category = EntityCategory.DIAGNOSTIC if sensor_info.debug else None

        if self._coeff is not None:
            if self._attr_device_class == SensorDeviceClass.WATER or self._attr_device_class == SensorDeviceClass.ENERGY:
                self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            else:
                self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_suggested_display_precision = str(
                self._coeff).count('0')

    async def async_added_to_hass(self):
        await self._heater.async_add_rinnai_heater_sensor(
            self._heater_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        await self._heater.async_remove_rinnai_heater_sensor(
            self._heater_data_updated)

    @callback
    def _heater_data_updated(self):
        self.async_write_ha_state()

    @property
    def state(self):
        if self._key in self._heater.data:
            if self._attr_options is not None:
                return self._attr_options[self._heater.data[self._key]]
            elif self._coeff is None:
                return self._heater.data[self._key]
            else:
                return float(self._heater.data[self._key]) * self._coeff

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._heater._device_info()

    @property
    def available(self) -> Optional[Dict[str, Any]]:
        return self._key in self._heater.data
