"""Config flow for OpenAI text-to-speech custom component."""
"""from __future__ import annotations
from typing import Any
import voluptuous as vol
import logging
from urllib.parse import urlparse

from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.selector import selector
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_API_KEY, CONF_MODEL, CONF_VOICE, CONF_SPEED, CONF_URL, DOMAIN, MODELS, VOICES, UNIQUE_ID

_LOGGER = logging.getLogger(__name__)

def generate_unique_id(user_input: dict) -> str:
    Generate a unique id from user input."""
    url = urlparse(user_input[CONF_URL])
    return f"{url.hostname}_{user_input[CONF_MODEL]}_{user_input[CONF_VOICE]}"

"""async def validate_user_input(user_input: dict):
    //Validate user input fields.
    if user_input.get(CONF_MODEL) is None:
        raise ValueError("Model is required")
    if user_input.get(CONF_VOICE) is None:
        raise ValueError("Voice is required")

class OpenAITTSConfigFlow(ConfigFlow, domain=DOMAIN):
    //Handle a config flow for OpenAI TTS.
    data_schema = vol.Schema({
        vol.Optional(CONF_API_KEY): str,
        vol.Optional(CONF_URL, default="https://api.openai.com/v1/audio/speech"): str,
        vol.Optional(CONF_SPEED, default=1.0): vol.Coerce(float),
        vol.Required(CONF_MODEL, default="tts-1"): selector({
            "select": {
                "options": MODELS,
                "mode": "dropdown",
                "sort": True,
                "custom_value": True
            }
        }),
        vol.Required(CONF_VOICE, default="shimmer"): selector({
            "select": {
                "options": VOICES,
                "mode": "dropdown",
                "sort": True,
                "custom_value": True
            }
        })
    })

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        //Handle the initial step.
        errors = {}
        if user_input is not None:
            try:
                await validate_user_input(user_input)
                unique_id = generate_unique_id(user_input)
                user_input[UNIQUE_ID] = unique_id
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                hostname = urlparse(user_input[CONF_URL]).hostname
                return self.async_create_entry(title=f"OpenAI TTS ({hostname}, {user_input[CONF_MODEL]}, {user_input[CONF_VOICE]})", data=user_input)
            except data_entry_flow.AbortFlow:
                return self.async_abort(reason="already_configured")
            except HomeAssistantError as e:
                _LOGGER.exception(str(e))
                errors["base"] = str(e)
            except ValueError as e:
                _LOGGER.exception(str(e))
                errors["base"] = str(e)
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception(str(e))
                errors["base"] = "unknown_error"
        return self.async_show_form(step_id="user", data_schema=self.data_schema, errors=errors, description_placeholders=user_input) 
"""
from __future__ import annotations
from typing import Any
import voluptuous as vol
import logging
from urllib.parse import urlparse
import websockets

from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigFlow
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_API_KEY, CONF_VOICE, CONF_URL, DOMAIN, UNIQUE_ID

_LOGGER = logging.getLogger(__name__)

def generate_unique_id(user_input: dict) -> str:
    """Generate a unique ID based on user input."""
    url = urlparse(user_input[CONF_URL])
    return f"{url.hostname}_{user_input[CONF_VOICE]}"

async def validate_user_input(user_input: dict):
    """Validate user input fields."""
    if not user_input.get(CONF_VOICE):
        raise ValueError("Voice is required")
    
    # Check WebSocket connectivity
    try:
        async with websockets.connect(user_input[CONF_URL]) as ws:
            await ws.send('{"event": "log", "message": "Test Connection"}')
            response = await ws.recv()
            _LOGGER.debug(f"WebSocket test response: {response}")
    except Exception as e:
        raise ValueError(f"WebSocket connection failed: {str(e)}")

class FishAudioTTSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fish.audio TTS."""
    VERSION = 1
    data_schema = vol.Schema({
        vol.Optional(CONF_API_KEY): str,  # API Key is optional
        vol.Required(CONF_URL, default="wss://api.fish.audio/v1/tts/live"): str,
        vol.Required(CONF_VOICE, default="default-voice"): str
    })

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                await validate_user_input(user_input)
                unique_id = generate_unique_id(user_input)
                user_input[UNIQUE_ID] = unique_id
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                hostname = urlparse(user_input[CONF_URL]).hostname
                return self.async_create_entry(
                    title=f"Fish.audio TTS ({hostname}, {user_input[CONF_VOICE]})", 
                    data=user_input
                )
            except data_entry_flow.AbortFlow:
                return self.async_abort(reason="already_configured")
            except HomeAssistantError as e:
                _LOGGER.exception(str(e))
                errors["base"] = str(e)
            except ValueError as e:
                _LOGGER.error(str(e))
                errors["base"] = str(e)
            except Exception as e:
                _LOGGER.exception(str(e))
                errors["base"] = "unknown_error"
                
        return self.async_show_form(step_id="user", data_schema=self.data_schema, errors=errors, description_placeholders=user_input)
