import threading
import queue
from isaac.types import SettingsInterface, SpeakerInteface, ListenerInterface
from typing import Optional


settings: Optional[SettingsInterface] = None
speaker: Optional[SpeakerInteface] = None
listener: Optional[ListenerInterface] = None
query_queue = queue.Queue()
event_exit = threading.Event()
past_exchanges = []
