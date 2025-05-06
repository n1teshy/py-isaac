import os
import tempfile
import threading


import isaac.globals as glb
import isaac.sync as sync

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame


def mute():
    """
    sets the `event_mute` event that signals the speaker thread to stop
    speaking.
    """
    sync.event_mute.set()


def say(text: str):
    """Speaks the given text in a separate thread."""

    def say_in_thread(text: str):
        sync.event_mute.clear()
        with sync.speech_lock:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                file = temp.name
            try:
                glb.speaker.text_to_wave(text, file)
                pygame.mixer.init()
                sound = pygame.mixer.Sound(file)
                sound.play()
                while pygame.mixer.get_busy():
                    if sync.event_mute.is_set():
                        sound.stop()
                        break
                    pygame.time.wait(100)
            finally:
                os.remove(file)

    threading.Thread(target=say_in_thread, args=(text,)).start()
