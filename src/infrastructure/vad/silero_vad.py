from livekit.plugins import silero
from src.config.settings import Settings
from src.core.exceptions import VADError
from src.infrastructure.vad.abstract_vad import AbstractVAD
from src.utils.logger import create_logger

logger = create_logger("silero_vad", "INFO")

class SileroVAD(AbstractVAD):

    def __init__(self, settings: Settings):
        self.settings = settings

    def initialize_vad(self):
        try:
            logger.info("Loading Silero VAD model")
            return silero.VAD.load()
        except Exception as e:
            logger.exception("Failed to load Silero VAD")
            raise VADError("Failed to load Silero VAD") from e
