from isaac.listeners import ListenerInterface, ListenOptions


class PyListener(ListenerInterface):
    def __init__(
        self,
        whisper_size: str,
        options: ListenOptions = ListenOptions(time_window_s=3),
    ):
        super().__init__(options)

        from listener import Listener

        self.py_listener = Listener(
            time_window=options.time_window_s,
            speech_handler=options.speech_handler,
            on_speech_start=options.on_speech_start,
            whisper_size=whisper_size,
            en_only=options.en_only,
            # show_download=False
        )

    def listen(self):
        self.py_listener.listen()

    def close(self):
        self.py_listener.close()

    def pause(self):
        self.py_listener.pause()

    def resume(self):
        self.py_listener.resume()
