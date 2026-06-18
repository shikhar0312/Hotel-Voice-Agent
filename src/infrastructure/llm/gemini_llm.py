from livekit.plugins import google
from src.config.settings import Settings
from src.core.exceptions import LLMError
from src.infrastructure.llm.abstract_llm import AbstractLLM
from src.utils.logger import create_logger

logger = create_logger("gemini_llm", "INFO")


class GeminiLLM(AbstractLLM):

    def __init__(self, settings: Settings):
        self.settings = settings

    def initialize_llm(self):
        try:
            logger.info(
                "Initializing Gemini LLM with model: %s, temperature: %s",
                self.settings.LLM_MODEL,
                self.settings.LLM_TEMPERATURE,
            )
            return google.LLM(
                model=self.settings.LLM_MODEL,
                temperature=self.settings.LLM_TEMPERATURE,
                api_key=self.settings.GOOGLE_API_KEY,
            )
        except Exception as e:
            logger.exception("Failed to initialize Gemini LLM")
            raise LLMError("Failed to initialize Gemini LLM") from e
