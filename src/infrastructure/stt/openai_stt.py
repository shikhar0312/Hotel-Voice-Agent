from livekit.plugins import openai
from src.config.settings import Settings
from src.core.exceptions import STTError
from src.infrastructure.stt.abstract_stt import AbstractSTT
from src.utils.logger import create_logger

logger = create_logger("openai_stt", "INFO")

class OpenAISTT(AbstractSTT):

    def __init__(self, settings: Settings):
        self.settings = settings

    def initialize_stt(self):
        try:
            logger.info("Initializing OpenAI STT with model: %s", self.settings.STT_MODEL)
            return openai.STT(
                model=self.settings.STT_MODEL,
            )
        except Exception as e:
            logger.exception("Failed to initialize OpenAI STT")
            raise STTError("Failed to initialize OpenAI STT") from e
