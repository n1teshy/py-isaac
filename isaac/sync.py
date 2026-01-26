import threading

event_mute = threading.Event()
speech_thread: threading.Thread | None = None

speech_lock = threading.Lock()
stdout_lock = threading.Lock()
