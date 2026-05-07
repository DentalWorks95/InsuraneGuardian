import sqlite3
from datetime import datetime

def log_action(username, action, details):
    conn = sqlite3.connect("insurance_guardian.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS audit_log (id INTEGER PRIMARY KEY, username TEXT, action TEXT, details TEXT, timestamp TEXT)")
    cursor.execute("INSERT INTO audit_log (username, action, details, timestamp) VALUES (?, ?, ?, ?)", (username, action, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
