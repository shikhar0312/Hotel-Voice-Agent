import os
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Literal

load_dotenv()

class Settings(BaseSettings):
    LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "")
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    GOOGLE_TTS_VOICE: str = os.getenv("GOOGLE_TTS_VOICE", "en-US-Journey-F")
    GOOGLE_TTS_LANGUAGE: str = os.getenv("GOOGLE_TTS_LANGUAGE", "en-US")
    STT_MODEL: str = os.getenv("STT_MODEL", "whisper-1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    TTS_MODEL: str = os.getenv("TTS_MODEL", "tts-1")
    TTS_VOICE: str = os.getenv("TTS_VOICE", "alloy")
    LLM_TEMPERATURE: float = Field(default=0.5, ge=0.0, le=2.0)
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", os.getenv("ELEVEN_API_KEY", ""))
    ELEVENLABS_STT_MODEL: str = os.getenv("ELEVENLABS_STT_MODEL", "scribe_v2_realtime")
    ELEVENLABS_TTS_MODEL: str = os.getenv("ELEVENLABS_TTS_MODEL", "eleven_multilingual_v2")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "")

    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    DEEPGRAM_STT_MODEL: str = os.getenv("DEEPGRAM_STT_MODEL", "nova-2")

    HUBSPOT_ACCESS_TOKEN: str = os.getenv("HUBSPOT_ACCESS_TOKEN", "")
    HUBSPOT_API_BASE_URL: str = os.getenv("HUBSPOT_API_BASE_URL", "https://api.hubapi.com")

    HOTEL_NAME: str = os.getenv("HOTEL_NAME", "Grandview Hotel")
    ASSISTANT_NAME: str = os.getenv("ASSISTANT_NAME", "Kelly")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = Field(default=5432, ge=1, le=65535)
    DB_NAME: str = os.getenv("DB_NAME", "hotel_room_service")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    STT_COST_PER_MINUTE: float = float(os.getenv("STT_COST_PER_MINUTE", "0.0043"))
    TTS_COST_PER_MILLION_CHARS: float = float(os.getenv("TTS_COST_PER_MILLION_CHARS", "15.0"))
    LLM_INPUT_COST_PER_MILLION: float = float(os.getenv("LLM_INPUT_COST_PER_MILLION", "0.15"))
    LLM_OUTPUT_COST_PER_MILLION: float = float(os.getenv("LLM_OUTPUT_COST_PER_MILLION", "0.60"))

    SELECTED_STT: Literal["openai", "deepgram", "elevenlabs"] = "deepgram"
    SELECTED_TTS: Literal["openai", "elevenlabs","google","deepgram"] = "openai"
    SELECTED_LLM: Literal["openai", "gemini"] = "openai"
    SELECTED_VAD: Literal["silero"] = "silero"

    @field_validator("LIVEKIT_URL")
    @classmethod
    def validate_livekit_url(cls, v: str) -> str:
        if not v.startswith(("ws://", "wss://", "http://", "https://")):
            raise ValueError(f"LIVEKIT_URL must be a valid URL (got: {v})")
        return v

    @field_validator(
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "STT_MODEL",
        "LLM_MODEL",
        "TTS_MODEL",
        "TTS_VOICE",
        "DEEPGRAM_STT_MODEL",
        "HOTEL_NAME",
        "ASSISTANT_NAME",
        "DB_HOST",
        "DB_NAME",
        "DB_USER"
    )
    @classmethod
    def validate_not_empty(cls, v: str, info) -> str:
        if not v or v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
