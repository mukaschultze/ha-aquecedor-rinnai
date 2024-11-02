import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, SENSORS_BUS_ARRAY, SENSORS_TELA_ARRAY, SENSORS_CONSUMO_ARRAY

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR,
             Platform.BUTTON, Platform.WATER_HEATER]
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
            raise ConfigEntryNotReady(f"Unable to fetch Rinnai device")

        hass.data[DOMAIN][entry.entry_id] = heater

        for component in PLATFORMS:
            hass.async_create_task(
                hass.config_entries.async_forward_entry_setup(entry, component)
            )

        return True
    except ConfigEntryNotReady as ex:
        raise ex
    except Exception as ex:
        _LOGGER.exception("Error setting up device", exc_info=True)
        raise ConfigEntryNotReady(
            f"Unknown error connecting to device") from ex


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(
                    entry, component)
                for component in PLATFORMS
            ]
        )
    )

    if not unload_ok:
        return False

    hass.data[DOMAIN][entry.entry_id] = None
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener, called when the config entry options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


class RinnaiHeater:

    def __init__(
        self,
        hass,
        entry: ConfigEntry
    ):
        self._hass = hass
        self._client = async_get_clientsession(hass, False)
        self._host = entry.options["host"]
        self._lock = asyncio.Lock()
        self._scan_interval = timedelta(seconds=entry.options.get(
            "scan_interval", DEFAULT_SCAN_INTERVAL))
        self._sensors = []
        self._reading = False
        self._name = entry.options["name"]

        self.data = dict()

    @callback
    async def async_add_rinnai_heater_sensor(self, update_callback):
        # This is the first sensor, set up interval.
        if not self._sensors:
            self._unsub_interval_method = async_track_time_interval(
                self._hass, self._async_refresh_data, self._scan_interval
            )

        self._sensors.append(update_callback)

    @callback
    async def async_remove_rinnai_heater_sensor(self, update_callback):
        self._sensors.remove(update_callback)

        if not self._sensors:
            """stop the interval timer upon removal of last sensor"""
            self._unsub_interval_method()
            self._unsub_interval_method = None
            await self.close()

    async def _async_refresh_data(self, now=None):
        try:
            await self.bus()
            await self.consumo()
            await self.tela()
            # await self.tela()
        except Exception as e:
            _LOGGER.exception("error reading heater data", exc_info=True)

        return True

    async def close(self):
        _LOGGER.info("closing http client")
        await self._client.close()

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
                return read.split(",")
            except Exception as e:
                _LOGGER.exception(
                    f"Error fetching /{endpoint} data", exc_info=True)
                self.data = dict()  # clear data on error so entities become unavailable
                return False
            finally:
                self._reading = False

    async def inc(self):
        return self.update_data(await self.request("inc"), SENSORS_TELA_ARRAY)

    async def dec(self):
        return self.update_data(await self.request("dec"), SENSORS_TELA_ARRAY)

    async def lig(self):
        return self.update_data(await self.request("lig"), SENSORS_TELA_ARRAY)

    async def bus(self):
        return self.update_data(await self.request("bus"), SENSORS_BUS_ARRAY)

    async def tela(self):
        return self.update_data(await self.request("tela_"), SENSORS_TELA_ARRAY)

    async def consumo(self):
        return self.update_data(await self.request("consumo"), SENSORS_CONSUMO_ARRAY)

    def update_data(self, response: list[str], sensors: dict[int, str], update_entities=True):
        if response is None or response is False:
            return False

        for address, name in sensors.items():
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
