import isaac.sync as sync


def mute():
    """
    sets the `event_mute` event that signals the speaker thread to stop
    speaking.
    """
    sync.event_mute.set()


def unmute():
    """
    clears the 'event_mute' event that signals speaker thread to stop.
    """
    sync.event_mute.clear()


def pre_speech():
    if sync.speech_thread and sync.speech_thread.is_alive():
        mute()
        sync.speech_thread.join()
    unmute()
