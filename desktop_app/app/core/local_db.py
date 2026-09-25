import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "local_state.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS offline_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_mac TEXT,
            ssid TEXT,
            bssids TEXT,
            timestamp TEXT,
            synced INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def save_offline_checkin(device_mac: str, ssid: str, bssids: list):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO offline_checkins (device_mac, ssid, bssids, timestamp) VALUES (?, ?, ?, ?)",
        (device_mac, ssid, json.dumps(bssids), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_unsynced_checkins():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, device_mac, ssid, bssids, timestamp FROM offline_checkins WHERE synced = 0")
    rows = c.fetchall()
    conn.close()
    return rows

def mark_as_synced(checkin_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE offline_checkins SET synced = 1 WHERE id = ?", (checkin_id,))
    conn.commit()
    conn.close()

# Inicia as tabelas assim que for importado
init_db()
