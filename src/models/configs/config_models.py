from pydantic import Field
from pydantic.dataclasses import dataclass
from typing import Literal

@dataclass
class LiveKitConfig:
    url: str
    api_key: str
    api_secret: str

@dataclass
class OpenAIConfig:
    api_key: str
    stt_model: str
    llm_model: str
    tts_model: str
    tts_voice: str
    temperature: float = Field(ge=0.0, le=2.0)

@dataclass
class DeepgramConfig:
    api_key: str
    stt_model: str

@dataclass
class HotelConfig:
    name: str
    assistant_name: str
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

@dataclass
class DatabaseConfig:
    host: str
    database: str
    user: str
    password: str
    port: int = Field(ge=1, le=65535)

@dataclass
class CostConfig:
    stt_cost_per_minute: float = Field(ge=0.0)
    tts_cost_per_million_chars: float = Field(ge=0.0)
    llm_input_cost_per_million: float = Field(ge=0.0)
    llm_output_cost_per_million: float = Field(ge=0.0)

@dataclass
class ProviderConfig:
    selected_stt: Literal["openai", "deepgram", "elevenlabs"]
    selected_tts: Literal["openai", "elevenlabs"]
    selected_llm: Literal["openai", "gemini"]
    selected_vad: Literal["silero"]

@dataclass
class Settings:
    livekit: LiveKitConfig
    openai: OpenAIConfig
    deepgram: DeepgramConfig
    hotel: HotelConfig
    database: DatabaseConfig
    cost: CostConfig
    providers: ProviderConfig

    @property
    def selected_stt(self) -> str:
        return self.providers.selected_stt

    @property
    def selected_tts(self) -> str:
        return self.providers.selected_tts

    @property
    def selected_llm(self) -> str:
        return self.providers.selected_llm

    @property
    def selected_vad(self) -> str:
        return self.providers.selected_vad
