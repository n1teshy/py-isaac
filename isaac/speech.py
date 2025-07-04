import threading
import sounddevice as sd

import isaac.globals as glb
import isaac.sync as sync
import numpy as np

PIPER_SAMPLE_RATE = 22050
PIPER_NUM_CHANNELS = 1


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

        with sd.OutputStream(
            samplerate=PIPER_SAMPLE_RATE, channels=PIPER_NUM_CHANNELS, dtype="int16"
        ) as stream:
            with sync.speech_lock:
                for audio_bytes in glb.speaker.synthesize_stream_raw(text):
                    if sync.event_mute.is_set():
                        break
                    stream.write(np.frombuffer(audio_bytes, dtype=np.int16))

    threading.Thread(target=say_in_thread, args=(text,)).start()
