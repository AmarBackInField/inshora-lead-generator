"""Configuration package."""

from .agent_config import (
    AgentConfig,
    STTConfig,
    LLMConfig,
    TTSConfig,
    RAGConfig,
    default_config
)
from .prompts import (
    AGENT_SYSTEM_INSTRUCTIONS,
    CHATBOT_SYSTEM_INSTRUCTIONS,
    get_greeting_prompt
)
from .knowledgebase import (
    INSHORA_KNOWLEDGE_BASE,
    get_knowledge_base,
    get_texas_laws,
    get_objection_handling,
    get_escalation_protocols,
    get_lead_scoring,
    get_tone_adaptation,
    get_promotions,
    get_rebuttals
)

__all__ = [
    "AgentConfig",
    "STTConfig",
    "LLMConfig",
    "TTSConfig",
    "RAGConfig",
    "default_config",
    "AGENT_SYSTEM_INSTRUCTIONS",
    "CHATBOT_SYSTEM_INSTRUCTIONS",
    "get_greeting_prompt",
    # Knowledge Base exports
    "INSHORA_KNOWLEDGE_BASE",
    "get_knowledge_base",
    "get_texas_laws",
    "get_objection_handling",
    "get_escalation_protocols",
    "get_lead_scoring",
    "get_tone_adaptation",
    "get_promotions",
    "get_rebuttals"
]

