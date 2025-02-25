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
    # Generate a unique ID based on user input.
    url = urlparse(user_input[CONF_URL])
    return f"{url.hostname}_{user_input[CONF_VOICE]}"

async def validate_user_input(user_input: dict):
    # Validate user input fields.
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

class FishAudioTTSConfigFlow(ConfigFlow, domain="fish_tts"):
    // Handle a config flow for Fish.audio TTS.
    VERSION = 1
    data_schema = vol.Schema({
        vol.Optional(CONF_API_KEY): str,  # API Key is optional
        vol.Required(CONF_URL, default="wss://api.fish.audio/v1/tts/live"): str,
        vol.Required(CONF_VOICE, default="default-voice"): str
    })

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        // Handle the initial step.
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
"""
import asyncio
import websockets
import ormsgpack
import logging
from typing import Any
from urllib.parse import urlparse
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
    
    try:
        # WebSocket connection with authorization header
        uri = user_input[CONF_URL]
        headers = {"Authorization": f"Bearer {user_input[CONF_API_KEY]}"}

        async with websockets.connect(uri, extra_headers=headers) as ws:
            # Send "start" event to initiate TTS session
            start_message = {
                "event": "start",
                "request": {
                    "text": "",
                    "latency": "normal",  # or "balanced"
                    "format": "opus",  # audio format
                    "prosody": {"speed": 1.0, "volume": 0},  # Optional prosody
                    "reference_id": user_input[CONF_VOICE],
                },
                "debug": True,  # Optional, can help in debugging
            }
            await ws.send(ormsgpack.packb(start_message))
            response = await ws.recv()
            _LOGGER.debug(f"WebSocket test response: {response}")
            
            # Additional connection check or logging if needed
            _LOGGER.info("WebSocket connection established and TTS session started.")

    except websockets.exceptions.WebSocketException as e:
        raise ValueError(f"WebSocket connection failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error occurred while validating connection: {str(e)}")

class FishAudioTTSConfigFlow(ConfigFlow, domain="fish_tts"):
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


