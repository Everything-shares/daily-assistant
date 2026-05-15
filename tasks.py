# tasks.py — full updated file

from datetime import datetime
from storage import load_data, save_data

def get_all_tasks():
    return load_data()

def show_tasks():
    tasks = get_all_tasks()
    today = datetime.today().strftime("%A, %B %d %Y")
    print(f"\n{'='*45}")
    print(f"  📋 YOUR TASKS — {today}")
    print(f"{'='*45}")
    if not tasks:
        print("  No tasks yet! Add your first task. 🚀")
    else:
        pending = [t for t in tasks if not t["done"]]
        done    = [t for t in tasks if t["done"]]
        if pending:
            print("\n  ⬜ PENDING:")
            for task in pending:
                print(f"     [{task['id']}] {task['text']}")
        if done:
            print("\n  ✅ COMPLETED:")
            for task in done:
                print(f"     [{task['id']}] {task['text']}")
    print(f"{'='*45}\n")

def add_task(text):
    tasks = get_all_tasks()
    new_task = {
        "id":         len(tasks) + 1,
        "text":       text,
        "done":       False,
        "created":    str(datetime.now()),
        "completed_at": None           # ← NEW: will be filled when done
    }
    tasks.append(new_task)
    save_data(tasks)

def complete_task(task_id):
    tasks = get_all_tasks()
    found = False
    for task in tasks:
        if task["id"] == task_id:
            task["done"]         = True
            task["completed_at"] = str(datetime.now())  # ← record the time!
            found = True
            break
    if not found:
        return
    save_data(tasks)

def delete_task(task_id):
    tasks    = get_all_tasks()
    new_list = [t for t in tasks if t["id"] != task_id]
    save_data(new_list)

def clear_completed():
    tasks = get_all_tasks()
    save_data([t for t in tasks if not t["done"]])