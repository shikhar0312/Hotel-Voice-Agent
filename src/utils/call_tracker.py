import time
import uuid
from datetime import datetime
from livekit.agents import metrics, MetricsCollectedEvent, AgentSession
from src.database.models import CallConversation, call_conversation_repo
from src.utils.logger import logger

class CallTracker:
    
    def __init__(self, session: AgentSession, room_name: str):
        self.session = session
        self.room_name = room_name
        self.user_id = uuid.uuid4()
        self.start_time = time.time()
        self.usage_collector = metrics.UsageCollector()
        
        self.session.on("metrics_collected", self.handle_metrics_event)
        logger.info(f"CallTracker initialized for room: {room_name}")
    
    def handle_metrics_event(self, ev: MetricsCollectedEvent):
        self.usage_collector.collect(ev.metrics)
        metrics.log_metrics(ev.metrics)
    
    def build_transcript(self) -> str:
        try:
            history = self.session.history
            transcript_lines = []
            
            for item in history:
                role = getattr(item, 'role', 'unknown')
                content = getattr(item, 'content', '')
                
                if content:
                    if role == 'user':
                        transcript_lines.append(f"Guest: {content}")
                    elif role == 'assistant':
                        transcript_lines.append(f"Agent: {content}")
            
            return "\n".join(transcript_lines)
        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            return ""
    
    def calculate_duration(self) -> float:
        return time.time() - self.start_time
    
    def extract_token_usage(self) -> dict:
        try:
            summary = self.usage_collector.get_summary()
            return {
                "input_tokens": getattr(summary, 'llm_prompt_tokens', 0) or 0,
                "output_tokens": getattr(summary, 'llm_completion_tokens', 0) or 0,
                "total_tokens": getattr(summary, 'llm_total_tokens', 0) or 0,
            }
        except Exception as e:
            logger.error(f"Error getting token usage: {e}")
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    
    async def persist_call_record(self, status: str = "completed"):
        try:
            duration = self.calculate_duration()
            transcript = self.build_transcript()
            tokens = self.extract_token_usage()
            
            conversation = CallConversation(
                user_id=self.user_id,
                status=status,
                transcript=transcript,
                input_tokens=tokens["input_tokens"],
                output_tokens=tokens["output_tokens"],
                total_tokens=tokens["total_tokens"],
                duration=duration,
            )
            
            conversation_id = call_conversation_repo.create(conversation)
            logger.info(f"Call saved to database - ID: {conversation_id}, Duration: {duration:.2f}s, Tokens: {tokens['total_tokens']}")
            
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error saving call data: {e}")
            return None
