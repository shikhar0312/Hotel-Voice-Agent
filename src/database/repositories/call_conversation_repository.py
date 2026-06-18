from typing import Optional, List
import uuid
from src.database.connection import database_pool
from src.models.state.call_conversation import CallConversation

class ConversationStore:
    """Store for CallConversation database operations."""
    
    @staticmethod
    async def create(conversation: CallConversation) -> int:
        """Create a new call conversation record. Returns the new ID."""
        async with database_pool.get_connection() as conn:
            query = """
                INSERT INTO call_conversation 
                (user_id, status, transcript, input_tokens, output_tokens, total_tokens, 
                    duration, stt_audio_duration, tts_characters, stt_cost, tts_cost, llm_cost, total_cost)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id
            """
            return await conn.fetchval(
                query,
                str(conversation.user_id),
                conversation.status,
                conversation.transcript,
                conversation.input_tokens,
                conversation.output_tokens,
                conversation.total_tokens,
                conversation.duration,
                conversation.stt_audio_duration,
                conversation.tts_characters,
                conversation.stt_cost,
                conversation.tts_cost,
                conversation.llm_cost,
                conversation.total_cost
            )
    
    @staticmethod
    async def find_by_id(conversation_id: int) -> Optional[CallConversation]:
        """Find a call conversation by ID. Returns None if not found."""
        async with database_pool.get_connection() as conn:
            query = """
                SELECT id, user_id, status, transcript, input_tokens, output_tokens, 
                    total_tokens, duration, stt_audio_duration, tts_characters,
                    stt_cost, tts_cost, llm_cost, total_cost, created_at
                FROM call_conversation
                WHERE id = $1
            """
            row = await conn.fetchrow(query, conversation_id)
            
            if row:
                return _row_to_conversation(row)
            return None
    
    @staticmethod
    async def find_all(limit: int = 100) -> List[CallConversation]:
        """Find all call conversations, ordered by most recent first."""
        async with database_pool.get_connection() as conn:
            query = """
                SELECT id, user_id, status, transcript, input_tokens, output_tokens, 
                    total_tokens, duration, stt_audio_duration, tts_characters,
                    stt_cost, tts_cost, llm_cost, total_cost, created_at
                FROM call_conversation
                ORDER BY created_at DESC
                LIMIT $1
            """
            rows = await conn.fetch(query, limit)
            return [_row_to_conversation(row) for row in rows]

def _row_to_conversation(row) -> CallConversation:
    """Convert a database row to a CallConversation entity."""
    return CallConversation(
        id=row[0],
        user_id=uuid.UUID(row[1]),
        status=row[2],
        transcript=row[3],
        input_tokens=row[4],
        output_tokens=row[5],
        total_tokens=row[6],
        duration=row[7],
        stt_audio_duration=row[8],
        tts_characters=row[9],
        stt_cost=row[10],
        tts_cost=row[11],
        llm_cost=row[12],
        total_cost=row[13],
        created_at=row[14]
    )


call_conversation_repo = ConversationStore()
