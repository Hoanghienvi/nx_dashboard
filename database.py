import sqlite3
import time
import json
from datetime import datetime

DB_NAME = "nx_dashboard.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Bảng lưu trữ Audit Log (Tăng tốc độ load)
    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  action TEXT, 
                  time_sec INTEGER, 
                  ip TEXT, 
                  details TEXT,
                  UNIQUE(username, action, time_sec))''')
    
    # 2. Bảng theo dõi thời gian sử dụng (Quota)
    c.execute('''CREATE TABLE IF NOT EXISTS user_usage
                 (username TEXT PRIMARY KEY, 
                  total_seconds INTEGER DEFAULT 0, 
                  last_active_ts INTEGER DEFAULT 0,
                  last_reset_date TEXT)''')
                  
    conn.commit()
    conn.close()

def save_audit_logs(logs):
    if not logs: return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for log in logs:
        try:
            # Chỉ insert nếu chưa tồn tại (nhờ UNIQUE constraint)
            c.execute("INSERT OR IGNORE INTO audit_logs (username, action, time_sec, ip, details) VALUES (?, ?, ?, ?, ?)",
                      (log['username'], log['action'], log['time'], log['ip'], log['details']))
        except: pass
    conn.commit()
    conn.close()

def get_user_logs(username, limit=100):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM audit_logs WHERE username=? ORDER BY time_sec DESC LIMIT ?", (username, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_user_usage(username, current_ts):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    today_str = datetime.fromtimestamp(current_ts).strftime('%Y-%m-%d')
    
    c.execute("SELECT total_seconds, last_active_ts, last_reset_date FROM user_usage WHERE username=?", (username,))
    row = c.fetchone()
    
    if not row:
        # User mới
        c.execute("INSERT INTO user_usage VALUES (?, 0, ?, ?)", (username, current_ts, today_str))
        used = 0
    else:
        total_sec, last_ts, last_date = row
        
        # Reset nếu sang ngày mới
        if last_date != today_str:
            total_sec = 0
            last_date = today_str
            
        # Tính thời gian online: Nếu lần cuối hoạt động cách đây < 5 phút (300s) thì cộng dồn
        diff = current_ts - last_ts
        if 0 < diff < 300: 
            total_sec += diff
            
        c.execute("UPDATE user_usage SET total_seconds=?, last_active_ts=?, last_reset_date=? WHERE username=?",
                  (total_sec, current_ts, last_date, username))
        used = total_sec
        
    conn.commit()
    conn.close()
    return used