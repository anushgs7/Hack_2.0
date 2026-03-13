import dbus
import time
from datetime import datetime

from Attention_Engine.Database import append_afk_session


# --------------------------------------------------
# Idle Threshold (seconds)
# --------------------------------------------------

IDLE_THRESHOLD = 5


# --------------------------------------------------
# DBus Idle Monitor
# --------------------------------------------------

def _get_idle_time_seconds():
    """
    Returns idle time in seconds using GNOME Mutter IdleMonitor.
    """

    bus = dbus.SessionBus()

    obj = bus.get_object(
        "org.gnome.Mutter.IdleMonitor",
        "/org/gnome/Mutter/IdleMonitor/Core"
    )

    iface = dbus.Interface(
        obj,
        "org.gnome.Mutter.IdleMonitor"
    )

    idle_ms = iface.GetIdletime()

    return idle_ms / 1000.0


# --------------------------------------------------
# Tracker Class
# --------------------------------------------------

class IdleTimeTracker:

    def __init__(self, user_email, session_id):

        self.user_email = user_email
        self.session_id = session_id

        self.running = False

        self.idle_active = False
        self.idle_start_time = None

    # --------------------------------------------------

    def start(self):
        """
        Start idle monitoring loop.
        """

        self.running = True

        while self.running:

            idle_seconds = _get_idle_time_seconds()

            now = datetime.now()

            # ------------------------------------------
            # Detect Idle Start
            # ------------------------------------------

            if idle_seconds >= IDLE_THRESHOLD and not self.idle_active:

                self.idle_active = True
                self.idle_start_time = now

            # ------------------------------------------
            # Detect Idle End
            # ------------------------------------------

            if idle_seconds < IDLE_THRESHOLD and self.idle_active:

                idle_end_time = now

                duration = (idle_end_time - self.idle_start_time).total_seconds()

                append_afk_session({
                    "user_email": self.user_email,
                    "session_id": self.session_id,
                    "idle_start_time": self.idle_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "idle_end_time": idle_end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "idle_duration_seconds": int(duration)
                })

                self.idle_active = False
                self.idle_start_time = None

            time.sleep(2)

    # --------------------------------------------------

    def stop(self):
        """
        Stop tracker and close active idle session if needed.
        """

        self.running = False

        if self.idle_active:

            now = datetime.now()

            duration = (now - self.idle_start_time).total_seconds()

            append_afk_session({
                "user_email": self.user_email,
                "session_id": self.session_id,
                "idle_start_time": self.idle_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "idle_end_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "idle_duration_seconds": int(duration)
            })

            self.idle_active = False
            self.idle_start_time = None
