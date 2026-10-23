import json
import os

DB_FILE = "tasks.json"
BUSY_FILE = "busy.json"

def load_tasks():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tasks(tasks):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

def load_busy():
    if os.path.exists(BUSY_FILE):
        with open(BUSY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_busy(busy):
    with open(BUSY_FILE, "w", encoding="utf-8") as f:
        json.dump(busy, f, ensure_ascii=False, indent=4)