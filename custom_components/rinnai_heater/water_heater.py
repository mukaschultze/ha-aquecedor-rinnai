import logging
import re
from typing import Any, Dict, Optional

from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityFeature, STATE_GAS, STATE_OFF
from homeassistant.const import UnitOfTemperature, PRECISION_WHOLE
from homeassistant.core import callback

from .const import DOMAIN, TEMPERATURES_MAP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    heater = hass.data[DOMAIN][entry.entry_id]
    entities = []

    sensor = RinnaiHeaterWaterHeater(heater)
    entities.append(sensor)

    async_add_entities(entities)
    return True


class RinnaiHeaterWaterHeater(WaterHeaterEntity):
    def __init__(self, heater):
        self._heater = heater

        self._attr_has_entity_name = True
        self._attr_unique_id = "heater"
        self._attr_translation_key = self._attr_unique_id

        self._attr_min_temp = 35
        self._attr_max_temp = 60
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_operation_list = [STATE_GAS, STATE_OFF]
        self._attr_supported_features = WaterHeaterEntityFeature.OPERATION_MODE | WaterHeaterEntityFeature.TARGET_TEMPERATURE

    async def async_added_to_hass(self):
        await self._heater.async_add_rinnai_heater_sensor(
            self._heater_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        await self._heater.async_remove_rinnai_heater_sensor(
            self._heater_data_updated)

    @callback
    def _heater_data_updated(self):
        self.schedule_update_ha_state()

    @property
    def current_temperature(self):
        if "water_outlet_temperature" in self._heater.data:
            return float(self._heater.data["water_outlet_temperature"]) * 0.01

    @property
    def target_temperature(self):
        if "target_temperature_raw" in self._heater.data:
            return TEMPERATURES_MAP[self._heater.data["target_temperature_raw"]] * 0.01

    @property
    def is_on(self):
        return self._heater.data["status"] != "11"

    @property
    def current_operation(self):
        return STATE_GAS if self.is_on else STATE_OFF

    async def async_set_temperature(self, **kwargs: Any):
        _LOGGER.debug(f"async_set_temperature: {kwargs}")

        temperature = kwargs.get("temperature") * 100

        nearest_temperature = min(
            TEMPERATURES_MAP.values(), key=lambda x: abs(x - temperature))
        nearest_temperature_index = list(
            TEMPERATURES_MAP.values()).index(nearest_temperature)

        current_temperature = self.target_temperature * 100
        current_temperature_index = list(
            TEMPERATURES_MAP.values()).index(current_temperature)

        steps = nearest_temperature_index - current_temperature_index

        _LOGGER.debug(f"async_set_temperature: {temperature} -> {nearest_temperature}/{
                      nearest_temperature_index} - {current_temperature}/{current_temperature_index} - {steps}")

        for i in range(abs(steps)):
            if steps > 0:
                await self._heater.inc()
            else:
                await self._heater.dec()

    async def async_set_operation_mode(self, mode):
        if mode == STATE_GAS:
            await self.async_turn_on()
        elif mode == STATE_OFF:
            await self.async_turn_off()

    async def async_turn_on(self):
        if not self.is_on:
            await self._heater.lig()

    async def async_turn_off(self):
        if self.is_on:
            await self._heater.lig()

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._heater._device_info()

    @property
    def available(self) -> Optional[Dict[str, Any]]:
        return True
