import psutil
import time
from datetime import datetime

from Attention_Engine.Database import append_app_session


# --------------------------------------------------
# Applications To Track
# --------------------------------------------------

TARGET_APPS = [
    "firefox",
    "code",
    "nautilus",
    "steam",
    "mpv",
    "gnome-text-editor",
    "gnome-system-monitor",
    "gnome-calculator"
]


# --------------------------------------------------
# Utility
# --------------------------------------------------

def _get_running_apps():
    """
    Returns dictionary of currently running tracked apps.

    {app_name: pid}
    """
    running = {}

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            name = proc.info['name']

            if name and name.lower() in TARGET_APPS:
                running[name.lower()] = proc.info['pid']

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return running


# --------------------------------------------------
# Tracker Class
# --------------------------------------------------

class ActiveAppTracker:

    def __init__(self, user_email, session_id):

        self.user_email = user_email
        self.session_id = session_id

        self.running = False
        self.active_apps = {}

    # --------------------------------------------------

    def start(self):
        """
        Start application monitoring loop.
        """
        self.running = True

        while self.running:

            current_apps = _get_running_apps()

            now = datetime.now()

            # ------------------------------------------
            # Detect App Start
            # ------------------------------------------

            for app, pid in current_apps.items():

                if app not in self.active_apps:

                    self.active_apps[app] = {
                        "pid": pid,
                        "start_time": now
                    }

            # ------------------------------------------
            # Detect App Close
            # ------------------------------------------

            for app in list(self.active_apps.keys()):

                if app not in current_apps:

                    app_data = self.active_apps.pop(app)

                    start_time = app_data["start_time"]
                    end_time = now

                    duration = (end_time - start_time).total_seconds()

                    append_app_session({
                        "user_email": self.user_email,
                        "session_id": self.session_id,
                        "app_name": app,
                        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "duration_seconds": int(duration),
                        "switch_event": "FALSE"
                    })

            time.sleep(0.5)

    # --------------------------------------------------

    def stop(self):
        """
        Stop tracker and close active sessions.
        """
        self.running = False

        now = datetime.now()

        for app in list(self.active_apps.keys()):

            app_data = self.active_apps.pop(app)

            start_time = app_data["start_time"]
            end_time = now

            duration = (end_time - start_time).total_seconds()

            append_app_session({
                "user_email": self.user_email,
                "session_id": self.session_id,
                "app_name": app,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": int(duration),
                "switch_event": "FALSE"
            })
