# main.py — Version 2 with AI Brain

from tasks import show_tasks, add_task, complete_task, delete_task, clear_completed
from ai_brain import ask_ai, get_daily_briefing

def show_menu():
    """Display the main menu."""
    print("\nWhat would you like to do?")
    print("  1 → View all tasks")
    print("  2 → Add a new task")
    print("  3 → Complete a task")
    print("  4 → Delete a task")
    print("  5 → Clear completed tasks")
    print("  6 → 🧠 Chat with AI assistant")
    print("  7 → ☀️  Get my daily briefing")
    print("  8 → Quit")
    print("-" * 35)

def chat_mode():
    """Enter a back-and-forth conversation with the AI."""
    print("\n" + "="*45)
    print("  🧠 AI ASSISTANT — Chat Mode")
    print("  Type 'back' to return to the main menu")
    print("="*45)
    
    chat_history = []  # Stores the conversation so AI remembers
    
    while True:
        user_input = input("\n💬 You → ").strip()
        
        if user_input.lower() == "back":
            print("👋 Leaving chat mode...")
            break
        
        if not user_input:
            continue
        
        print("\n🤖 Assistant is thinking...\n")
        
        try:
            reply, chat_history = ask_ai(user_input, chat_history)
            print(f"🤖 Assistant → {reply}")
        except Exception as e:
            print(f"❌ Error talking to AI: {e}")
            print("Check your API key in the .env file.")

def main():
    """Main loop."""
    print("\n👋 Welcome to your AI Daily Assistant!")
    print("Your personal task manager + AI brain is ready.")
    
    while True:
        show_menu()
        choice = input("→ Enter your choice: ").strip()
        
        if choice == "1":
            show_tasks()
        
        elif choice == "2":
            task_text = input("📝 What's the task? → ").strip()
            if task_text:
                add_task(task_text)
            else:
                print("❌ Task cannot be empty!")
        
        elif choice == "3":
            show_tasks()
            try:
                task_id = int(input("✅ Enter task ID to complete → "))
                complete_task(task_id)
            except ValueError:
                print("❌ Please enter a valid number!")
        
        elif choice == "4":
            show_tasks()
            try:
                task_id = int(input("🗑️  Enter task ID to delete → "))
                delete_task(task_id)
            except ValueError:
                print("❌ Please enter a valid number!")
        
        elif choice == "5":
            clear_completed()
        
        elif choice == "6":
            chat_mode()
        
        elif choice == "7":
            print("\n☀️  Generating your daily briefing...\n")
            try:
                briefing = get_daily_briefing()
                print("="*45)
                print(briefing)
                print("="*45)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "8":
            print("\n👋 Goodbye! Have a productive day!")
            break
        
        else:
            print("❌ Invalid choice. Please enter 1–8.")

# Run the app
main()