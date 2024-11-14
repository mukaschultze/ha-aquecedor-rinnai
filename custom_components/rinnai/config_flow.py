from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.components import dhcp, zeroconf
from typing import Any
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv
from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_HOST,
    DEFAULT_SCAN_INTERVAL_BUS,
    DEFAULT_SCAN_INTERVAL_CONSUMO,
    DEFAULT_SCAN_INTERVAL_TELA,
    CONF_SCAN_INTERVAL_BUS,
    CONF_SCAN_INTERVAL_CONSUMO,
    CONF_SCAN_INTERVAL_TELA,
)

import voluptuous as vol
import logging

_LOGGER = logging.getLogger(__name__)


async def async_try_get_serial(hass: HomeAssistant, ip_address: str) -> str:
    try:
        client = async_get_clientsession(hass, False)
        res = await client.get(f"http://{ip_address}/bus")
        read = await res.text()
        data = read.split(",")
        return data[19]
    except Exception as ex:
        raise CannotConnect from ex


HOST_SCHEMA = vol.Schema({vol.Required(CONF_HOST, default=DEFAULT_HOST): str})

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Optional(
            CONF_SCAN_INTERVAL_BUS, default=DEFAULT_SCAN_INTERVAL_BUS
        ): vol.Coerce(float),
        vol.Optional(
            CONF_SCAN_INTERVAL_TELA, default=DEFAULT_SCAN_INTERVAL_TELA
        ): vol.Coerce(float),
        vol.Optional(
            CONF_SCAN_INTERVAL_CONSUMO, default=DEFAULT_SCAN_INTERVAL_CONSUMO
        ): vol.Coerce(float),
    }
)

RECONFIGURE_SCHEMA = HOST_SCHEMA.extend(CONFIG_SCHEMA.schema)


class RinnaiHeaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    async def async_set_serial_number(self, host: str):
        serial_number = await async_try_get_serial(self.hass, host)
        self.host = host
        await self.async_set_unique_id(serial_number)
        if self.source == config_entries.SOURCE_RECONFIGURE:
            self._abort_if_unique_id_mismatch()
        else:
            self._abort_if_unique_id_configured(updates={CONF_HOST: host})

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors = {}

        if user_input is not None:
            try:
                await self.async_set_serial_number(user_input[CONF_HOST])
                return await self.async_step_config()
            except CannotConnect:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=HOST_SCHEMA, errors=errors
        )

    async def async_step_config(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME], data={CONF_HOST: self.host, **user_input}
            )

        return self.async_show_form(step_id="config", data_schema=CONFIG_SCHEMA)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        errors = {}

        if user_input is not None:
            try:
                await self.async_set_serial_number(user_input[CONF_HOST])
                return self.async_update_reload_and_abort(
                    self._get_reconfigure_entry(),
                    title=user_input[CONF_NAME],
                    data_updates=user_input,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"

        reconfigure_entry = self._get_reconfigure_entry()

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                RECONFIGURE_SCHEMA, reconfigure_entry.data
            ),
            errors=errors,
            description_placeholders={"device_name": reconfigure_entry.title},
        )

    async def async_step_zeroconf(self, discovery_info: zeroconf.ZeroconfServiceInfo):
        try:
            await self.async_set_serial_number(discovery_info.host)
            return await self.async_step_config()
        except CannotConnect:
            return self.async_abort(reason="cannot_connect")

    async def async_step_dhcp(self, discovery_info: dhcp.DhcpServiceInfo):
        try:
            await self.async_set_serial_number(discovery_info.ip)
            return await self.async_step_config()
        except CannotConnect:
            return self.async_abort(reason="cannot_connect")


class CannotConnect(Exception):
    """Exception to raise when we cannot connect."""
