import os
import sys
import os.path as path

import isaac.meta as meta

# Gemini API fields
GMNI_FLD_SYS_INST = "system_instruction"
GMNI_FLD_CONTENT = "content"
GMNI_FLD_ROLE = "role"
GMNI_FLD_PARTS = "parts"
GMNI_FLD_CONTENTS = "contents"
GMNI_FLD_CANDIDATES = "candidates"
GMNI_FLD_TEXT = "text"
GMNI_FLD_USAGE = "usageMetadata"
GMNI_FLD_ERROR = "error"

GMNI_USG_PROMPT = "promptTokenCount"
GMNI_USG_COMPLETION = "candidatesTokenCount"

GMNI_ROLE_USER = "user"
GMNI_ROLE_MODEL = "model"

# Groq  API fields
GROQ_FLD_ROLE = "role"
GROQ_FLD_CHOICES = "choices"
GROQ_FLD_MESSAGE = "message"
GROQ_FLD_CONTENT = "content"
GROQ_FLD_MESSAGES = "messages"
GROQ_FLD_MODEL = "model"
GROQ_FLD_USAGE = "usage"
GROQ_FLD_ERROR = "error"
GROQ_FLD_ERROR_CODE = "code"

GROQ_USG_PROMPT = "prompt_tokens"
GROQ_USG_COMPLETION = "completion_tokens"

GROQ_ROLE_SYSTEM = "system"
GROQ_ROLE_USER = "user"
GROQ_ROLE_ASSISTANT = "assistant"

# Settings fields
STNG_FLD_GROQ = "groq"
STNG_FLD_GEMINI = "gemini"
STNG_FLD_KEY = "key"
STNG_FLD_MODEL = "model"
STNG_FLD_HEARING = "hearing"
STNG_FLD_WHISPER_SIZE = "whisperSize"
STNG_FLD_SPEECH = "speech"
STNG_FLD_PIPER_VOICE = "piperVoice"
STNG_FLD_IS_ENABLED = "isEnabled"
STNG_FLD_RSPNS_GENERATOR = "responseGenerator"
STNG_FLD_SYS_MESSAGE = "systemMessage"
STNG_FLD_CONTEXT_ENABLED = "contextEnabled"
STNG_FLD_SHELL = "shell"

# Response generator APIs
RSPNS_GNRTR_GROQ = "groq"
RSPNS_GNRTR_GEMINI = "gemini"


if os.name == "nt":
    APP_DIR = path.join(os.getenv("APPDATA"), meta.name)
elif os.name == "posix":
    home = path.expanduser("~")
    if os.uname().sysname == "Darwin":
        APP_DIR = path.join(home, "Library/Application Support", meta.name)
    else:
        APP_DIR = path.join(home, ".config", meta.name)
else:
    print("your system is not supported")
    sys.exit()

# File names
FILE_SETTINGS = path.join(APP_DIR, "settings.json")
FILE_SHELL = "powershell.exe" if os.name == "nt" else "/bin/sh"

# messages
MSG_LANG_MODEL_ERROR = "could not process that query, something went wrong"
