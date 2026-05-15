# app.py — Version 4: Stats, Charts & Notifications

import streamlit as st
import plotly.graph_objects as go
from tasks import add_task, complete_task, delete_task, clear_completed
from storage import load_data, get_weekly_stats
from ai_brain import ask_ai, get_daily_briefing
from notifier import notify_task_added, notify_task_completed

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AI Daily Assistant",
    page_icon="🧠",
    layout="wide"
)

# ─────────────────────────────────────────
# DARK / LIGHT MODE TOGGLE
# ─────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

if st.session_state.dark_mode:
    BG         = "#0f1117"
    CARD_BG    = "#1e2130"
    TEXT       = "#ffffff"
    ACCENT     = "#4f8ef7"
    DONE_COLOR = "#2ecc71"
    SUBTEXT    = "#c9d1e0"
    BORDER     = "#4f8ef7"
    SHADOW     = "rgba(79,142,247,0.25)"
else:
    BG         = "#eef2f7"
    CARD_BG    = "#ffffff"
    TEXT       = "#0a0a0a"
    ACCENT     = "#1a56db"
    DONE_COLOR = "#15803d"
    SUBTEXT    = "#374151"
    BORDER     = "#1a56db"
    SHADOW     = "rgba(26,86,219,0.2)"

# ─────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────
st.markdown(f"""
<style>
    /* Background and base text */
    .stApp {{ background-color: {BG} !important; }}

    /* All text elements */
    .stApp, .stApp p, .stApp span, .stApp div,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    .stApp label, .stApp li {{
        color: {TEXT} !important;
    }}

    /* Metrics */
    [data-testid="stMetricLabel"] p {{ color: {SUBTEXT} !important; }}
    [data-testid="stMetricValue"]   {{ color: {TEXT}    !important; }}

    /* Inputs */
    .stTextInput input, .stTextArea textarea {{
        background-color: {CARD_BG} !important;
        color: {TEXT} !important;
        border: 2px solid {BORDER} !important;
        border-radius: 8px !important;
    }}
    .stTextInput label, .stTextArea label {{
        color: {TEXT} !important;
        font-weight: 600 !important;
    }}

    /* Buttons */
    .stButton > button {{
        background-color: {ACCENT} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }}
    .stButton > button:hover {{ opacity: 0.85 !important; }}

    /* Tabs */
    .stTabs [data-baseweb="tab"] {{
        color: {SUBTEXT} !important;
        font-weight: 600 !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {ACCENT} !important;
        border-bottom: 3px solid {ACCENT} !important;
    }}

    /* Progress bar */
    .stProgress > div > div > div {{
        background-color: {ACCENT} !important;
    }}

    /* ── Our fully custom box — no Streamlit dependency ── */
    .box {{
        background-color: {CARD_BG};
        border: 3px solid {BORDER};
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px {SHADOW};
    }}
    .box-title {{
        color: {ACCENT};
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: 0.3px;
    }}

    /* Task cards */
    .task-card {{
        background: {CARD_BG};
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border-left: 4px solid {ACCENT};
        color: {TEXT};
        font-size: 15px;
        font-weight: 500;
        box-shadow: 0 2px 6px {SHADOW};
    }}
    .task-card.done {{
        border-left-color: {DONE_COLOR};
        opacity: 0.55;
        text-decoration: line-through;
    }}

    /* Section labels */
    .section-title {{
        color: {ACCENT};
        font-size: 16px;
        font-weight: 700;
        margin: 14px 0 8px 0;
    }}

    /* Chat bubbles */
    .chat-user {{
        background: {ACCENT};
        color: #ffffff !important;
        padding: 10px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 6px 0 6px auto;
        max-width: 80%;
        text-align: right;
        font-weight: 500;
    }}
    .chat-ai {{
        background: {CARD_BG};
        color: {TEXT} !important;
        padding: 10px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 6px auto 6px 0;
        max-width: 80%;
        border: 2px solid {BORDER};
        font-weight: 500;
    }}
    .chat-placeholder {{
        color: {SUBTEXT};
        font-style: italic;
    }}

    /* Divider */
    hr {{ border-color: {BORDER} !important; opacity: 0.4; }}

    /* Hide Streamlit chrome */
    #MainMenu {{ visibility: hidden; }}
    footer    {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
for key, default in [
    ("chat_history", []),
    ("chat_display", []),
    ("briefing",     None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
h1, h2 = st.columns([6, 1])
with h1:
    st.markdown(f"<h1 style='color:{TEXT};'>🧠 AI Daily Assistant</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{SUBTEXT};'>Your personal productivity companion — powered by Gemini AI</p>", unsafe_allow_html=True)
with h2:
    mode_label = "☀️ Light Mode" if st.session_state.dark_mode else "🌙 Dark Mode"
    if st.button(mode_label, use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

st.divider()

# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Tasks & AI", "📊 Weekly Stats", "🔔 Notifications"])


# ══════════════════════════════════════════
# TAB 1 — Tasks & AI Chat
# ══════════════════════════════════════════
with tab1:
    left_col, right_col = st.columns([1, 1], gap="large")

    # ── LEFT: Task Manager ──
    with left_col:
        st.markdown(f"<h2 style='color:{TEXT};'>📋 Task Manager</h2>", unsafe_allow_html=True)

        # Add task box
        st.markdown(f"""
        <div class="box">
            <div class="box-title">➕ Add a New Task</div>
        </div>
        """, unsafe_allow_html=True)

        # Inputs must be outside the HTML div — placed right after
        new_task = st.text_input(
            "Task", placeholder="e.g. Study Python for 1 hour...",
            label_visibility="collapsed"
        )
        if st.button("Add Task ✅", use_container_width=True):
            if new_task.strip():
                add_task(new_task.strip())
                notify_task_added(new_task.strip())
                st.success(f"Task added: '{new_task}'")
                st.rerun()
            else:
                st.warning("Please type a task first!")

        st.markdown("---")

        # Stats
        tasks    = load_data()
        pending  = [t for t in tasks if not t["done"]]
        done     = [t for t in tasks if t["done"]]
        total    = len(tasks)
        progress = len(done) / total if total > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("📝 Total",     total)
        c2.metric("⏳ Pending",   len(pending))
        c3.metric("✅ Completed", len(done))

        if total > 0:
            st.progress(progress, text=f"{int(progress*100)}% done today!")

        st.markdown("---")

        # Pending tasks
        if pending:
            st.markdown('<div class="section-title">⬜ Pending Tasks</div>', unsafe_allow_html=True)
            for task in pending:
                c1, c2, c3 = st.columns([6, 1, 1])
                c1.markdown(
                    f'<div class="task-card">[{task["id"]}] {task["text"]}</div>',
                    unsafe_allow_html=True
                )
                if c2.button("✅", key=f"done_{task['id']}"):
                    complete_task(task["id"])
                    notify_task_completed(task["text"])
                    st.rerun()
                if c3.button("🗑️", key=f"del_{task['id']}"):
                    delete_task(task["id"])
                    st.rerun()

        # Completed tasks
        if done:
            st.markdown('<div class="section-title">✅ Completed</div>', unsafe_allow_html=True)
            for task in done:
                c1, c2 = st.columns([7, 1])
                c1.markdown(
                    f'<div class="task-card done">[{task["id"]}] {task["text"]}</div>',
                    unsafe_allow_html=True
                )
                if c2.button("🗑️", key=f"del_done_{task['id']}"):
                    delete_task(task["id"])
                    st.rerun()
            if st.button("🧹 Clear All Completed", use_container_width=True):
                clear_completed()
                st.rerun()

        if not tasks:
            st.info("No tasks yet! Add your first task above 🚀")

    # ── RIGHT: AI Assistant ──
    with right_col:
        st.markdown(f"<h2 style='color:{TEXT};'>🤖 AI Assistant</h2>", unsafe_allow_html=True)

        if st.button("☀️ Get My Daily Briefing", use_container_width=True):
            with st.spinner("Generating your briefing..."):
                try:
                    st.session_state.briefing = get_daily_briefing()
                except Exception as e:
                    st.error(f"Error: {e}")

        # Daily briefing box
        if st.session_state.briefing:
            st.markdown(f"""
            <div class="box">
                <div class="box-title">☀️ Your Daily Briefing</div>
                <div style="color:{TEXT}; line-height:1.6;">{st.session_state.briefing}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"<p style='color:{TEXT}; font-weight:700; font-size:16px;'>💬 Chat with your AI assistant</p>", unsafe_allow_html=True)

        # Chat window — bordered box header
        st.markdown(f'<div class="box" style="padding:14px;">', unsafe_allow_html=True)

        # Chat messages rendered as HTML inside the box
        if not st.session_state.chat_display:
            st.markdown(f'<p class="chat-placeholder">Ask me anything about your tasks or your day!</p>', unsafe_allow_html=True)
        for msg in st.session_state.chat_display:
            css  = "chat-user" if msg["role"] == "user" else "chat-ai"
            icon = "💬" if msg["role"] == "user" else "🤖"
            st.markdown(
                f'<div class="{css}">{icon} {msg["content"]}</div>',
                unsafe_allow_html=True
            )

        st.markdown('</div>', unsafe_allow_html=True)

        # Chat input (must be outside the HTML div)
        user_input = st.chat_input("Ask your assistant anything...")
        if user_input:
            st.session_state.chat_display.append({"role": "user", "content": user_input})
            with st.spinner("Thinking..."):
                try:
                    reply, st.session_state.chat_history = ask_ai(
                        user_input, st.session_state.chat_history
                    )
                    st.session_state.chat_display.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"AI Error: {e}")
            st.rerun()

        if st.session_state.chat_display:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.chat_display = []
                st.rerun()


# ══════════════════════════════════════════
# TAB 2 — Weekly Stats
# ══════════════════════════════════════════
with tab2:
    st.markdown(f"<h2 style='color:{TEXT};'>📊 Your Weekly Productivity</h2>", unsafe_allow_html=True)

    weekly    = get_weekly_stats()
    days      = list(weekly.keys())
    completed = [weekly[d]["completed"] for d in days]
    added     = [weekly[d]["added"]     for d in days]

    from datetime import datetime
    labels = [datetime.strptime(d, "%Y-%m-%d").strftime("%a %d") for d in days]

    chart_bg   = "#1e2130" if st.session_state.dark_mode else "#ffffff"
    chart_text = "#ffffff" if st.session_state.dark_mode else "#0a0a0a"
    grid_color = "rgba(255,255,255,0.1)" if st.session_state.dark_mode else "rgba(0,0,0,0.08)"

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="✅ Completed", x=labels, y=completed,
        marker_color=DONE_COLOR, text=completed, textposition="outside",
        textfont=dict(color=chart_text)
    ))
    fig.add_trace(go.Bar(
        name="➕ Added", x=labels, y=added,
        marker_color=ACCENT, text=added, textposition="outside",
        textfont=dict(color=chart_text)
    ))
    fig.update_layout(
        barmode="group",
        plot_bgcolor=chart_bg,
        paper_bgcolor=chart_bg,
        font_color=chart_text,
        title=dict(text="Tasks Added vs Completed — Last 7 Days",
                   font=dict(color=chart_text, size=16)),
        legend=dict(orientation="h", y=1.1, font=dict(color=chart_text)),
        xaxis=dict(tickfont=dict(color=chart_text),
                   gridcolor=grid_color, linecolor=grid_color),
        yaxis=dict(tickfont=dict(color=chart_text),
                   gridcolor=grid_color, linecolor=grid_color),
        margin=dict(t=60, b=20)
    )

    # Wrap chart in our custom box
    st.markdown(f'<div class="box" style="padding:16px;">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Week summary
    st.markdown(f"<h3 style='color:{TEXT};'>🏆 Week Summary</h3>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Added",     sum(added))
    s2.metric("Total Completed", sum(completed))
    s3.metric("Best Day", labels[completed.index(max(completed))] if any(completed) else "—")
    rate = int(sum(completed) / sum(added) * 100) if sum(added) > 0 else 0
    s4.metric("Completion Rate", f"{rate}%")


# ══════════════════════════════════════════
# TAB 3 — Notifications
# ══════════════════════════════════════════
with tab3:
    st.markdown(f"<h2 style='color:{TEXT};'>🔔 Desktop Notifications</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{SUBTEXT};'>Send yourself a quick reminder popup right now!</p>", unsafe_allow_html=True)

    # Notification box header
    st.markdown(f'<div class="box"><div class="box-title">✏️ Custom Notification</div></div>', unsafe_allow_html=True)

    notif_title = st.text_input("Notification Title", value="⏰ Reminder",
                                placeholder="e.g. Time to take a break!")
    notif_msg   = st.text_area("Message",
                                placeholder="e.g. You've been working for 1 hour. Stretch!",
                                height=100)
    if st.button("🔔 Send Notification", use_container_width=True):
        if notif_title and notif_msg:
            from notifier import send_notification
            send_notification(notif_title, notif_msg)
            st.success("✅ Notification sent! Check your desktop.")
        else:
            st.warning("Please fill in both title and message.")

    st.markdown("---")
    st.markdown(f"<h3 style='color:{TEXT};'>⚡ Quick Reminders</h3>", unsafe_allow_html=True)

    q1, q2, q3 = st.columns(3)
    if q1.button("☕ Take a Break",  use_container_width=True):
        from notifier import send_notification
        send_notification("☕ Break Time!", "Step away for 5 minutes.")
        st.success("Sent!")
    if q2.button("💧 Drink Water",   use_container_width=True):
        from notifier import send_notification
        send_notification("💧 Stay Hydrated!", "Time to drink some water.")
        st.success("Sent!")
    if q3.button("🧘 Stretch",       use_container_width=True):
        from notifier import send_notification
        send_notification("🧘 Stretch Break!", "Stand up and stretch for 2 min.")
        st.success("Sent!")
