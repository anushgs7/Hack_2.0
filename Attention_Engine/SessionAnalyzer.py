from datetime import datetime

from Attention_Engine.Database import (
    read_app_sessions,
    read_afk_sessions,
    append_attention_event
)


TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class SessionAnalyzer:

    def __init__(self, user_email, session_id):

        self.user_email = user_email
        self.session_id = session_id

    # --------------------------------------------------

    def analyze(self):
        """
        Perform session attention analysis.
        """

        app_sessions = read_app_sessions(self.user_email, self.session_id)
        afk_sessions = read_afk_sessions(self.user_email, self.session_id)

        events = []

        # --------------------------------------------------
        # App Events
        # --------------------------------------------------

        for app in app_sessions:

            start_time = datetime.strptime(app["start_time"], TIME_FORMAT)
            end_time = datetime.strptime(app["end_time"], TIME_FORMAT)

            duration = int(app["duration_seconds"])

            fragmentation = "TRUE" if duration < 15 else "FALSE"

            events.append({
                "timestamp": start_time,
                "active_app": app["app_name"],
                "attention_state": "ACTIVE",
                "event_type": "APP_START",
                "fragmentation_marker": fragmentation
            })

            events.append({
                "timestamp": end_time,
                "active_app": app["app_name"],
                "attention_state": "ACTIVE",
                "event_type": "APP_END",
                "fragmentation_marker": "FALSE"
            })

        # --------------------------------------------------
        # AFK Events
        # --------------------------------------------------

        for afk in afk_sessions:

            start_time = datetime.strptime(afk["idle_start_time"], TIME_FORMAT)
            end_time = datetime.strptime(afk["idle_end_time"], TIME_FORMAT)

            events.append({
                "timestamp": start_time,
                "active_app": "NONE",
                "attention_state": "IDLE",
                "event_type": "AFK_START",
                "fragmentation_marker": "TRUE"
            })

            events.append({
                "timestamp": end_time,
                "active_app": "NONE",
                "attention_state": "ACTIVE",
                "event_type": "AFK_END",
                "fragmentation_marker": "FALSE"
            })

        # --------------------------------------------------
        # Sort Events
        # --------------------------------------------------

        events.sort(key=lambda x: x["timestamp"])

        # --------------------------------------------------
        # Detect App Switches
        # --------------------------------------------------

        last_app = None
        last_time = None

        for event in events:

            if event["event_type"] == "APP_START":

                current_app = event["active_app"]

                if last_app and current_app != last_app:

                    delta = (event["timestamp"] - last_time).total_seconds()

                    fragmentation = "TRUE" if delta < 10 else "FALSE"

                    append_attention_event({
                        "user_email": self.user_email,
                        "session_id": self.session_id,
                        "timestamp": event["timestamp"].strftime(TIME_FORMAT),
                        "active_app": current_app,
                        "attention_state": "SWITCH",
                        "event_type": "APP_SWITCH",
                        "fragmentation_marker": fragmentation
                    })

                last_app = current_app
                last_time = event["timestamp"]

            append_attention_event({
                "user_email": self.user_email,
                "session_id": self.session_id,
                "timestamp": event["timestamp"].strftime(TIME_FORMAT),
                "active_app": event["active_app"],
                "attention_state": event["attention_state"],
                "event_type": event["event_type"],
                "fragmentation_marker": event["fragmentation_marker"]
            })
