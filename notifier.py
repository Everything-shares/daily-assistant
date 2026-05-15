# notifier.py — Desktop popup notifications

from plyer import notification

def send_notification(title, message):
    """Send a desktop popup notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="AI Daily Assistant",
            timeout=8  # Popup stays for 8 seconds
        )
    except Exception as e:
        print(f"Notification error: {e}")

def notify_task_added(task_text):
    send_notification(
        title="✅ Task Added!",
        message=f"'{task_text}' added to your list."
    )

def notify_task_completed(task_text):
    send_notification(
        title="🎉 Task Completed!",
        message=f"Great job finishing '{task_text}'!"
    )

def notify_daily_reminder():
    send_notification(
        title="☀️ Daily Assistant Reminder",
        message="Don't forget to check your tasks for today!"
    )