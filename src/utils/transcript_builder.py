from typing import Optional
from livekit.agents import AgentSession
from src.utils.logger import create_logger
from src.config.settings import settings
from src.core.exceptions import TranscriptError

logger = create_logger("transcript_builder", settings.LOG_LEVEL)

def format_session_transcript(session: Optional[AgentSession]) -> str:
    """
    Format agent session history into a readable transcript.
    
    Converts session history items into 'Guest:' and 'Agent:' prefixed lines.
    Returns empty string if session is None or has no history.
    """
    if not session or not hasattr(session, 'history'):
        return ""
    
    try:
        history = session.history
        transcript_lines = []
        
        for item in history.items:
            role = getattr(item, 'role', 'unknown')
            content = _extract_content(item)
            
            if content:
                prefix = "Guest: " if role == 'user' else "Agent: "
                transcript_lines.append(f"{prefix}{content}")
        
        return "\n".join(transcript_lines)
    except Exception as e:
        logger.error(f"Error building transcript: {e}")
        return ""

def _extract_content(item) -> str:
    """Extract text content from a history item."""
    content = getattr(item, 'text_content', '') or ''
    if not content and hasattr(item, 'content'):
        content = str(item.content) if item.content else ''
    return content

build_transcript = format_session_transcript
