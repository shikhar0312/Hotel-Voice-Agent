from typing import Optional
from src.utils.logger import create_logger
from src.config.settings import settings
from src.core.exceptions import MetricsError

logger = create_logger("usage_extractor", settings.LOG_LEVEL)

def get_usage_summary(usage_collector) -> dict:
    """
    Extract usage metrics from a UsageCollector.
    
    Returns a dictionary with input/output tokens, STT duration, and TTS characters.
    Returns zero values if collector is None or extraction fails.
    """
    empty_metrics = {
        "input_tokens": 0,
        "output_tokens": 0,
        "stt_audio_duration": 0.0,
        "tts_characters": 0
    }
    
    if not usage_collector:
        return empty_metrics
    
    try:
        summary = usage_collector.get_summary()
        return {
            "input_tokens": getattr(summary, 'llm_prompt_tokens', 0) or 0,
            "output_tokens": getattr(summary, 'llm_completion_tokens', 0) or 0,
            "stt_audio_duration": getattr(summary, 'stt_audio_duration', 0) or 0,
            "tts_characters": getattr(summary, 'tts_characters_count', 0) or 0
        }
    except Exception as e:
        logger.error(f"Error getting usage summary: {e}")
        return empty_metrics

extract_usage_metrics = get_usage_summary
