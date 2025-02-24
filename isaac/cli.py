import time
import shlex
import queue
import threading

try:
    import readline
except ImportError:
    import pyreadline3 as readline

from typing import Optional
import isaac.constants as c
import isaac.command as command
import isaac.globals as glb
from isaac.settings import Settings
from isaac.utils import clear, write, print_welcome


def query_hadler():
    while not glb.event_exit.is_set():
        try:
            query, event = glb.query_queue.get(timeout=1)
        except queue.Empty:
            continue
        try:
            if query == c.CMD_EXIT:
                glb.event_exit.set()
                event.set()
            command.run_query(query)
        finally:
            if query != c.CMD_EXIT:
                event.set()


def command_completer(text: str, state: int) -> Optional[str]:
    """handles auto-completion of commands and their arguments."""
    text = readline.get_line_buffer().lstrip()
    if not command.is_command(text):
        return
    words = shlex.split(text)
    if len(words) > 2:
        return
    cmd_word = words[0]
    if not command.command_exists(cmd_word):
        if len(words) == 1:
            options = [cmd for cmd in c.commands if cmd.startswith(cmd_word)]
            return options[state] if state < len(options) else None
        return None
    if cmd_word not in c.command_args:
        return
    arg = words[1] if len(words) == 2 else ""
    options = [option for option in c.command_args[cmd_word] if option.startswith(arg)]
    return options[state] if state < len(options) else None


def main():
    """starts the REPL loop."""
    readline.set_completer(command_completer)
    readline.parse_and_bind("tab: complete")

    clear()
    print_welcome()
    glb.settings = Settings()
    glb.settings.enact()
    query_thread = threading.Thread(target=query_hadler)
    event_completion = threading.Event()
    query_thread.start()

    while True:
        try:
            if glb.settings.hearing_enabled:
                write(">> ", end="")
            while glb.settings.hearing_enabled:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
            if glb.event_exit.is_set():
                return
            query = input("" if glb.settings.hearing_enabled else ">> ")
            glb.query_queue.put((query.strip(), event_completion))
            event_completion.wait()
            if glb.event_exit.is_set():
                return
            event_completion.clear()
        except KeyboardInterrupt:
            write("\r", end="")
