from typing import Dict
from src.config.settings import Settings
from src.infrastructure.vad.silero_vad import SileroVAD
from src.utils.logger import create_logger

logger = create_logger("vad_factory", "INFO")

class VADFactory:

    _instances: Dict[str, object] = {}

    @classmethod
    def get_loaded_vad(cls, settings: Settings):
        provider = settings.SELECTED_VAD

        if provider in cls._instances:
            logger.debug("Reusing cached VAD provider: %s", provider)
            return cls._instances[provider]

        logger.info("Loading VAD provider: %s", provider)

        if provider == "silero":
            vad = SileroVAD(settings).initialize_vad()

        else:
            raise ValueError(f"Unsupported VAD provider: {provider}")

        cls._instances[provider] = vad
        return vad
