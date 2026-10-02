import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Set
from config.settings import DB_PATH, TRACKER_CSV_PATH

def init_tracker_db(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outreach_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer TEXT NOT NULL,
            email TEXT NOT NULL,
            platform TEXT,
            channel TEXT,
            message_generated TEXT NOT NULL,
            sent TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            collaboration_angle TEXT,
            detail TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_contacted_emails(db_path: Path = DB_PATH) -> Set[str]:
    init_tracker_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT LOWER(email) FROM outreach_log WHERE sent = 'Yes' AND email != 'Not Found'")
    rows = cursor.fetchall()
    conn.close()
    return {r[0] for r in rows if r[0]}

def log_outreach_entry(entry: Dict[str, Any], db_path: Path = DB_PATH) -> None:
    init_tracker_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO outreach_log (
            influencer, email, platform, channel, message_generated,
            sent, date, status, collaboration_angle, detail
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry.get("influencer", ""),
        entry.get("email", ""),
        entry.get("platform", "Instagram"),
        entry.get("channel", "Email"),
        entry.get("message_generated", "Yes"),
        entry.get("sent", "No"),
        entry.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        entry.get("status", "PENDING"),
        entry.get("collaboration_angle", ""),
        entry.get("detail", "")
    ))
    conn.commit()
    conn.close()

def fetch_all_outreach_logs(db_path: Path = DB_PATH) -> List[Dict[str, Any]]:
    init_tracker_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT influencer, email, platform, channel, message_generated,
               sent, date, status, collaboration_angle, detail
        FROM outreach_log
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    logs = []
    for r in rows:
        logs.append({
            "Influencer": r[0],
            "Email": r[1],
            "Platform": r[2],
            "Channel": r[3],
            "Message Generated": r[4],
            "Sent": r[5],
            "Date": r[6],
            "Status": r[7],
            "Collaboration Angle": r[8],
            "Detail": r[9]
        })
    return logs

def export_outreach_tracker_csv(records: List[Dict[str, Any]], csv_path: Path = TRACKER_CSV_PATH) -> Path:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    return csv_path
