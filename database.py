<<<<<<< HEAD
import sqlite3
import os
from datetime import datetime, date
import json
import numpy as np
import io
import config


# Fix DeprecationWarning for default date adapters
def adapt_date(val):
    return val.isoformat()


def convert_date(val):
    return date.fromisoformat(val.decode())


sqlite3.register_adapter(date, adapt_date)
sqlite3.register_converter("date", convert_date)


def get_connection():
    """Create a database connection."""
    conn = sqlite3.connect(config.DB_FILE, check_same_thread=False)
    return conn


def init_db():
    """Initialize the database tables."""
    conn = get_connection()
    c = conn.cursor()

    # Staff Table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            mobile_number TEXT,
            email TEXT,
            department TEXT,
            role TEXT,
            face_encoding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Attendance Table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id TEXT NOT NULL,
            punch_date DATE NOT NULL,
            in_time TIME,
            out_time TIME,
            status TEXT,
            late_min INTEGER DEFAULT 0,
            FOREIGN KEY (staff_id) REFERENCES staff (staff_id),
            UNIQUE(staff_id, punch_date)
        )
    """
    )

    # Counters Table (Monthly Reset)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS counters (
            staff_id TEXT NOT NULL,
            month_str TEXT NOT NULL,
            grace_count INTEGER DEFAULT 0,
            late_count INTEGER DEFAULT 0,
            permission_count INTEGER DEFAULT 0,
            PRIMARY KEY (staff_id, month_str),
            FOREIGN KEY (staff_id) REFERENCES staff (staff_id)
        )
    """
    )

    conn.commit()
    conn.close()
    print("Database initialized.")


def adapt_array(arr):
    """
    Convert numpy array to binary for SQLite storage.
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


# Register SQLite adapters for numpy arrays (face encodings)
sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)

if __name__ == "__main__":
    init_db()
=======
import sqlite3
import os
from datetime import datetime, date
import json
import numpy as np
import io
import config


# Fix DeprecationWarning for default date adapters
def adapt_date(val):
    return val.isoformat()


def convert_date(val):
    return date.fromisoformat(val.decode())


sqlite3.register_adapter(date, adapt_date)
sqlite3.register_converter("date", convert_date)


def get_connection():
    """Create a database connection."""
    conn = sqlite3.connect(config.DB_FILE, check_same_thread=False)
    return conn


def init_db():
    """Initialize the database tables."""
    conn = get_connection()
    c = conn.cursor()

    # Staff Table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            mobile_number TEXT,
            email TEXT,
            department TEXT,
            role TEXT,
            face_encoding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Attendance Table
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id TEXT NOT NULL,
            punch_date DATE NOT NULL,
            in_time TIME,
            out_time TIME,
            status TEXT,
            late_min INTEGER DEFAULT 0,
            FOREIGN KEY (staff_id) REFERENCES staff (staff_id),
            UNIQUE(staff_id, punch_date)
        )
    """
    )

    # Counters Table (Monthly Reset)
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS counters (
            staff_id TEXT NOT NULL,
            month_str TEXT NOT NULL,
            grace_count INTEGER DEFAULT 0,
            late_count INTEGER DEFAULT 0,
            permission_count INTEGER DEFAULT 0,
            PRIMARY KEY (staff_id, month_str),
            FOREIGN KEY (staff_id) REFERENCES staff (staff_id)
        )
    """
    )

    conn.commit()
    conn.close()
    print("Database initialized.")


def adapt_array(arr):
    """
    Convert numpy array to binary for SQLite storage.
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)


# Register SQLite adapters for numpy arrays (face encodings)
sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("array", convert_array)

if __name__ == "__main__":
    init_db()
>>>>>>> f56354bff23c57e9dbb309990488effecb6c4ad5
