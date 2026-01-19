from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class ListenOptions:
    sampling_rate: int = 16000
    num_channels: int = 1
    time_window_s: int = 2
    on_speech_start: Optional[Callable] = None
    speech_handler: Optional[Callable[[str], None]] = None
    en_only: bool = True


class ListenerInterface(ABC):
    options: ListenOptions

    def __init__(self, options: ListenOptions):
        self.options = options

    @abstractmethod
    def listen(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def pause(self) -> None: ...

    @abstractmethod
    def resume(self) -> None: ...
