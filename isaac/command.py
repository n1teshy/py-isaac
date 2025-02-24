try:
    import readline
except ImportError:
    import pyreadline3 as readline
import shlex
from typing import Optional

import platform
import subprocess
import isaac.constants as c
import isaac.globals as glb
import isaac.sync as sync
import psutil
import os
import isaac.speech as speech
from isaac.theme import BOLD_BRIGHT, BRIGHT, RESET
from isaac.utils import clear, write, label_switch, handle_lm_response
import isaac.lang_models as lm
from difflib import SequenceMatcher


def is_command(text: str) -> bool:
    """
    prints if the given text is a command, i.e. if it starts with a colon(:).
    """
    return text.startswith(":")


def is_shell_command(text: str) -> bool:
    return text.startswith("!")


def command_exists(word: str) -> bool:
    """
    checks if the given word is one of the valid commands defined in the file.
    """
    return word in c.commands


def handle_misspell(word: str) -> str:
    """prints the most similar command to word."""

    # penalizes command matches that don't share the first letter
    def key(c: str):
        return SequenceMatcher(None, word, c).ratio() * (
            0.8 if c[:2] != word[:2] else 1
        )

    similar = max(c.commands, key=key)
    write(f"command not found, did you mean '{similar}'?")


def command_completer(text: str, state: int) -> Optional[str]:
    """handles auto-completion of commands and their arguments."""
    text = readline.get_line_buffer().lstrip()
    if not is_command(text):
        return
    words = shlex.split(text)
    if len(words) > 2:
        return
    command = words[0]
    if not command_exists(command):
        if len(words) == 1:
            options = [cmd for cmd in c.commands if cmd.startswith(command)]
            return options[state] if state < len(options) else None
        return None
    if command not in c.command_args:
        return
    arg = words[1] if len(words) == 2 else ""
    options = [option for option in c.command_args[command] if option.startswith(arg)]
    return options[state] if state < len(options) else None


def handle_select(args: list[str]):
    """handles the ':select' command."""
    if len(args) > 1:
        write(":select only takes one argument")
        return
    elif len(args) == 0:
        write(":select needs an argument")
        return

    arg = args[0]
    if arg not in c.selectables:
        write(f"invalid argument {arg}, must be one of {c.selectables}")
        return

    if arg == c.SELECTABLE_LM_PROVIDER:
        glb.settings.select_lm_provider()
    elif arg == c.SELECTABLE_LANG_MODEL:
        glb.settings.select_lm()
    elif arg == c.SELECTABLE_VOICE:
        glb.settings.select_voice()
    else:
        glb.settings.select_whisper_size()


def handle_toggle(args: list[str]):
    """handles the ':toggle' command."""
    if len(args) > 1:
        write(":toggle only takes one argument")
        return
    elif len(args) == 0:
        write(":toggle needs an argument")
        return

    arg = args[0]
    if arg not in c.togglables:
        write(f"invalid argument {arg}, argument must be one of {c.togglables}")
        return

    if arg == c.TOGGLABLE_SPEECH:
        glb.settings.toggle_speech()
    elif arg == c.TOGGLABLE_CONTEXT:
        glb.settings.toggle_context()
    else:
        glb.settings.toggle_hearing()


def handle_cmd():
    """handles the `:cmd` command, i.e. launches the appropriate shell."""
    try:
        if glb.listener is not None:
            glb.listener.pause()
        if platform.system() == "Windows":
            subprocess.run(["powershell.exe"])
        else:
            subprocess.run(["/bin/sh"])
    finally:
        if glb.listener is not None:
            glb.listener.resume()


def display_status():
    """Displays the user's preferences, token cost, and memory consumption."""
    settings = glb.settings
    lang_model = (
        glb.settings.groq_model
        if settings.response_generator == c.RSPNS_GNRTR_GROQ
        else glb.settings.gemini_model
    )
    total_mem = psutil.virtual_memory().total
    parent = psutil.Process(os.getpid())
    consumed_mem = parent.memory_info().rss
    for child in parent.children(recursive=True):
        consumed_mem += child.memory_info().rss
    mem_per = consumed_mem / total_mem * 100

    lines = [
        "%slanguage model:%s" % (BOLD_BRIGHT, RESET),
        "  %sprovider%s: %s" % (BRIGHT, RESET, settings.response_generator),
        "  %smodel:%s %s" % (BRIGHT, RESET, lang_model),
        "  %sinstruction:%s %s" % (BRIGHT, RESET, settings.system_message or "null"),
        "  %scontext:%s %s" % (BRIGHT, RESET, label_switch(settings.context_enabled)),
        "%sspeech:%s" % (BOLD_BRIGHT, RESET),
        "  %sstatus:%s %s" % (BRIGHT, RESET, label_switch(settings.speech_enabled)),
        "  %svoice:%s %s" % (BRIGHT, RESET, glb.settings.piper_voice),
        "%shearing:%s" % (BOLD_BRIGHT, RESET),
        "  %sstatus:%s %s" % (BRIGHT, RESET, label_switch(settings.hearing_enabled)),
        "  %smodel:%s %s" % (BRIGHT, RESET, settings.whisper_size or "null"),
        "%sconsumption:%s" % (BOLD_BRIGHT, RESET),
        "  %sprompt tokens:%s %s" % (BRIGHT, RESET, settings.prompt_tokens),
        "  %scompletion tokens:%s %s" % (BRIGHT, RESET, settings.completion_tokens),
        "  %smemory:%s %.2f%%" % (BRIGHT, RESET, mem_per),
    ]
    write("\n".join(lines))


def display_commands():
    """Displays the available commands."""
    lines = [
        "%s%s%s to turn features on or off" % (BOLD_BRIGHT, c.CMD_TOGGLE, RESET),
        "  %s%s %s%s to toggle the assistant's speech"
        % (BRIGHT, c.CMD_TOGGLE, c.TOGGLABLE_SPEECH, RESET),
        (
            "  %s%s %s%s to toggle the use of conversation"
            " history for coherent responses"
        )
        % (BRIGHT, c.CMD_TOGGLE, c.TOGGLABLE_CONTEXT, RESET),
        "  %s%s %s%s to toggle the assistant's ability to hear you"
        % (BRIGHT, c.CMD_TOGGLE, c.TOGGLABLE_HEARING, RESET),
        "%s%s%s for selecting from available models and voices"
        % (BOLD_BRIGHT, c.CMD_SELECT, RESET),
        "  %s%s %s%s to select the language model provider"
        % (BRIGHT, c.CMD_SELECT, c.SELECTABLE_LM_PROVIDER, RESET),
        "  %s%s %s%s to select the model for generating responses"
        % (BRIGHT, c.CMD_SELECT, c.SELECTABLE_LANG_MODEL, RESET),
        "  %s%s %s%s to select the assistant's voice"
        % (BRIGHT, c.CMD_SELECT, c.SELECTABLE_VOICE, RESET),
        "  %s%s %s%s to select the model interpreting speech"
        % (BRIGHT, c.CMD_SELECT, c.SELECTABLE_WHISPER_MODEL, RESET),
        "%s%s%s to set the LLM API key for the selected provider"
        % (BOLD_BRIGHT, c.CMD_KEY, RESET),
        "%s%s%s to instruct the model to behave a certain way"
        % (BOLD_BRIGHT, c.CMD_INSTRUCT, RESET),
        "%s%s%s to display status and settings" % (BOLD_BRIGHT, c.CMD_STATUS, RESET),
        "%s%s%s to mute the assistant" % (BOLD_BRIGHT, c.CMD_MUTE, RESET),
        "%s%s%s to launch a shell session" % (BOLD_BRIGHT, c.CMD_CMD, RESET),
        "%s%s%s to print this help message" % (BOLD_BRIGHT, c.CMD_COMMANDS, RESET),
        "%s%s%s to clear the terminal" % (BOLD_BRIGHT, c.CMD_CLEAR, RESET),
        "%s%s%s to exit" % (BOLD_BRIGHT, c.CMD_EXIT, RESET),
    ]
    write("\n".join(lines))


def handle_exit():
    glb.settings.dump_to_cache()
    if glb.listener is not None:
        glb.settings.disable_hearing()


def handle_command(words: list[str]):
    """handles words as command."""
    command = words[0]

    if command == c.CMD_SELECT:
        handle_select(words[1:])
    elif command == c.CMD_TOGGLE:
        handle_toggle(words[1:])
    elif command == c.CMD_KEY:
        glb.settings.set_key()
    elif command == c.CMD_INSTRUCT:
        glb.settings.instruct_lm()
    elif command == c.CMD_STATUS:
        display_status()
    elif command == c.CMD_MUTE:
        speech.mute()
    elif command == c.CMD_CMD:
        handle_cmd()
    elif command == c.CMD_COMMANDS:
        display_commands()
    elif command == c.CMD_CLEAR:
        clear()
    elif command == c.CMD_EXIT:
        handle_exit()


def run_query(query: str):
    if len(query.strip()) > 0:
        if is_shell_command(query):
            with sync.stdout_lock:
                subprocess.call(query[1:].lstrip(), shell=True)
        elif is_command(query):
            try:
                words = shlex.split(query)
                cmd_word = words[0]
                if command_exists(cmd_word):
                    handle_command(words)
                else:
                    handle_misspell(cmd_word)
            except ValueError:
                write("invalid command")
        else:
            handle_lm_response(lm.ask(query))
