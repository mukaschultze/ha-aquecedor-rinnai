import asyncio
import logging
import aiohttp
import time

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr
from homeassistant.const import CONF_HOST

from .const import (
    DOMAIN,
    PRIORITY_DISCRIMINATOR,
    SENSORS_BUS_ARRAY,
    SENSORS_TELA_ARRAY,
    SENSORS_CONSUMO_ARRAY,
    CONF_AUTO_PRIORITY,
    CONF_SCAN_INTERVAL_BUS,
    CONF_SCAN_INTERVAL_TELA,
    CONF_SCAN_INTERVAL_CONSUMO,
    DEFAULT_AUTO_PRIORITY,
    DEFAULT_SCAN_INTERVAL_BUS,
    DEFAULT_SCAN_INTERVAL_TELA,
    DEFAULT_SCAN_INTERVAL_CONSUMO,
)

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    hass.data[DOMAIN] = {}
    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    try:
        entry.async_on_unload(entry.add_update_listener(async_reload_entry))

        heater = RinnaiHeater(hass, entry)

        successReading = await heater.bus()

        if not successReading:
            raise ConfigEntryNotReady("Unable to fetch Rinnai device")

        hass.data[DOMAIN][entry.entry_id] = heater

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        return True
    except ConfigEntryNotReady as ex:
        raise ex
    except Exception as ex:
        _LOGGER.exception("Error setting up device", exc_info=True)
        raise ConfigEntryNotReady("Unknown error connecting to device") from ex


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if not unload_ok:
        return False

    hass.data[DOMAIN][entry.entry_id] = None
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


class RinnaiHeater:
    def __init__(self, hass, entry: ConfigEntry):
        self._hass = hass
        self._entry = entry
        self._client = async_get_clientsession(hass, False)
        self._host = entry.data[CONF_HOST]
        self._lock = asyncio.Lock()

        self._sensors = []
        self._reading = False
        self._name = entry.title
        self._auto_priority = entry.data.get(CONF_AUTO_PRIORITY, DEFAULT_AUTO_PRIORITY)

        self.data = {}

        self._last_success = time.time()
        self._timeout = 0

    @callback
    async def async_add_rinnai_heater_sensor(self, update_callback):
        # This is the first sensor, set up interval.
        if not self._sensors:
            scan_interval_bus = self._entry.data.get(CONF_SCAN_INTERVAL_BUS, DEFAULT_SCAN_INTERVAL_BUS)
            scan_interval_tela = self._entry.data.get(CONF_SCAN_INTERVAL_TELA, DEFAULT_SCAN_INTERVAL_TELA)
            scan_interval_consumo = self._entry.data.get(CONF_SCAN_INTERVAL_CONSUMO, DEFAULT_SCAN_INTERVAL_CONSUMO)
            self._timeout = max(scan_interval_bus, scan_interval_tela) * 4

            a = (
                async_track_time_interval(self._hass, self.bus, timedelta(seconds=scan_interval_bus))
                if scan_interval_bus > 0
                else lambda: None
            )
            b = (
                async_track_time_interval(self._hass, self.tela, timedelta(seconds=scan_interval_tela))
                if scan_interval_tela > 0
                else lambda: None
            )
            c = (
                async_track_time_interval(self._hass, self.consumo, timedelta(seconds=scan_interval_consumo))
                if scan_interval_consumo > 0
                else lambda: None
            )

            self._unsub_interval_method = lambda: (a(), b(), c())

        self._sensors.append(update_callback)

    @callback
    async def async_remove_rinnai_heater_sensor(self, update_callback):
        self._sensors.remove(update_callback)

        if not self._sensors:
            """stop the interval timer upon removal of last sensor"""
            self._unsub_interval_method()
            self._unsub_interval_method = None

    async def request(self, endpoint: str):
        # if self._reading:
        #     _LOGGER.warning(
        #         f"skipping fetching /{endpoint} data, previous read still in progress, make sure your scan interval is not too low")
        #     return None
        # else:
        #     self._reading = True

        _LOGGER.debug(f"requesting /{endpoint}")

        async with self._lock:
            try:
                res = await self._client.get(f"http://{self._host}/{endpoint}")
                read = await res.text()
                self._last_success = time.time()
                return read.split(",")
            except aiohttp.client_exceptions.ServerDisconnectedError:
                return True  # not even an empty response, the priority endpoint simply closes the TCP connection
            except aiohttp.client_exceptions.ClientConnectorError:
                return False
            except aiohttp.client_exceptions.ServerTimeoutError:
                return False
            except Exception:
                _LOGGER.exception(f"Error fetching /{endpoint} data", exc_info=True)
                return False
            finally:
                self._reading = False

    def is_connected(self):
        return time.time() - self._last_success < self._timeout
    
    async def inc(self):
        return self.update_data(await self.request("inc"), SENSORS_TELA_ARRAY)

    async def dec(self):
        return self.update_data(await self.request("dec"), SENSORS_TELA_ARRAY)

    async def lig(self):
        return self.update_data(await self.request("lig"), SENSORS_TELA_ARRAY)

    async def bus(self, now=None):
        return self.update_data(await self.request("bus"), SENSORS_BUS_ARRAY)

    async def tela(self, now=None):
        return self.update_data(await self.request("tela_"), SENSORS_TELA_ARRAY)

    async def consumo(self, now=None):
        return self.update_data(await self.request("consumo"), SENSORS_CONSUMO_ARRAY)

    async def prioridade(self, set: bool):
        priority = PRIORITY_DISCRIMINATOR if set else "null"
        return await self.request(f"ip:{priority}:pri")

    def update_data(self, response: list[str], sensors: dict[int, str], update_entities=True):
        if response is None or response is False:
            return False
    
        response = response or {}

        for name, address in sensors.items():
            self.data[name] = response[address]

        if update_entities:
            for update_callback in self._sensors:
                update_callback()

        return True

    def _device_info(self):
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self.data["mac_address"])},
            "identifiers": {(DOMAIN, self.data["serial_number"])},
            "name": self._name,
            "model": self._name,
            "manufacturer": "Rinnai",
            "serial_number": self.data["serial_number"],
        }
