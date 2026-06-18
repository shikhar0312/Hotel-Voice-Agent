from typing import Dict
from src.config.settings import Settings
from src.infrastructure.llm.gemini_llm import GeminiLLM
from src.infrastructure.llm.openai_llm import OpenAILLM
from src.utils.logger import create_logger

logger = create_logger("llm_factory", "INFO")

class LLMFactory:

    _instances: Dict[str, object] = {}

    @classmethod
    def get_initialized_llm(cls, settings: Settings):
        provider = settings.SELECTED_LLM

        if provider in cls._instances:
            logger.debug("Reusing cached LLM provider: %s", provider)
            return cls._instances[provider]

        logger.info("Initializing LLM provider: %s", provider)

        if provider == "openai":
            llm = OpenAILLM(settings).initialize_llm()

        elif provider == "gemini":
            llm = GeminiLLM(settings).initialize_llm()

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        cls._instances[provider] = llm
        return llm
