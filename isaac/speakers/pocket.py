import threading
import wave
from typing import Optional

import sounddevice as sd

import isaac.sync as sync
from isaac.speakers import SpeakerInterface, SpeechOptions
from isaac.speakers.utils import pre_speech


class PocketSpeaker(SpeakerInterface):
    def __init__(
        self,
        voice_file: str,
        options: SpeechOptions = SpeechOptions(sample_rate=24000),
    ):
        from pocket_tts import TTSModel

        self.tts = TTSModel.load_model()
        self.options = options
        device = next(self.tts.parameters()).device
        self.voice_sample = self._load_wav(
            voice_file, self.tts.sample_rate, device
        )

    def _load_wav(self, path: str, sample_rate: int, device):
        import numpy as np
        import torch
        from scipy.signal import resample_poly

        with wave.open(path, "rb") as wf:
            sr = wf.getframerate()
            n_channels = wf.getnchannels()
            n_frames = wf.getnframes()
            audio_bytes = wf.readframes(n_frames)
            audio = (
                np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
                / 32768.0
            )
            if n_channels > 1:
                audio = audio.reshape(-1, n_channels).mean(axis=1)
            if sr != sample_rate:
                gcd = np.gcd(sr, sample_rate)
                up = sample_rate // gcd
                down = sr // gcd
                audio = resample_poly(audio, up, down)

        return torch.from_numpy(audio).unsqueeze(0).to(device)

    def say(self, text: str, options: Optional[SpeechOptions] = None) -> None:
        with sd.OutputStream(
            samplerate=self.tts.sample_rate, channels=1, dtype="float32"
        ) as stream:
            state = self.tts.get_state_for_audio_prompt(self.voice_sample)
            with sync.speech_lock:
                for chunk in self.tts.generate_audio_stream(
                    model_state=state, text_to_generate=text, copy_state=True
                ):
                    if sync.event_mute.is_set():
                        break
                    chunk = (
                        chunk.numpy()
                        if chunk.device.type == "cpu"
                        else chunk.cpu().numpy()
                    )
                    stream.write(chunk)

    def say_in_thread(
        self, text: str, options: Optional[SpeechOptions] = None
    ) -> threading.Thread:
        pre_speech()
        t = threading.Thread(target=self.say, args=(text, options))
        sync.speech_thread = t
        t.start()
        return t

    def close(self):
        del self.tts
