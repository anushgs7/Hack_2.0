import os
from collections import defaultdict

from openai import OpenAI

from Attention_Engine.Database import (
    read_app_sessions,
    read_afk_sessions,
    read_attention_sessions,
    read_session_metadata
)


REPORT_FILE = "session_report.txt"


class ReportGenerator:

    def __init__(self, user_email, session_id):

        self.user_email = user_email
        self.session_id = session_id

    # --------------------------------------------------

    def generate(self):
        """
        Generate attention report using ChatGPT API.
        """

        app_data = read_app_sessions(self.user_email, self.session_id)
        afk_data = read_afk_sessions(self.user_email, self.session_id)
        attention_data = read_attention_sessions(self.user_email, self.session_id)
        metadata = read_session_metadata(self.user_email, self.session_id)

        payload = self._build_payload(app_data, afk_data, attention_data, metadata)

        report_text = self._generate_ai_report(payload)

        with open(REPORT_FILE, "w") as f:
            f.write(report_text)

        return REPORT_FILE

    # --------------------------------------------------

    def _build_payload(self, app_data, afk_data, attention_data, metadata):

        total_idle = sum(int(x["idle_duration_seconds"]) for x in afk_data)

        app_usage = defaultdict(int)

        for app in app_data:
            app_usage[app["app_name"]] += int(app["duration_seconds"])

        fragmentation_events = sum(
            1 for x in attention_data if x["fragmentation_marker"] == "TRUE"
        )

        switch_events = sum(
            1 for x in attention_data if x["event_type"] == "APP_SWITCH"
        )

        session_info = metadata[0] if metadata else {}

        payload = {
            "session_info": session_info,
            "total_idle_seconds": total_idle,
            "app_usage_seconds": dict(app_usage),
            "fragmentation_events": fragmentation_events,
            "switch_events": switch_events,
            "attention_event_count": len(attention_data)
        }

        return payload

    # --------------------------------------------------

    def _generate_ai_report(self, payload):

        api_key = os.getenv("OPENAI_API_KEY")

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are analyzing an offline human attention mapping session.

The system only tracks interaction signals. It does not evaluate productivity.

Provide a neutral analysis of the session attention flow.

Session Data:
{payload}

Write a concise attention report describing:

- session duration
- idle distribution
- application usage patterns
- attention shifts
- fragmentation events
- overall attention flow
"""

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )

        return response.output_text
