import uuid
from typing import Optional
from src.models.state.call_conversation import CallConversation
from src.database.models import call_conversation_repo
from src.utils.logger import logger
from src.database.init_db import initialize_database
from src.utils.usage_extractor import get_usage_summary
from src.core.exceptions import DatabaseError

def build_call_conversation(
    call_data: dict,
    duration: float,
    transcript: str,
    costs: dict
) -> CallConversation:
    """
    Build a CallConversation entity from call data.
    
    Combines metrics, costs, and transcript into a complete conversation record.
    """
    metrics = get_usage_summary(call_data.get("usage_collector"))
    
    return CallConversation(
        user_id=call_data.get("user_id", uuid.uuid4()),
        status="completed",
        transcript=transcript,
        input_tokens=metrics["input_tokens"],
        output_tokens=metrics["output_tokens"],
        total_tokens=metrics["input_tokens"] + metrics["output_tokens"],
        duration=duration,
        stt_audio_duration=metrics["stt_audio_duration"],
        tts_characters=metrics["tts_characters"],
        stt_cost=costs["stt_cost"],
        tts_cost=costs["tts_cost"],
        llm_cost=costs["llm_cost"],
        total_cost=costs["total_cost"],
    )

async def save_call_conversation(conversation: CallConversation) -> Optional[int]:
    """
    Persist a CallConversation to the database.
    
    Returns the conversation ID if successful, None otherwise.
    """
    try:
        await initialize_database()
        
        conversation_id = await call_conversation_repo.create(conversation)
        return conversation_id
    except Exception as e:
        logger.error(f"Error saving call conversation: {e}")
        return None

create_call_record = build_call_conversation
persist_call_record = save_call_conversation
