class AgentError(Exception):
    """Base exception for all agent-related errors."""
    pass

class ConfigurationError(AgentError):
    """Raised when configuration is invalid or missing."""
    pass

class ConfigValidationError(AgentError):
    """Raised when configuration validation fails."""
    pass

class DatabaseError(AgentError):
    """Raised when database operations fail."""
    pass

class STTError(AgentError):
    """Raised when Speech-to-Text initialization or processing fails."""
    pass

class TTSError(AgentError):
    """Raised when Text-to-Speech initialization or processing fails."""
    pass

class LLMError(AgentError):
    """Raised when LLM initialization or processing fails."""
    pass

class VADError(AgentError):
    """Raised when Voice Activity Detection initialization fails."""
    pass

class ToolExecutionError(AgentError):
    """Raised when a tool function fails to execute."""
    pass

class TranscriptError(AgentError):
    """Raised when transcript building fails."""
    pass

class MetricsError(AgentError):
    """Raised when metrics collection fails."""
    pass
