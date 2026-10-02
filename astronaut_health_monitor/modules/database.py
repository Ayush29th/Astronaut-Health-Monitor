import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'astronaut_health.db')

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Telemetry Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            heart_rate REAL,
            spo2 REAL,
            temperature REAL,
            blood_pressure_sys REAL,
            blood_pressure_dia REAL,
            respiratory_rate REAL,
            stress REAL,
            fatigue REAL,
            hydration REAL,
            sleep_score REAL,
            activity REAL,
            scenario TEXT
        )
    ''')
    
    # Environment Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS environment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            cabin_pressure REAL,
            co2 REAL,
            oxygen_level REAL,
            temperature REAL,
            humidity REAL,
            radiation REAL,
            scenario TEXT
        )
    ''')

    # Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            parameter TEXT,
            severity TEXT,
            value REAL,
            message TEXT,
            ai_explanation TEXT,
            recommendation TEXT,
            status TEXT DEFAULT 'ACTIVE'
        )
    ''')

    # Seed data if empty
    cursor.execute("SELECT COUNT(*) FROM telemetry")
    if cursor.fetchone()[0] == 0:
        seed_initial_data(conn)

    conn.commit()
    conn.close()

def seed_initial_data(conn):
    import random
    base_time = datetime.now() - timedelta(minutes=60)
    for i in range(60):
        t = base_time + timedelta(minutes=i)
        hr = round(72.0 + random.uniform(-1.5, 1.5), 2)
        spo2 = round(98.5 + random.uniform(-0.2, 0.2), 2)
        conn.execute('''
            INSERT INTO telemetry (
                timestamp, heart_rate, spo2, temperature, 
                blood_pressure_sys, blood_pressure_dia, 
                respiratory_rate, stress, fatigue, 
                hydration, sleep_score, activity, scenario
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (t.isoformat(), hr, spo2, 36.8, 118.0, 78.0, 14.0, 18.0, 12.0, 96.0, 88.0, 5.0, "Normal"))
        
        conn.execute('''
            INSERT INTO environment (
                timestamp, cabin_pressure, co2, oxygen_level, 
                temperature, humidity, radiation, scenario
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (t.isoformat(), 14.7, 400.0, 21.0, 22.0, 40.0, 0.5, "Normal"))
        
    conn.commit()

def save_telemetry(data: dict):
    conn = sqlite3.connect(DB_PATH)
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
    cols = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    sql = f'INSERT INTO telemetry ({cols}) VALUES ({placeholders})'
    conn.execute(sql, tuple(data.values()))
    conn.commit()
    conn.close()
    
def save_environment(data: dict):
    conn = sqlite3.connect(DB_PATH)
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
    cols = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    sql = f'INSERT INTO environment ({cols}) VALUES ({placeholders})'
    conn.execute(sql, tuple(data.values()))
    conn.commit()
    conn.close()

def save_alert(alert_data: dict):
    conn = sqlite3.connect(DB_PATH)
    if 'timestamp' not in alert_data:
        alert_data['timestamp'] = datetime.now().isoformat()
    cols = ', '.join(alert_data.keys())
    placeholders = ', '.join(['?'] * len(alert_data))
    sql = f'INSERT INTO alerts ({cols}) VALUES ({placeholders})'
    conn.execute(sql, tuple(alert_data.values()))
    conn.commit()
    conn.close()

def get_recent_telemetry(minutes=60):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM telemetry WHERE timestamp >= datetime('now', '-{minutes} minutes')", conn)
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def get_all_telemetry(limit=1000):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM telemetry ORDER BY timestamp DESC LIMIT {limit}", conn)
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
    return df

def get_active_alerts():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM alerts WHERE status != 'RESOLVED' ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def acknowledge_alert(alert_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE alerts SET status = 'ACKNOWLEDGED' WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

def resolve_alert(alert_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE alerts SET status = 'RESOLVED' WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()

def get_all_alerts(limit=1000):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM alerts ORDER BY timestamp DESC LIMIT {limit}", conn)
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def get_recent_environment(minutes=60):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM environment WHERE timestamp >= datetime('now', '-{minutes} minutes')", conn)
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def clear_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM telemetry")
    conn.execute("DELETE FROM environment")
    conn.execute("DELETE FROM alerts")
    conn.commit()
    conn.close()
