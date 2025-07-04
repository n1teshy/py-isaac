import threading
import queue
from isaac.types import SettingsInterface, ListenerInterface
from typing import Optional
from piper.voice import PiperVoice


settings: Optional[SettingsInterface] = None
speaker: Optional[PiperVoice] = None
listener: Optional[ListenerInterface] = None
query_queue = queue.Queue()
event_exit = threading.Event()
past_exchanges = []
