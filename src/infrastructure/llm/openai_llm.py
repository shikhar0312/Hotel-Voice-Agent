from livekit.plugins import openai
from src.config.settings import Settings
from src.core.exceptions import LLMError
from src.infrastructure.llm.abstract_llm import AbstractLLM
from src.utils.logger import create_logger

logger = create_logger("openai_llm", "INFO")

class OpenAILLM(AbstractLLM):

    def __init__(self, settings: Settings):
        self.settings = settings

    def initialize_llm(self):
        try:
            logger.info(
                "Initializing OpenAI LLM with model: %s, temperature: %s",
                self.settings.LLM_MODEL,
                self.settings.LLM_TEMPERATURE
            )
            return openai.LLM(
                model=self.settings.LLM_MODEL,
                temperature=self.settings.LLM_TEMPERATURE,
            )
        except Exception as e:
            logger.exception("Failed to initialize OpenAI LLM")
            raise LLMError("Failed to initialize OpenAI LLM") from e
