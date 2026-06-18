from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class CallConversation:
    user_id: uuid.UUID
    status: str
    transcript: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    duration: float
    stt_audio_duration: float = 0.0
    tts_characters: int = 0
    stt_cost: float = 0.0
    tts_cost: float = 0.0
    llm_cost: float = 0.0
    total_cost: float = 0.0
    id: Optional[int] = None
    created_at: Optional[datetime] = None
