'''import requests

class OpenAITTSEngine:

    def __init__(self, api_key: str, voice: str, model: str, speed: int, url: str):
        self._api_key = api_key
        self._voice = voice
        self._model = model
        self._speed = speed
        self._url = url

    def get_tts(self, text: str):
        """ Makes request to OpenAI TTS engine to convert text into audio"""
        headers: dict = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
        data: dict = {
            "model": self._model,
            "input": text,
            "voice": self._voice,
            "response_format": "wav",
            "speed": self._speed
        }
        return requests.post(self._url, headers=headers, json=data)

    @staticmethod
    def get_supported_langs() -> list:
        """Returns list of supported languages. Note: the model determines the provides language automatically."""
        return ["af", "ar", "hy", "az", "be", "bs", "bg", "ca", "zh", "hr", "cs", "da", "nl", "en", "et", "fi", "fr", "gl", "de", "el", "he", "hi", "hu", "is", "id", "it", "ja", "kn", "kk", "ko", "lv", "lt", "mk", "ms", "mr", "mi", "ne", "no", "fa", "pl", "pt", "ro", "ru", "sr", "sk", "sl", "es", "sw", "sv", "tl", "ta", "th", "tr", "uk", "ur", "vi", "cy"]
'''
import asyncio
import websockets
import ormsgpack

class FishAudioTTSEngine:
    def __init__(self, api_key: str, voice: str, url: str):
        self._api_key = api_key
        self._voice = voice
        self._url = url

    async def get_tts(self, text: str):
        """ Streams text to Fish.audio TTS and retrieves audio in real time via WebSocket """
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}

        async with websockets.connect(self._url, extra_headers=headers) as ws:
            # Send start event
            await ws.send(
                ormsgpack.packb(
                    {
                        "event": "start",
                        "request": {
                            "text": "",
                            "latency": "normal",
                            "format": "opus",
                            "prosody": {"speed": 1.0, "volume": 0},
                            "reference_id": self._voice,
                        },
                    }
                )
            )

            # Send text
            await ws.send(ormsgpack.packb({"event": "text", "text": text}))

            # Flush buffer to generate audio
            await ws.send(ormsgpack.packb({"event": "flush"}))

            # Collect audio response
            audio_data = b""
            while True:
                message = await ws.recv()
                response = ormsgpack.unpackb(message)

                if response["event"] == "audio":
                    audio_data += response["audio"]
                elif response["event"] in ["stop", "finish"]:
                    break

            return audio_data

    @staticmethod
    def get_supported_langs() -> list:
        """Returns list of supported languages (Fish.audio auto-detects language)."""
        return ["en", "es", "fr", "de", "it", "zh", "hi", "ar", "ru", "ja", "pt", "ko"]

