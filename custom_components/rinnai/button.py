import logging
import re
from typing import Any, Dict, Optional

from homeassistant.components.button import ButtonEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    heater = hass.data[DOMAIN][entry.entry_id]
    entities = []

    inc = RinnaiHeaterTemperatureButton(heater, True)
    entities.append(inc)

    dec = RinnaiHeaterTemperatureButton(heater, False)
    entities.append(dec)

    async_add_entities(entities)
    return True


class RinnaiHeaterTemperatureButton(ButtonEntity):
    def __init__(self, heater, increase):
        self._heater = heater
        self._increase = increase

        self._attr_has_entity_name = True
        self._attr_unique_id = (
            "temperature_increase" if increase else "temperature_decrease"
        )
        self._attr_translation_key = self._attr_unique_id

    async def async_press(self):
        if self._heater._auto_priority:
            await self._heater.prioridade(True)

        if self._increase:
            await self._heater.inc()
        else:
            await self._heater.dec()

        if self._heater._auto_priority:
            await self._heater.prioridade(False)

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._heater._device_info()

    @property
    def available(self) -> Optional[Dict[str, Any]]:
        return True
