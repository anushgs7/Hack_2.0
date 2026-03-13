import csv
import os
from pathlib import Path


# --------------------------------------------------
# File Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "Database"

APP_TRACKER_FILE = DATABASE_DIR / "app_tracker.csv"
AFK_TRACKER_FILE = DATABASE_DIR / "afk_tracker.csv"
ATTENTION_TRACKER_FILE = DATABASE_DIR / "attention_tracker.csv"
SESSION_METADATA_FILE = DATABASE_DIR / "session_metadata.csv"


# --------------------------------------------------
# CSV Schemas
# --------------------------------------------------

APP_TRACKER_SCHEMA = [
    "user_email",
    "session_id",
    "app_name",
    "start_time",
    "end_time",
    "duration_seconds",
    "switch_event"
]

AFK_TRACKER_SCHEMA = [
    "user_email",
    "session_id",
    "idle_start_time",
    "idle_end_time",
    "idle_duration_seconds"
]

ATTENTION_TRACKER_SCHEMA = [
    "user_email",
    "session_id",
    "timestamp",
    "active_app",
    "attention_state",
    "event_type",
    "fragmentation_marker"
]

SESSION_METADATA_SCHEMA = [
    "user_email",
    "session_id",
    "session_start_time",
    "session_end_time",
    "total_duration_seconds"
]


# --------------------------------------------------
# Internal Utility
# --------------------------------------------------

def _ensure_file(file_path, schema):
    """
    Ensure CSV file exists and has header.
    """
    os.makedirs(DATABASE_DIR, exist_ok=True)

    if not os.path.exists(file_path):
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(schema)


# --------------------------------------------------
# Initialization
# --------------------------------------------------

def initialize_database():
    """
    Ensure all database files exist with correct headers.
    """
    _ensure_file(APP_TRACKER_FILE, APP_TRACKER_SCHEMA)
    _ensure_file(AFK_TRACKER_FILE, AFK_TRACKER_SCHEMA)
    _ensure_file(ATTENTION_TRACKER_FILE, ATTENTION_TRACKER_SCHEMA)
    _ensure_file(SESSION_METADATA_FILE, SESSION_METADATA_SCHEMA)


# --------------------------------------------------
# Write Operations
# --------------------------------------------------

def append_app_session(row_dict):
    """
    Append application session record.
    """
    with open(APP_TRACKER_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=APP_TRACKER_SCHEMA)
        writer.writerow(row_dict)


def append_afk_session(row_dict):
    """
    Append idle/AFK session record.
    """
    with open(AFK_TRACKER_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=AFK_TRACKER_SCHEMA)
        writer.writerow(row_dict)


def append_attention_event(row_dict):
    """
    Append processed attention event.
    """
    with open(ATTENTION_TRACKER_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ATTENTION_TRACKER_SCHEMA)
        writer.writerow(row_dict)


def append_session_metadata(row_dict):
    """
    Append session metadata.
    """
    with open(SESSION_METADATA_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SESSION_METADATA_SCHEMA)
        writer.writerow(row_dict)


# --------------------------------------------------
# Read Operations
# --------------------------------------------------

def read_app_sessions(user_email=None, session_id=None):
    """
    Read app session data optionally filtered by user/session.
    """
    return _read_filtered(APP_TRACKER_FILE, user_email, session_id)


def read_afk_sessions(user_email=None, session_id=None):
    """
    Read AFK session data optionally filtered by user/session.
    """
    return _read_filtered(AFK_TRACKER_FILE, user_email, session_id)


def read_attention_sessions(user_email=None, session_id=None):
    """
    Read attention analysis data.
    """
    return _read_filtered(ATTENTION_TRACKER_FILE, user_email, session_id)


def read_session_metadata(user_email=None, session_id=None):
    """
    Read session metadata.
    """
    return _read_filtered(SESSION_METADATA_FILE, user_email, session_id)


# --------------------------------------------------
# Shared Filtering Utility
# --------------------------------------------------

def _read_filtered(file_path, user_email=None, session_id=None):
    """
    Read CSV and filter by user_email and/or session_id.
    """
    if not os.path.exists(file_path):
        return []

    results = []

    with open(file_path, "r", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if user_email and row["user_email"] != user_email:
                continue

            if session_id and row["session_id"] != session_id:
                continue

            results.append(row)

    return results
