# ai_brain.py
# This file handles all communication with Google Gemini AI

import os
import google.generativeai as genai
from dotenv import load_dotenv
from storage import load_data

# Load your secret API key from the .env file
load_dotenv()

# Connect to Gemini using your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Choose the Gemini model to use
MODEL = "gemini-2.5-flash"  # Free, fast, and very capable ✅


def get_tasks_summary():
    """Convert your tasks into text so the AI can understand them."""
    tasks = load_data()

    if not tasks:
        return "The user has no tasks yet."

    pending = [t for t in tasks if not t["done"]]
    done    = [t for t in tasks if t["done"]]

    summary = f"The user has {len(tasks)} total tasks.\n"

    if pending:
        summary += "\nPENDING TASKS:\n"
        for t in pending:
            summary += f"  - [{t['id']}] {t['text']}\n"

    if done:
        summary += "\nCOMPLETED TASKS:\n"
        for t in done:
            summary += f"  - [{t['id']}] {t['text']}\n"

    return summary


def build_system_prompt():
    """Build the AI personality + task context."""
    tasks_context = get_tasks_summary()

    return f"""You are a friendly, smart, and motivating personal daily assistant.
You help the user manage their tasks, stay productive, and feel good about their day.

Here is the user's current task list:
{tasks_context}

Your rules:
- Keep responses short and clear (3-5 lines max unless asked for more)
- Be warm, encouraging, and positive
- When suggesting tasks or priorities, refer to tasks by their ID number
- If the user seems stressed, be extra supportive
- Use simple language — the user may be a beginner
- Use emojis occasionally to keep things friendly 😊
"""


def ask_ai(user_message, chat_history):
    """
    Send a message to Gemini and get a response back.

    - user_message  : what the user just typed
    - chat_history  : list of past messages (so AI remembers the conversation)
    """

    # Create the Gemini model with personality instructions
    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=build_system_prompt()
    )

    # Convert our chat history into Gemini's expected format
    gemini_history = []
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({
            "role": role,
            "parts": [msg["content"]]
        })

    # Start a chat session with the existing history
    chat_session = model.start_chat(history=gemini_history)

    # Send the new message
    response = chat_session.send_message(user_message)
    ai_reply = response.text

    # Save both messages to our chat history for memory
    chat_history.append({"role": "user",      "content": user_message})
    chat_history.append({"role": "assistant",  "content": ai_reply})

    return ai_reply, chat_history


def get_daily_briefing():
    """Generate a motivating morning briefing based on your tasks."""
    tasks_context = get_tasks_summary()

    prompt = f"""Based on these tasks, give me a short motivating morning briefing.
Include:
1. A warm good morning greeting
2. How many tasks are pending
3. One recommendation on what to focus on first and why
4. A short motivational sentence to close

Tasks:
{tasks_context}"""

    model = genai.GenerativeModel(model_name=MODEL)
    response = model.generate_content(prompt)

    return response.text