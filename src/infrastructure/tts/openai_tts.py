from livekit.plugins import openai
from src.config.settings import Settings
from src.core.exceptions import TTSError
from src.infrastructure.tts.abstract_tts import AbstractTTS
from src.utils.logger import create_logger

logger = create_logger("openai_tts", "INFO")

class OpenAITTS(AbstractTTS):

    def __init__(self, settings: Settings):
        self.settings = settings

    def initialize_tts(self):
        try:
            logger.info(
                "Initializing OpenAI TTS with model: %s, voice: %s",
                self.settings.TTS_MODEL,
                self.settings.TTS_VOICE
            )
            return openai.TTS(
                model=self.settings.TTS_MODEL,
                voice=self.settings.TTS_VOICE,
            )
        except Exception as e:
            logger.exception("Failed to initialize OpenAI TTS")
            raise TTSError("Failed to initialize OpenAI TTS") from e
