import queue
import threading
from typing import Optional

from isaac.listeners import ListenerInterface
from isaac.speakers import SpeakerInterface
from isaac.thinkers import ThinkerInterface
from isaac.types import SettingsInterface

settings: Optional[SettingsInterface] = None
listener: Optional[ListenerInterface] = None
thinker: Optional[ThinkerInterface] = None
speaker: Optional[SpeakerInterface] = None
query_queue = queue.Queue()
event_exit = threading.Event()
past_exchanges = []
