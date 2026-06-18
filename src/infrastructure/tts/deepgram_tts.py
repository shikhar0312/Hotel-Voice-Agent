from livekit.plugins import deepgram
from src.config.settings import Settings
from src.core.exceptions import TTSError
from src.infrastructure.tts.abstract_tts import AbstractTTS
from src.utils.logger import create_logger

logger = create_logger("deepgram_tts", "INFO")

class DeepgramTTS(AbstractTTS):

    def __init__(self, settings: Settings):
        self.settings = settings

    def initialize_tts(self):
        try:
            model = getattr(self.settings, "DEEPGRAM_TTS_MODEL", "aura-asteria-en")

            logger.info(
                "Initializing Deepgram TTS with model: %s", model
            )

            return deepgram.TTS(
                model=model,
                api_key=self.settings.DEEPGRAM_API_KEY,
            )
        except Exception as e:
            logger.exception("Failed to initialize Deepgram TTS")
            raise TTSError("Failed to initialize Deepgram TTS") from e
