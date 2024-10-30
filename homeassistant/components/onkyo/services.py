"""Onkyo services."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol

from homeassistant.components.media_player import DOMAIN as MEDIA_PLAYER_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN

if TYPE_CHECKING:
    from .media_player import OnkyoMediaPlayer

DATA_MP_ENTITIES: HassKey[dict[str, dict[str, OnkyoMediaPlayer]]] = HassKey(DOMAIN)

ATTR_HDMI_OUTPUT = "hdmi_output"
ACCEPTED_VALUES = [
    "no",
    "analog",
    "yes",
    "out",
    "out-sub",
    "sub",
    "hdbaset",
    "both",
    "up",
]
ONKYO_SELECT_OUTPUT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_HDMI_OUTPUT): vol.In(ACCEPTED_VALUES),
    }
)
SERVICE_SELECT_HDMI_OUTPUT = "onkyo_select_hdmi_output"

ATTR_ISCP_COMMAND = "iscp_command"
ATTR_ISCP_VALUE = "iscp_value"
ONKYO_COMMAND_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_ISCP_COMMAND): cv.string,
        vol.Required(ATTR_ISCP_VALUE): cv.string,
    }
)
SERVICE_COMMAND = "onkyo_command"


ATTR_ISCP_MESSAGE = "iscp_message"
ONKYO_MESSAGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_ISCP_MESSAGE): cv.string,
    }
)
SERVICE_MESSAGE = "onkyo_message"

async def async_register_services(hass: HomeAssistant) -> None:
    """Register Onkyo services."""

    hass.data.setdefault(DATA_MP_ENTITIES, {})

    async def async_service_handle(service: ServiceCall) -> None:
        """Handle for services."""
        entity_ids = service.data[ATTR_ENTITY_ID]

        targets: list[OnkyoMediaPlayer] = []
        for receiver_entities in hass.data[DATA_MP_ENTITIES].values():
            targets.extend(
                entity
                for entity in receiver_entities.values()
                if entity.entity_id in entity_ids
            )

        for target in targets:
            if service.service == SERVICE_SELECT_HDMI_OUTPUT:
                await target.async_select_output(service.data[ATTR_HDMI_OUTPUT])
            if service.service == SERVICE_COMMAND:
                await target.async_command(service.data[ATTR_ISCP_COMMAND], service.data[ATTR_ISCP_VALUE])
            if service.service == SERVICE_MESSAGE:
                await target.async_message(service.data[ATTR_ISCP_MESSAGE])

    hass.services.async_register(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_SELECT_HDMI_OUTPUT,
        async_service_handle,
        schema=ONKYO_SELECT_OUTPUT_SCHEMA,
    )

    hass.services.async_register(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_COMMAND,
        async_service_handle,
        schema=ONKYO_COMMAND_SCHEMA,
    )

    hass.services.async_register(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_MESSAGE,
        async_service_handle,
        schema=ONKYO_MESSAGE_SCHEMA,
    )
