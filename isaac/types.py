from typing import Optional, Literal
from abc import ABC, abstractmethod


class SettingsInterface(ABC):
    groq_key: Optional[str]
    groq_model: str
    gemini_key: Optional[str]
    gemini_model: str
    hearing_enabled: bool
    whisper_size: str
    speech_enabled: bool
    piper_voice: str
    response_generator: Literal["gemini", "groq"]
    system_message = Optional[str]
    context_enabled: bool
    shell: str
    prompt_tokens: int
    completion_tokens: int


class SpeakerInteface(ABC):
    @abstractmethod
    def text_to_wave(self, text: str, file: str): ...


class ListenerInterface(ABC):
    @abstractmethod
    def listen(self): ...

    @abstractmethod
    def close(self): ...

    @abstractmethod
    def pause(self): ...

    @abstractmethod
    def resume(self): ...
