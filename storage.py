# storage.py
import json
import os

DATA_FILE = "tasks.json"

def load_data():
    """Load tasks from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        print("⚠️  Data file was corrupted. Starting fresh.")
        return []

def save_data(tasks):
    """Save tasks to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def get_weekly_stats():
    """
    Returns how many tasks were completed per day
    for the last 7 days — used for the weekly chart.
    """
    from datetime import datetime, timedelta

    tasks    = load_data()
    today    = datetime.today().date()
    stats    = {}

    # Build a dict for the last 7 days with 0 as default
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        stats[str(day)] = {"completed": 0, "added": 0}

    for task in tasks:
        # Count tasks added per day
        if "created" in task:
            created_date = task["created"][:10]  # "2026-04-24"
            if created_date in stats:
                stats[created_date]["added"] += 1

        # Count tasks completed per day
        if task.get("done") and "completed_at" in task:
            completed_date = task["completed_at"][:10]
            if completed_date in stats:
                stats[completed_date]["completed"] += 1

    return stats