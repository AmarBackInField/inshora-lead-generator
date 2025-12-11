"""Configuration settings for the telephony agent."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class STTConfig:
    """Speech-to-Text configuration."""
    model: str = "nova-3"
    language: str = "en-US"
    interim_results: bool = True
    punctuate: bool = True
    smart_format: bool = True
    filler_words: bool = True
    endpointing_ms: int = 25
    sample_rate: int = 16000


@dataclass
class LLMConfig:
    """Large Language Model configuration."""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7


@dataclass
class TTSConfig:
    """Text-to-Speech configuration."""
    model: str = "sonic-2"
    voice: str = "a0e99841-438c-4a64-b679-ae501e7d6091"  # Professional female voice
    language: str = "en"
    speed: float = 1.0
    sample_rate: int = 24000


@dataclass
class RAGConfig:
    """RAG Service configuration."""
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    openai_api_key: Optional[str] = None


@dataclass
class AgentConfig:
    """Main agent configuration."""
    agent_name: str = "inbound-agent"
    log_level: str = "INFO"
    
    # Sub-configurations
    stt: STTConfig = field(default_factory=STTConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)


# Default configuration instance
default_config = AgentConfig()

