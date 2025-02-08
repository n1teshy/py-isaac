import json
import os

from yapper import PiperVoiceUS

import isaac.constants as c

if not os.path.isdir(c.APP_DIR):
    os.mkdir(c.APP_DIR)

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
                    c.STNG_FLD_PIPER_VOICE: PiperVoiceUS.HFC_FEMALE.value,
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
