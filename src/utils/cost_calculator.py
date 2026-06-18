from src.config.settings import settings

def calculate_call_costs(
    input_tokens: int, 
    output_tokens: int, 
    stt_audio_duration: float, 
    tts_characters: int
) -> dict:
    stt_cost = (stt_audio_duration / 60) * settings.STT_COST_PER_MINUTE
    
    tts_cost = (tts_characters / 1_000_000) * settings.TTS_COST_PER_MILLION_CHARS
    
    llm_cost = (
        (input_tokens / 1_000_000) * settings.LLM_INPUT_COST_PER_MILLION +
        (output_tokens / 1_000_000) * settings.LLM_OUTPUT_COST_PER_MILLION
    )
    
    total_cost = stt_cost + tts_cost + llm_cost
    
    return {
        "stt_cost": stt_cost,
        "tts_cost": tts_cost,
        "llm_cost": llm_cost,
        "total_cost": total_cost
    }
