import logging
import re
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import BinarySensorEntity, EntityCategory
from homeassistant.const import Platform
from homeassistant.core import callback

from .const import DOMAIN, SENSORS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    heater = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for sensor_info in SENSORS:
        if sensor_info.platform == Platform.BINARY_SENSOR:
            sensor = RinnaiHeaterBinarySensor(heater, sensor_info)
            entities.append(sensor)

    async_add_entities(entities)
    return True


class RinnaiHeaterBinarySensor(BinarySensorEntity):
    def __init__(self, heater, sensor_info):
        """Initialize the sensor."""
        self._heater = heater
        self._key = sensor_info.name

        self._attr_has_entity_name = True
        self._attr_unique_id = self._key
        self._attr_translation_key = self._attr_unique_id
        self._attr_device_class = sensor_info.device_class
        self._attr_entity_registry_enabled_default = sensor_info.enabled
        self._attr_entity_category = EntityCategory.DIAGNOSTIC if sensor_info.debug else None

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
    def is_on(self):
        if self._key in self._heater.data:
            return self._heater.data[self._key] == "1"

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._heater._device_info()

    @property
    def available(self) -> Optional[Dict[str, Any]]:
        return self._key in self._heater.data
