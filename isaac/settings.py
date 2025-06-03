import re
import json
import string
import threading

from yapper import GeminiModel, GroqModel, PiperVoiceGB, PiperVoiceUS

import isaac.constants as c
from isaac.utils import select_from, write, get_piper_voice_enum, safe_input
from isaac.types import SettingsInterface
import isaac.speech as speech
from yapper import PiperSpeaker
import isaac.globals as glb
import isaac.sync as sync


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
        cache = json.load(open(c.FILE_SETTINGS, encoding="utf-8"))
        self.groq_key = cache[c.STNG_FLD_GROQ][c.STNG_FLD_KEY]
        self.groq_model = cache[c.STNG_FLD_GROQ][c.STNG_FLD_MODEL]
        self.gemini_key = cache[c.STNG_FLD_GEMINI][c.STNG_FLD_KEY]
        self.gemini_model = cache[c.STNG_FLD_GEMINI][c.STNG_FLD_MODEL]
        self.hearing_enabled = cache[c.STNG_FLD_HEARING][c.STNG_FLD_IS_ENABLED]
        self.whisper_size = cache[c.STNG_FLD_HEARING][c.STNG_FLD_WHISPER_SIZE]
        self.speech_enabled = cache[c.STNG_FLD_SPEECH][c.STNG_FLD_IS_ENABLED]
        self.piper_voice = cache[c.STNG_FLD_SPEECH][c.STNG_FLD_PIPER_VOICE]
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
        elif self.response_generator == c.RSPNS_GNRTR_GROQ:
            return self.groq_model
        return None

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
            c.STNG_FLD_PIPER_VOICE: self.piper_voice,
        }
        cache[c.STNG_FLD_HEARING] = {
            c.STNG_FLD_IS_ENABLED: self.hearing_enabled,
            c.STNG_FLD_WHISPER_SIZE: self.whisper_size,
        }
        cache[c.STNG_FLD_RSPNS_GENERATOR] = self.response_generator
        cache[c.STNG_FLD_SYS_MESSAGE] = self.system_message
        cache[c.STNG_FLD_CONTEXT_ENABLED] = self.context_enabled
        cache[c.STNG_FLD_SHELL] = self.shell
        json.dump(cache, open(c.FILE_SETTINGS, "w", encoding="utf-8"), indent=2)

    def select_lm_provider(self):
        """
        lets the user select a language model provider,
        currently from `Groq` and `Gemini`.
        """
        options = [c.RSPNS_GNRTR_GEMINI, c.RSPNS_GNRTR_GROQ]
        idx = select_from(
            options, prompt="select an LLM API provider", allow_none=False
        )
        if idx != -1:
            self.response_generator = options[idx]
        if self.lang_model is None:
            self.select_lm()

    def select_lm(self):
        """
        lets the user select a language model to be used for answering
        queries.
        """
        if self.response_generator is None:
            self.select_lm_provider()
        provider = self.response_generator
        if provider is None:
            return
        options = (
            [model.value for model in GroqModel]
            if self.response_generator == c.RSPNS_GNRTR_GROQ
            else list(GeminiModel)
        )
        idx = select_from(
            options, prompt="please select a language model", allow_none=False
        )
        if idx == -1:
            return
        if provider == c.RSPNS_GNRTR_GEMINI:
            self.gemini_model = options[idx]
        else:
            self.groq_model = options[idx]

        if (
            self.response_generator == c.RSPNS_GNRTR_GROQ
            and self.groq_key is None
            or self.response_generator == c.RSPNS_GNRTR_GEMINI
            and self.gemini_key is None
        ):
            self.set_key()

    def set_key(self):
        """sets the key for the currently selected language model provider."""
        if self.response_generator is None:
            self.select_lm()
        key = safe_input(f"please enter your {self.response_generator} key: ").strip()
        if len(key) > 0:
            if self.response_generator == c.RSPNS_GNRTR_GROQ:
                self.groq_key = key
            else:
                self.gemini_key = key
        write()

    def instruct_lm(self):
        """
        sets the system message to be used for querying the language
        model.
        """
        message = safe_input("instruction: ")
        if len(message.strip()) > 0:
            self.system_message = message

    def toggle_context(self):
        """
        toggles the use of context to help the model come up with coherent
        responses.
        """
        self.context_enabled = not self.context_enabled

    def enable_speech(self):
        """
        enables speech for the assistant so it can both prints and speaks its
        response.
        """
        with sync.stdout_lock:
            glb.speaker = PiperSpeaker(get_piper_voice_enum(self.piper_voice))
        self.speech_enabled = True

    def disable_speech(self):
        """disables speech for the assistant."""
        glb.speaker = None
        self.speech_enabled = False

    def select_voice(self):
        """
        lets the user select a piper voice for the assistant to speak with
        """
        voices = [voice.value for voice in PiperVoiceUS] + [
            voice.value for voice in PiperVoiceGB
        ]
        idx = select_from(voices, prompt="select a voice")
        if idx == -1:
            return
        if self.speech_enabled and self.piper_voice != voices[idx]:
            with sync.stdout_lock:
                glb.speaker = PiperSpeaker(get_piper_voice_enum(voices[idx]))
        self.piper_voice = voices[idx]

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
            prompt="please select a whisper model, large model means better accuracy",
        )
        self.whisper_size = whisper_options[idx]

    def enable_hearing(self):
        """enables the assistant to hear user with py-listener."""
        from listener import Listener

        event_completion = threading.Event()

        def handle_speech(query: list[str]):
            # print voice transcription on the console so
            # the user may know what the assistant interprets
            query = " ".join(query).strip()
            if re.search("\w+", query) is None:
                return
            splits = query.split(" ")
            if len(splits) == 1:
                candidate = "".join(c for c in splits[0] if c not in string.punctuation)
                candidate = ":" + candidate.lower()
                if candidate in c.commands:
                    query = candidate
            write(re.sub(r"\n+", ";", query))
            glb.query_queue.put((query, event_completion))
            event_completion.wait()
            if not glb.event_exit.is_set():
                write(">> ", end="")
                event_completion.clear()

        glb.listener = Listener(
            time_window=3,
            speech_handler=handle_speech,
            on_speech_start=speech.mute,
            whisper_size=self.whisper_size,
            en_only=True,
            # show_download=False
        )
        glb.listener.listen()
        self.hearing_enabled = True

    def disable_hearing(self):
        """stops listening to user."""
        glb.listener.close()
        glb.listener = None
        self.hearing_enabled = False

    def toggle_hearing(self):
        """toggles assistant's ability to hear user's speech."""
        if self.hearing_enabled:
            self.disable_hearing()
        else:
            self.enable_hearing()

    def enact(self):
        """brings the settings into action."""
        if self.speech_enabled:
            self.enable_speech()
        if self.hearing_enabled:
            self.enable_hearing()
