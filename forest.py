import streamlit as st
import time
from database import log_forest_session, get_forest_stats, init_forest_db

# Call this in your main app.py navigation:
# from forest import forest_page
# elif page == "🌳 Forest": forest_page()

def forest_page():
    init_forest_db()

    st.title("🌳 Forest Focus Timer")
    st.markdown("Stay focused. Grow your forest. 🌱")

    name = st.session_state.get("student_name", "")
    if not name:
        name = st.text_input("Enter your name to track your forest:")
        if name:
            st.session_state["student_name"] = name

    if not name:
        return

    # ---------- Stats Row ----------
    stats = get_forest_stats(name)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌳 Trees Grown", stats.get("trees", 0))
    col2.metric("🪙 Coins Earned", stats.get("coins", 0))
    col3.metric("⏱ Today (mins)", stats.get("today_mins", 0))
    col4.metric("📅 This Week (hrs)", round(stats.get("week_mins", 0) / 60, 1))

    st.markdown("---")

    # ---------- Timer Setup ----------
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### ⚙️ Set Your Focus Session")

        duration_option = st.radio(
            "Session Duration",
            ["🍅 Pomodoro (25 min)", "🎯 Deep Work (50 min)", "⚡ Quick (15 min)", "🔧 Custom"],
            horizontal=False
        )

        if duration_option == "🍅 Pomodoro (25 min)":
            duration_mins = 25
        elif duration_option == "🎯 Deep Work (50 min)":
            duration_mins = 50
        elif duration_option == "⚡ Quick (15 min)":
            duration_mins = 15
        else:
            duration_mins = st.slider("Custom Duration (minutes)", 5, 120, 30)

        subject_focus = st.text_input("What are you studying?", placeholder="e.g. Data Structures")

        tree_type = st.selectbox("Choose your tree 🌱", [
            "🌱 Sapling", "🌿 Fern", "🎋 Bamboo",
            "🌲 Pine", "🌴 Palm", "🍎 Apple Tree", "🌳 Oak"
        ])

    with col_right:
        st.markdown("### 🌱 Your Tree")

        # Tree growth stages
        STAGES = {
            0:   ("🪨", "Waiting to plant..."),
            10:  ("🌱", "A seed is sprouting!"),
            25:  ("🌿", "Growing nicely..."),
            50:  ("🌲", "Half grown!"),
            75:  ("🌳", "Almost there..."),
            100: ("🎄", "Fully grown! Beautiful!")
        }

        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False
        if "timer_start" not in st.session_state:
            st.session_state.timer_start = None
        if "timer_duration" not in st.session_state:
            st.session_state.timer_duration = duration_mins * 60
        if "tree_alive" not in st.session_state:
            st.session_state.tree_alive = True
        if "session_complete" not in st.session_state:
            st.session_state.session_complete = False

        # Display current tree stage
        progress_pct = 0
        if st.session_state.timer_running and st.session_state.timer_start:
            elapsed = time.time() - st.session_state.timer_start
            total = st.session_state.timer_duration
            progress_pct = min(int((elapsed / total) * 100), 100)

        # Find correct stage
        stage_emoji, stage_msg = "🪨", "Waiting to plant..."
        for threshold in sorted(STAGES.keys(), reverse=True):
            if progress_pct >= threshold:
                stage_emoji, stage_msg = STAGES[threshold]
                break

        if not st.session_state.tree_alive:
            stage_emoji = "🥀"
            stage_msg = "Your tree died... Try again!"

        # Big tree display
        st.markdown(f"""
        <div style='text-align:center; padding: 20px; background: linear-gradient(135deg, #e8f5e9, #c8e6c9); 
             border-radius: 16px; margin: 10px 0;'>
            <div style='font-size: 80px;'>{stage_emoji}</div>
            <div style='font-size: 16px; color: #2e7d32; font-weight: bold; margin-top: 8px;'>{stage_msg}</div>
        </div>
        """, unsafe_allow_html=True)

        # Progress bar
        if st.session_state.timer_running:
            st.progress(progress_pct / 100)
            st.caption(f"Focus progress: {progress_pct}%")

    st.markdown("---")

    # ---------- Timer Controls ----------
    col_start, col_stop, col_give_up = st.columns(3)

    with col_start:
        if not st.session_state.timer_running:
            if st.button("🌱 Start Growing", use_container_width=True, type="primary"):
                st.session_state.timer_running = True
                st.session_state.timer_start = time.time()
                st.session_state.timer_duration = duration_mins * 60
                st.session_state.tree_alive = True
                st.session_state.session_complete = False
                st.session_state.current_subject = subject_focus
                st.session_state.current_tree = tree_type
                st.rerun()

    with col_stop:
        if st.session_state.timer_running:
            if st.button("✅ Complete Session", use_container_width=True):
                elapsed = time.time() - st.session_state.timer_start
                total = st.session_state.timer_duration
                pct_done = (elapsed / total) * 100

                if pct_done >= 80:  # 80%+ = tree survives
                    coins = int(duration_mins * 1.5)
                    log_forest_session(
                        name,
                        subject_focus,
                        duration_mins,
                        tree_type,
                        "completed",
                        coins
                    )
                    st.session_state.timer_running = False
                    st.session_state.session_complete = True
                    st.success(f"🌳 Tree grown! +{coins} coins earned!")
                    st.balloons()
                else:
                    st.warning("⚠️ You need to complete at least 80% of the session!")

    with col_give_up:
        if st.session_state.timer_running:
            if st.button("🥀 Give Up", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.tree_alive = False
                log_forest_session(name, subject_focus, 0, tree_type, "died", 0)
                st.error("🥀 Your tree died. Stay focused next time!")
                st.rerun()

    # ---------- Live Countdown ----------
    if st.session_state.timer_running and st.session_state.timer_start:
        elapsed = time.time() - st.session_state.timer_start
        remaining = max(st.session_state.timer_duration - elapsed, 0)
        mins_left = int(remaining // 60)
        secs_left = int(remaining % 60)

        st.markdown(f"""
        <div style='text-align:center; font-size: 48px; font-weight: bold; 
             color: #2e7d32; padding: 20px;'>
            ⏱ {mins_left:02d}:{secs_left:02d}
        </div>
        """, unsafe_allow_html=True)

        if remaining <= 0:
            coins = int(st.session_state.timer_duration / 60 * 1.5)
            log_forest_session(
                name,
                st.session_state.get("current_subject", ""),
                st.session_state.timer_duration // 60,
                st.session_state.get("current_tree", "🌳"),
                "completed",
                coins
            )
            st.session_state.timer_running = False
            st.session_state.session_complete = True
            st.success(f"🎉 Session complete! Tree grown! +{coins} coins!")
            st.balloons()
            st.rerun()

        # Auto-refresh every second
        time.sleep(1)
        st.rerun()

    st.markdown("---")

    # ---------- My Forest Gallery ----------
    st.markdown("### 🌲 My Forest")
    sessions = get_forest_stats(name, full=True)
    forest_sessions = sessions.get("sessions", [])

    if forest_sessions:
        # Display forest as emoji grid
        completed = [s for s in forest_sessions if s["status"] == "completed"]
        died = [s for s in forest_sessions if s["status"] == "died"]

        forest_display = ""
        for s in completed[-20:]:  # Show last 20 trees
            forest_display += s.get("tree_type", "🌳") + " "

        if forest_display:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #e8f5e9, #a5d6a7); 
                 padding: 20px; border-radius: 16px; font-size: 30px; 
                 text-align: center; letter-spacing: 5px;'>
                {forest_display}
            </div>
            """, unsafe_allow_html=True)

        # Session history table
        st.markdown("#### 📋 Recent Sessions")
        for s in reversed(forest_sessions[-5:]):
            status_icon = "🌳" if s["status"] == "completed" else "🥀"
            st.markdown(
                f"{status_icon} **{s.get('subject', 'Study')}** — "
                f"{s.get('duration', 0)} mins — "
                f"🪙 {s.get('coins', 0)} coins — "
                f"_{s.get('date', '')}_"
            )
    else:
        st.info("🌱 Your forest is empty. Start your first session!")

    # ---------- Coins Redemption Banner ----------
    coins = stats.get("coins", 0)
    if coins >= 100:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #fff9c4, #f9a825); 
             padding: 15px; border-radius: 12px; text-align: center; margin-top: 20px;'>
            <b>🌍 You have {coins} coins!</b><br>
            In a real deployment, you can donate coins to plant real trees via Trees for the Future! 🌳
        </div>
        """, unsafe_allow_html=True)
