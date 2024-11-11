import logging
from collections.abc import Mapping

import voluptuous as vol
from typing import Any
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
)

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL_BUS, DEFAULT_SCAN_INTERVAL_TELA, DEFAULT_SCAN_INTERVAL_CONSUMO

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    vol.Required("name"): str,
    vol.Required("host", default="WIFI-RINNAI"): str,
    vol.Required("scan_interval_bus", default=DEFAULT_SCAN_INTERVAL_BUS): vol.Coerce(float),
    vol.Required("scan_interval_tela", default=DEFAULT_SCAN_INTERVAL_TELA): vol.Coerce(float),
    vol.Required("scan_interval_consumo", default=DEFAULT_SCAN_INTERVAL_CONSUMO): vol.Coerce(float),
})

CONFIG_FLOW = {
    "user": SchemaFlowFormStep(schema=CONFIG_SCHEMA),
}

OPTIONS_FLOW = {
    "init": CONFIG_FLOW["user"],
    **CONFIG_FLOW,
}


class RinnaiHeaterConfigFlow(SchemaConfigFlowHandler, domain=DOMAIN):
    config_flow = CONFIG_FLOW
    options_flow = OPTIONS_FLOW

    def async_config_entry_title(self, options: Mapping[str, Any]) -> str:
        """Return config entry title."""
        return options.get("name")
