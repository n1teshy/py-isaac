import queue
import threading
from typing import Optional

from isaac.speakers import SpeakerInterface
from isaac.types import ListenerInterface, SettingsInterface

settings: Optional[SettingsInterface] = None
speaker: Optional[SpeakerInterface] = None
listener: Optional[ListenerInterface] = None
query_queue = queue.Queue()
event_exit = threading.Event()
past_exchanges = []
