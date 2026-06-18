from livekit.plugins import google
from src.config.settings import Settings
from src.core.exceptions import TTSError
from src.infrastructure.tts.abstract_tts import AbstractTTS
from src.utils.logger import create_logger

logger = create_logger("google_tts", "INFO")

class GoogleTTS(AbstractTTS):

    def __init__(self, settings: Settings):
        self.settings = settings

    def initialize_tts(self):
        try:
            voice = getattr(self.settings, "GOOGLE_TTS_VOICE", "en-US-Journey-F")
            language = getattr(self.settings, "GOOGLE_TTS_LANGUAGE", "en-US")

            logger.info(
                "Initializing Google TTS with voice: %s, language: %s",
                voice, language
            )

            return google.TTS(
                voice_name=voice,
                language=language,
            )
        except Exception as e:
            logger.exception("Failed to initialize Google TTS")
            raise TTSError("Failed to initialize Google TTS") from e
