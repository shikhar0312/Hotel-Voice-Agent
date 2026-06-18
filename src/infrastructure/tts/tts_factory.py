from typing import Dict
from src.config.settings import Settings
from src.infrastructure.tts.elevenlabs_tts import ElevenLabsTTS
from src.infrastructure.tts.openai_tts import OpenAITTS
from src.infrastructure.tts.google_tts import GoogleTTS
from src.infrastructure.tts.deepgram_tts import DeepgramTTS
from src.utils.logger import create_logger

logger = create_logger("tts_factory", "INFO")

class TTSFactory:

    _instances: Dict[str, object] = {}

    @classmethod
    def get_initialized_tts(cls, settings: Settings):
        provider = settings.SELECTED_TTS

        if provider in cls._instances:
            logger.debug("Reusing cached TTS provider: %s", provider)
            return cls._instances[provider]

        logger.info("Initializing TTS provider: %s", provider)

        if provider == "openai":
            tts = OpenAITTS(settings).initialize_tts()

        elif provider == "elevenlabs":
            tts = ElevenLabsTTS(settings).initialize_tts()

        elif provider == "google":
            tts = GoogleTTS(settings).initialize_tts()

        elif provider == "deepgram":
            tts = DeepgramTTS(settings).initialize_tts()

        else:
            raise ValueError(f"Unsupported TTS provider: {provider}")

        cls._instances[provider] = tts
        return tts
