import logging
from typing import Any, Dict, Optional

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    heater = hass.data[DOMAIN][entry.entry_id]
    entities = []

    priority = RinnaiHeaterPrioritySwitch(heater)
    entities.append(priority)

    async_add_entities(entities)
    return True


class RinnaiHeaterPrioritySwitch(SwitchEntity):
    def __init__(self, heater):
        self._heater = heater
        self._key = "device_ip_priority"

        self._attr_has_entity_name = True
        self._attr_unique_id = "priority"
        self._attr_translation_key = self._attr_unique_id

    @property
    def is_on(self):
        if self._key not in self._heater.data:
            return False

        return self._heater.data[self._key] != "null:pri"

    async def async_turn_on(self, **kwargs):
        await self._heater.prioridade(True)
        await self._heater.bus()

    async def async_turn_off(self, **kwargs):
        await self._heater.prioridade(False)
        await self._heater.bus()

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        return self._heater._device_info()

    @property
    def available(self) -> Optional[Dict[str, Any]]:
        return self._key in self._heater.data
