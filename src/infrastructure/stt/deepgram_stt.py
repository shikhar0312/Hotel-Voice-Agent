from livekit.plugins import deepgram
from src.config.settings import Settings
from src.core.exceptions import STTError
from src.infrastructure.stt.abstract_stt import AbstractSTT
from src.utils.logger import create_logger

logger = create_logger("deepgram_stt", "INFO")

class DeepgramSTT(AbstractSTT):

    def __init__(self, settings: Settings):
        self.settings = settings

    def initialize_stt(self):
        try:
            logger.info("Initializing Deepgram STT with model: %s", self.settings.DEEPGRAM_STT_MODEL)
            return deepgram.STT(
                model=self.settings.DEEPGRAM_STT_MODEL,
                language="en",
            )
        except Exception as e:
            logger.exception("Failed to initialize Deepgram STT")
            raise STTError("Failed to initialize Deepgram STT") from e
