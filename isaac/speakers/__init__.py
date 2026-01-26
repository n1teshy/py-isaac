import threading as t
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class SpeechOptions:
    sample_rate: int = 44100
    num_channels: int = 1


class SpeakerInterface(ABC):
    @abstractmethod
    def say(
        self, text: str, options: Optional[SpeechOptions] = None
    ) -> None: ...

    @abstractmethod
    def say_in_thread(
        self, text: str, options: Optional[SpeechOptions] = None
    ) -> t.Thread: ...

    def close(self):
        pass
