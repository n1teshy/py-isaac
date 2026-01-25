from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class ThinkerConfig:
    model: str
    api_key: str
    system_message: str


class ThoughtOptions:
    system_message: Optional[str] = None
    history: Optional[list] = None
    temperature: float = 1.0


class ThinkerInterface(ABC):
    config: ThinkerConfig

    def __init__(self, config: ThinkerConfig):
        self.config = config

    @abstractmethod
    def think(
        self, query: str, options: Optional[ThoughtOptions] = None
    ) -> str: ...

    def stream(self, query: str, options: ThoughtOptions) -> Iterator[str]:
        raise NotImplemented(
            f"{self.__class__.__name__} does not support streaming"
        )
