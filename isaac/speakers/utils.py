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
