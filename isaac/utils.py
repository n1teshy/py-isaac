import os
import platform
import re
import socket
from typing import Optional, Union

from rich.console import Console, ConsoleOptions
from rich.markdown import Markdown
from rich.segment import Segment
from yapper import PiperVoiceGB, PiperVoiceUS

import isaac.constants as c
import isaac.globals as glb
import isaac.speech as speech
import isaac.sync as sync
import isaac.theme as theme

rich_console = Console()


def clear():
    """
    clears the screen.
    """
    os.system("cls" if platform.system() == "Windows" else "clear")


def write(*args, **kwargs):
    """
    prints the given text on the screen with a lock that prevents
    the listener thread from interrupting it.
    """
    with sync.stdout_lock:
        print(*args, **kwargs, flush=True)


def label_switch(switch: bool):
    """
    return a string that prints the given boolean switch on the screen
    in color.
    """
    label = "on" if switch else "off"
    pre = theme.GREEN if switch else theme.RED
    label = pre + label + theme.RESET
    return label


def print_welcome():
    """Prints the welcome message on the screen."""
    banner = """
%s ___   ____      _         _      ____
|_ _| / ___|    / \       / \    / ___|
 | |  \___ \   / _ \     / _ \  | |
 | | _ ___) | / ___ \ _ / ___ \ | |___
|___(_)____(_)_/   \_(_)_/   \_(_)____|%s"""
    message = banner + "   type %s%s%s to see commands.\n"
    message = message % (
        theme.BRIGHT,
        theme.RESET,
        theme.BOLD_BRIGHT,
        c.CMD_COMMANDS,
        theme.RESET,
    )
    print(message)


def get_piper_voice_enum(str_voice: str) -> Union[PiperVoiceUS, PiperVoiceGB]:
    """
    takes stringified name of a piper voice and return the matching attribute
    from enum `PiperVoiceUS` or `PiperVoiceGB`.
    """
    for voice_enum in list(PiperVoiceUS) + list(PiperVoiceGB):
        if voice_enum.value == str_voice:
            return voice_enum


def safe_input(message: str) -> str:
    try:
        if glb.listener is not None:
            glb.listener.pause()
        with sync.stdout_lock:
            return input(message)
    finally:
        if glb.listener is not None:
            glb.listener.resume()


def select_from(
    options: list[str],
    prompt: Optional[str] = None,
    allow_none: bool = True,
    none_label: str = "none",
) -> int:
    """
    Displays indexed options on the screen and lets the user select
    one by typing its index.
    """
    if allow_none:
        options += [none_label]
    options = [f"{idx}: {option}" for idx, option in enumerate(options)]
    if prompt is not None:
        write(theme.BOLD_BRIGHT + prompt + theme.RESET)
    write("\n".join(options))
    while True:
        idx = safe_input("select by typing the index: ").strip()
        try:
            idx = int(idx)
            if idx >= len(options):
                raise ValueError()
        except ValueError:
            write("invalid option")
            continue
        if allow_none and idx == len(options) - 1:
            return -1
        write()
        return idx


def normalize_md(text: str) -> str:
    """
    Detects code blocks in markdown text and replaces the code with
    "you can see the code on the screen", replacs 'code' with specific
    language if it can be detected.
    """

    def replacer(match):
        match = re.search("```(\w+).*", text)
        repl = match.group(1) if match else "the code"
        return f"you can see {repl} on the screen. "

    text = re.sub(r"```.*?```", replacer, text, flags=re.DOTALL)
    text = re.sub(r"#+ ", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    return text


def check_internet():
    try:
        socket.getaddrinfo("google.com", 80)
        return True
    except OSError:
        return False


def handle_lm_response(response: str):
    """
    prints the response on the screen, normalizes and speaks it.
    """
    with sync.stdout_lock:
        rich_console.print(CustomMarkdown(response))
    if glb.settings.speech_enabled:
        speech.say(normalize_md(response))


class CustomMarkdown(Markdown):
    """
    rich.markdown.Markdown prepends a leading space character before lines of
    code, that makes the code clearer to read but it becomes difficult to just
    copy it from the console and paste because of the leading space, this
    class detects those leading spaces, and moves them with sequence of spaces
    or before the next newline character, makes code easy to copy and paste.
    """

    def __rich_console__(self, console: Console, options: ConsoleOptions):
        rows: list[list[Segment]] = [[]]
        bg_style = None
        for seg in super().__rich_console__(console, options):
            rows[-1].append(seg)
            if (
                bg_style is None
                and seg.style
                and seg.style.bgcolor
                and seg.text.strip(" ") == ""
            ):
                bg_style = seg.style
            if seg.text.endswith("\n"):
                rows.append([])

        rows = rows[:-1] if len(rows[-1]) == 0 else rows

        for row_idx in range(len(rows)):
            row = rows[row_idx]
            if (
                not row[0].text.startswith(" ")
                or row[0].text.count(" ") == options.max_width
            ):
                continue
            if row[0].text == " ":
                rows[row_idx] = row = row[1:]
            else:
                segment = Segment(row[0].text[1:], row[0].style, row[0].control)
                rows[row_idx][0] = row[0] = segment
            rows[row_idx] = row[:-1] + [Segment(" ", style=bg_style)] + [row[-1]]

        for segment in [s for row in rows for s in row]:
            yield segment
