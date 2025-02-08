import threading

event_mute = threading.Event()
speech_lock = threading.Lock()
stdout_lock = threading.Lock()
