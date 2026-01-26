import threading
from typing import Optional

import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice

import isaac.sync as sync
from isaac.speakers import SpeakerInterface, SpeechOptions
from isaac.speakers.utils import pre_speech


class PiperSpeaker(SpeakerInterface):
    def __init__(
        self,
        onnx_f: str,
        conf_f: str,
        options: SpeechOptions = SpeechOptions(
            sample_rate=22050, num_channels=1
        ),
    ):
        self.speaker = PiperVoice.load(onnx_f, conf_f)
        self.options = options

    def say(self, text: str, options: Optional[SpeechOptions] = None) -> None:
        """Speaks the given text in a separate thread."""
        options = options or self.options
        with sd.OutputStream(
            samplerate=options.sample_rate,
            channels=options.num_channels,
            dtype="int16",
        ) as stream:
            with sync.speech_lock:
                for audio_bytes in self.speaker.synthesize_stream_raw(text):
                    if sync.event_mute.is_set():
                        break
                    stream.write(np.frombuffer(audio_bytes, dtype=np.int16))

    def say_in_thread(
        self, text: str, options: Optional[SpeechOptions] = None
    ) -> threading.Thread:
        pre_speech()
        t = threading.Thread(target=self.say, args=(text, options))
        sync.speech_thread = t
        t.start()
        return t
