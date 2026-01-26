from abc import ABC
from typing import Literal, Optional


class SettingsInterface(ABC):
    groq_key: Optional[str]
    groq_model: str
    gemini_key: Optional[str]
    gemini_model: str
    hearing_enabled: bool
    whisper_size: str
    speech_enabled: bool
    custom_voices: list[str]
    piper_voice: str
    response_generator: Literal["gemini", "groq"]
    system_message = Optional[str]
    context_enabled: bool
    shell: str
    prompt_tokens: int
    completion_tokens: int
