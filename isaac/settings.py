import getpass
import importlib
import json
import os
import re
import shutil
import string
import threading
from glob import glob

from yapper import GeminiModel, GroqModel, PiperVoiceGB, PiperVoiceUS
from yapper.constants import piper_voice_quality_map
from yapper.utils import download_piper_model

import isaac.constants as c
import isaac.globals as glb
import isaac.sync as sync
from isaac.listeners.py_listener import ListenOptions, PyListener
from isaac.speakers.piper import PiperSpeaker
from isaac.speakers.utils import mute
from isaac.thinkers import ThinkerConfig
from isaac.thinkers.gemini import GeminiThinker
from isaac.thinkers.groq import GroqThinker
from isaac.types import SettingsInterface
from isaac.utils import (
    get_piper_voice_enum,
    is_wavefile,
    launch_text_editor,
    normalize_path,
    safe_print,
    select_from,
)

whisper_options = [
    "tiny",
    "tiny.en",
    "base",
    "base.en",
    "small",
    "small.en",
    "medium",
    "medium",
    "turbo",
    "large",
    "auto",
]
whisper_option_details = [
    "~1GB",
    "~1GB, english only",
    "~1GB",
    "~1GB, english only",
    "~2GB",
    "~2GB, english only",
    "~5GB",
    "~5GB, english only",
    "~6GB",
    "~10GB",
    "select based on resource availability",
]


class Settings(SettingsInterface):
    """
    stores the user's preferences, loads settings from the default settings
    file on initialization and can dump back to the same file.
    """

    def __init__(self):
        self.ensure_files()
        cache = json.load(open(c.FILE_SETTINGS, encoding="utf-8"))
        self.groq_key = cache[c.STNG_FLD_GROQ][c.STNG_FLD_KEY]
        self.groq_model = cache[c.STNG_FLD_GROQ][c.STNG_FLD_MODEL]
        self.gemini_key = cache[c.STNG_FLD_GEMINI][c.STNG_FLD_KEY]
        self.gemini_model = cache[c.STNG_FLD_GEMINI][c.STNG_FLD_MODEL]
        self.hearing_enabled = cache[c.STNG_FLD_HEARING][c.STNG_FLD_IS_ENABLED]
        self.whisper_size = cache[c.STNG_FLD_HEARING][c.STNG_FLD_WHISPER_SIZE]
        self.speech_enabled = cache[c.STNG_FLD_SPEECH][c.STNG_FLD_IS_ENABLED]
        self.custom_voices = glob(os.path.join(c.VOICES_DIR, "*.wav"))
        # this field was renamed, this is for backward-compatibility
        self.voice = cache[c.STNG_FLD_SPEECH].get(
            c.STNG_FLD_VOICE, PiperVoiceUS.HFC_FEMALE.value
        )
        self.response_generator = cache[c.STNG_FLD_RSPNS_GENERATOR]
        self.system_message = cache[c.STNG_FLD_SYS_MESSAGE]
        self.context_enabled = cache[c.STNG_FLD_CONTEXT_ENABLED]
        self.shell = cache[c.STNG_FLD_SHELL]
        self.prompt_tokens = 0
        self.completion_tokens = 0
        if self.response_generator is None:
            self.select_lm_provider()

    @property
    def lang_model(self):
        if self.response_generator == c.RSPNS_GNRTR_GEMINI:
            return self.gemini_model
        return self.groq_model

    def ensure_files(self):
        """
        ensures that the settings file exists, if not creates it
        with default values.
        """
        os.makedirs(c.APP_DIR, exist_ok=True)
        os.makedirs(c.VOICES_DIR, exist_ok=True)
        if not os.path.isfile(c.FILE_SETTINGS):
            with open(c.FILE_SETTINGS, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        c.STNG_FLD_GROQ: {
                            c.STNG_FLD_KEY: None,
                            c.STNG_FLD_MODEL: None,
                        },
                        c.STNG_FLD_GEMINI: {
                            c.STNG_FLD_KEY: None,
                            c.STNG_FLD_MODEL: None,
                        },
                        c.STNG_FLD_SPEECH: {
                            c.STNG_FLD_IS_ENABLED: False,
                            c.STNG_FLD_VOICE: PiperVoiceUS.HFC_FEMALE.value,
                        },
                        c.STNG_FLD_HEARING: {
                            c.STNG_FLD_IS_ENABLED: False,
                            c.STNG_FLD_WHISPER_SIZE: "auto",
                        },
                        c.STNG_FLD_RSPNS_GENERATOR: None,
                        c.STNG_FLD_SYS_MESSAGE: None,
                        c.STNG_FLD_CONTEXT_ENABLED: True,
                        c.STNG_FLD_SHELL: c.FILE_SHELL,
                    },
                    f,
                    indent=2,
                )

    def dump_to_cache(self):
        """dumps settings to the default settings file."""
        cache = {}
        cache[c.STNG_FLD_GROQ] = {
            c.STNG_FLD_KEY: self.groq_key,
            c.STNG_FLD_MODEL: self.groq_model,
        }
        cache[c.STNG_FLD_GEMINI] = {
            c.STNG_FLD_KEY: self.gemini_key,
            c.STNG_FLD_MODEL: self.gemini_model,
        }
        cache[c.STNG_FLD_SPEECH] = {
            c.STNG_FLD_IS_ENABLED: self.speech_enabled,
            c.STNG_FLD_VOICE: self.voice,
        }
        cache[c.STNG_FLD_HEARING] = {
            c.STNG_FLD_IS_ENABLED: self.hearing_enabled,
            c.STNG_FLD_WHISPER_SIZE: self.whisper_size,
        }
        cache[c.STNG_FLD_RSPNS_GENERATOR] = self.response_generator
        cache[c.STNG_FLD_SYS_MESSAGE] = self.system_message
        cache[c.STNG_FLD_CONTEXT_ENABLED] = self.context_enabled
        cache[c.STNG_FLD_SHELL] = self.shell
        json.dump(
            cache, open(c.FILE_SETTINGS, "w", encoding="utf-8"), indent=2
        )

    def select_lm_provider(self):
        """
        lets the user select a language model provider,
        currently from `Groq` and `Gemini`.
        """
        options = [c.RSPNS_GNRTR_GEMINI, c.RSPNS_GNRTR_GROQ]
        idx = select_from(
            options, prompt="select an LLM API provider", allow_none=False
        )
        self.response_generator = options[idx]
        self.dump_to_cache()
        if self.lang_model is None:
            self.select_lm()
        self.initialize_thinker()

    def select_lm(self):
        """
        lets the user select a language model to be used for answering
        queries.
        """
        if self.response_generator is None:
            self.select_lm_provider()

        options = (
            [model.value for model in GroqModel]
            if self.response_generator == c.RSPNS_GNRTR_GROQ
            else [model.value for model in GeminiModel]
        )
        idx = select_from(
            options, prompt="please select a language model", allow_none=False
        )
        if self.response_generator == c.RSPNS_GNRTR_GEMINI:
            self.gemini_model = options[idx]
            if self.gemini_key is None:
                self.set_key()
        else:
            self.groq_model = options[idx]
            if self.groq_key is None:
                self.set_key()

        self.initialize_thinker()
        self.dump_to_cache()

    def set_key(self):
        """sets the key for the currently selected language model provider."""
        if self.response_generator is None:
            self.select_lm()
        while True:
            key = getpass.getpass(
                f"please enter your {self.response_generator} key: "
            ).strip()
            if len(key) == 0:
                safe_print("invalid key")
                continue
            if self.response_generator == c.RSPNS_GNRTR_GROQ:
                self.groq_key = key
            else:
                self.gemini_key = key
            break
        self.dump_to_cache()
        safe_print()

    def instruct_lm(self):
        """
        sets the system message to be used for querying the language
        model.
        """
        while True:
            message = launch_text_editor(self.system_message)
            if len(message.strip()) == 0:
                safe_print("empty instruction")
                continue
            break
        self.system_message = message
        self.initialize_thinker()
        self.dump_to_cache()

    def toggle_context(self):
        """
        toggles the use of context to help the model come up with coherent
        responses.
        """
        self.context_enabled = not self.context_enabled
        self.dump_to_cache()

    def enable_speech(self):
        """
        enables speech for the assistant so it can both prints and speaks its
        response.
        """
        with sync.stdout_lock:
            if is_wavefile(self.voice):
                # dynamic import because PocketSpeaker is heavy sl
                from isaac.speakers.pocket import PocketSpeaker

                glb.speaker = PocketSpeaker(self.voice)
            else:
                voice = get_piper_voice_enum(self.voice)
                onnx_f, conf_f = download_piper_model(
                    voice, piper_voice_quality_map[voice], True
                )
                glb.speaker = PiperSpeaker(onnx_f, conf_f)
        self.speech_enabled = True
        self.dump_to_cache()

    def disable_speech(self):
        """disables speech for the assistant."""
        self.speech_enabled = False
        self.dump_to_cache()

    def select_voice(self):
        """
        lets the user select a piper voice for the assistant to speak with
        """
        voices = (
            ["custom voice (clone)"]
            + self.custom_voices
            + [voice.value for voice in PiperVoiceUS]
            + [voice.value for voice in PiperVoiceGB]
        )
        idx = select_from(voices, prompt="select a voice")
        if idx == -1:
            return

        if idx > 0:
            self.voice = voices[idx]
        else:
            if importlib.util.find_spec("pocket_tts") is None:
                safe_print(
                    "please run `pip install py-isaac[custom-voice]` first"
                )
                return
            while True:
                safe_print("custom voice (wave file): ", end="")
                file = normalize_path(input().strip())
                if not is_wavefile(file):
                    safe_print("invalid file, please input a valid wave file")
                    continue
                tgt_file = os.path.join(c.VOICES_DIR, os.path.basename(file))
                shutil.copy2(file, tgt_file)
                self.custom_voices.append(tgt_file)
                self.voice = tgt_file
                break

        if not self.speech_enabled:
            self.dump_to_cache()
        else:
            self.enable_speech()

    def toggle_speech(self):
        """toggles the assistant's ability to speak."""
        if self.speech_enabled:
            self.disable_speech()
        else:
            self.enable_speech()

    def select_whisper_size(self):
        """
        lets the user select the size of the whisper model used for converting
        user's speech to text.
        """
        display_options = [
            f"{whisper_options[idx]} ({whisper_option_details[idx]})"
            for idx in range(len(whisper_options))
        ]
        idx = select_from(
            display_options,
            prompt=(
                "please select a whisper model, "
                "large model means better accuracy"
            ),
        )
        self.whisper_size = whisper_options[idx]
        self.dump_to_cache()
        if self.hearing_enabled:
            # load the newly selected whisper model
            self.disable_hearing()
            self.enable_hearing()

    def enable_hearing(self):
        """enables the assistant to hear user with py-listener."""
        event_completion = threading.Event()

        def handle_speech(query: list[str]):
            # print voice transcription on the console so
            # the user may know what the assistant interprets
            query = " ".join(query).strip()
            if re.search(r"\w+", query) is None:
                return
            splits = query.split(" ")
            if len(splits) == 1:
                candidate = "".join(
                    c for c in splits[0] if c not in string.punctuation
                )
                candidate = ":" + candidate.lower()
                if candidate in c.commands:
                    query = candidate
            safe_print(re.sub(r"\n+", ";", query))
            glb.query_queue.put((query, event_completion))
            event_completion.wait()
            if not glb.event_exit.is_set():
                safe_print(">> ", end="")
                event_completion.clear()

        glb.listener = PyListener(
            self.whisper_size,
            ListenOptions(speech_handler=handle_speech, on_speech_start=mute),
        )
        glb.listener.listen()
        self.hearing_enabled = True
        self.dump_to_cache()

    def disable_hearing(self):
        """stops listening to user."""
        glb.listener.close()
        glb.listener = None
        self.hearing_enabled = False
        self.dump_to_cache()

    def toggle_hearing(self):
        """toggles assistant's ability to hear user's speech."""
        if self.hearing_enabled:
            self.disable_hearing()
        else:
            self.enable_hearing()

    def initialize_thinker(self):
        if self.response_generator == c.RSPNS_GNRTR_GEMINI:
            config = ThinkerConfig(
                self.gemini_model, self.gemini_key, self.system_message
            )
            glb.thinker = GeminiThinker(config)
        else:
            config = ThinkerConfig(
                self.groq_model, self.groq_key, self.system_message
            )
            glb.thinker = GroqThinker(config)

    def enact(self):
        """brings the settings into action."""
        if self.hearing_enabled:
            self.enable_hearing()
        self.initialize_thinker()
        if self.speech_enabled:
            self.enable_speech()
