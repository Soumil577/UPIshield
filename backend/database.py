"""
SQLite Database Connection and Schema Management for SIH26184.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sih_cybercrime.db")


def get_db_connection() -> sqlite3.Connection:
    """Creates and returns a thread-safe connection to the SQLite database with Row factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initializes SQLite schema for complaints, cases, transactions, locations, cashouts, and alerts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        bank TEXT NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        cctv_available INTEGER NOT NULL,
        historical_fraud_count INTEGER NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        total_amount_lost REAL NOT NULL,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL,
        primary_mule_account TEXT,
        primary_mule_upi TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        victim_name TEXT NOT NULL,
        victim_phone TEXT NOT NULL,
        victim_upi TEXT NOT NULL,
        victim_account TEXT NOT NULL,
        victim_bank TEXT NOT NULL,
        fraud_category TEXT NOT NULL,
        reported_amount REAL NOT NULL,
        incident_time TEXT NOT NULL,
        reported_time TEXT NOT NULL,
        status TEXT NOT NULL,
        city TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        sender_id TEXT NOT NULL,
        sender_type TEXT NOT NULL,
        receiver_id TEXT NOT NULL,
        receiver_type TEXT NOT NULL,
        amount REAL NOT NULL,
        timestamp TEXT NOT NULL,
        device_id TEXT,
        ip_address TEXT,
        location TEXT,
        layer_index INTEGER NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historical_cashouts (
        id TEXT PRIMARY KEY,
        location_id TEXT NOT NULL,
        amount REAL NOT NULL,
        withdrawal_time TEXT NOT NULL,
        distance_from_last_hop_km REAL NOT NULL,
        mule_account_id TEXT NOT NULL,
        successful INTEGER NOT NULL,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        case_title TEXT NOT NULL,
        priority TEXT NOT NULL,
        target_agencies TEXT NOT NULL,
        predicted_locations TEXT NOT NULL,
        dispatched_at TEXT NOT NULL,
        status TEXT NOT NULL,
        action_code TEXT NOT NULL,
        summary TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases(id)
    );
    """)

    conn.commit()
    conn.close()
