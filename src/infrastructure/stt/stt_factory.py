from typing import Dict
from src.config.settings import Settings
from src.infrastructure.stt.deepgram_stt import DeepgramSTT
from src.infrastructure.stt.elevenlabs_stt import ElevenLabsSTT
from src.infrastructure.stt.openai_stt import OpenAISTT
from src.utils.logger import create_logger

logger = create_logger("stt_factory", "INFO")

class STTFactory:

    _instances: Dict[str, object] = {}

    @classmethod
    def get_initialized_stt(cls, settings: Settings):
        provider = settings.SELECTED_STT

        if provider in cls._instances:
            logger.debug("Reusing cached STT provider: %s", provider)
            return cls._instances[provider]

        logger.info("Initializing STT provider: %s", provider)

        if provider == "deepgram":
            stt = DeepgramSTT(settings).initialize_stt()

        elif provider == "openai":
            stt = OpenAISTT(settings).initialize_stt()

        elif provider == "elevenlabs":
            stt = ElevenLabsSTT(settings).initialize_stt()

        else:
            raise ValueError(f"Unsupported STT provider: {provider}")

        cls._instances[provider] = stt
        return stt
