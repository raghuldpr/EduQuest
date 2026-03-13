import sqlite3
import json
from datetime import date, datetime

DB_PATH = "studyplanner.db"

def init_forest_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS forest_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            subject TEXT,
            duration INTEGER,
            tree_type TEXT,
            status TEXT,
            coins INTEGER,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_forest_session(name, subject, duration, tree_type, status, coins):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO forest_sessions (student_name, subject, duration, tree_type, status, coins, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, subject, duration, tree_type, status, coins, str(date.today())))
    conn.commit()
    conn.close()

def get_forest_stats(name, full=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Total trees and coins
    c.execute("SELECT COUNT(*), SUM(coins) FROM forest_sessions WHERE student_name=? AND status='completed'", (name,))
    row = c.fetchone()
    trees = row[0] or 0
    coins = row[1] or 0

    # Today's study time
    c.execute("SELECT SUM(duration) FROM forest_sessions WHERE student_name=? AND date=? AND status='completed'",
              (name, str(date.today())))
    today_row = c.fetchone()
    today_mins = today_row[0] or 0

    # This week
    from datetime import timedelta
    week_start = str(date.today() - timedelta(days=7))
    c.execute("SELECT SUM(duration) FROM forest_sessions WHERE student_name=? AND date>=? AND status='completed'",
              (name, week_start))
    week_row = c.fetchone()
    week_mins = week_row[0] or 0

    result = {"trees": trees, "coins": coins, "today_mins": today_mins, "week_mins": week_mins}

    if full:
        c.execute("SELECT subject, duration, tree_type, status, coins, date FROM forest_sessions WHERE student_name=? ORDER BY id DESC LIMIT 20", (name,))
        rows = c.fetchall()
        result["sessions"] = [
            {"subject": r[0], "duration": r[1], "tree_type": r[2],
             "status": r[3], "coins": r[4], "date": r[5]} for r in rows
        ]

    conn.close()
    return result

def init_db():
    # Ensure all tables exist in one call
    init_forest_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _ensure_xp_tables(c)
    conn.commit()
    conn.close()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            created_at TEXT DEFAULT (date('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            plan_json TEXT,
            exam_date TEXT,
            subjects TEXT,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            day_num INTEGER,
            topic_index INTEGER,
            status TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_plan(name, plan, exam_date, subjects):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Delete old plan if exists
    c.execute("DELETE FROM plans WHERE student_name=?", (name,))
    c.execute("DELETE FROM progress WHERE student_name=?", (name,))
    c.execute("""
        INSERT INTO plans (student_name, plan_json, exam_date, subjects, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (name, json.dumps(plan), exam_date, json.dumps(subjects), str(datetime.now())))
    conn.commit()
    conn.close()

def get_plan(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT plan_json FROM plans WHERE student_name=? ORDER BY id DESC LIMIT 1", (name,))
    row = c.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def update_topic_status(name, day_num, topic_index, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Check if exists
    c.execute("""
        SELECT id FROM progress 
        WHERE student_name=? AND day_num=? AND topic_index=?
    """, (name, day_num, topic_index))
    row = c.fetchone()
    if row:
        c.execute("""
            UPDATE progress SET status=?, updated_at=? WHERE id=?
        """, (status, str(datetime.now()), row[0]))
    else:
        c.execute("""
            INSERT INTO progress (student_name, day_num, topic_index, status, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, day_num, topic_index, status, str(datetime.now())))
    conn.commit()
    conn.close()

def get_progress(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get plan
    c.execute("SELECT plan_json, exam_date FROM plans WHERE student_name=? ORDER BY id DESC LIMIT 1", (name,))
    plan_row = c.fetchone()
    if not plan_row:
        conn.close()
        return None

    plan = json.loads(plan_row[0])
    exam_date = datetime.strptime(plan_row[1], "%Y-%m-%d").date()
    days_left = (exam_date - date.today()).days

    # Count total topics
    total = sum(len(day.get("topics", [])) for day in plan.get("days", []))

    # Get statuses
    c.execute("""
        SELECT status, COUNT(*) FROM progress 
        WHERE student_name=? GROUP BY status
    """, (name,))
    rows = c.fetchall()
    status_map = {row[0]: row[1] for row in rows}

    done = status_map.get("done", 0)
    skipped = status_map.get("skipped", 0)
    pending = total - done - skipped

    conn.close()
    return {
        "total": total,
        "done": done,
        "skipped": skipped,
        "pending": pending,
        "days_left": max(days_left, 0)
    }

# ─── XP & Gamification Constants ────────────────────────────────────────────

XP_LEVELS = [
    {"level": 1,  "title": "Novice",      "min_xp": 0},
    {"level": 2,  "title": "Apprentice",  "min_xp": 100},
    {"level": 3,  "title": "Scholar",     "min_xp": 300},
    {"level": 4,  "title": "Explorer",    "min_xp": 600},
    {"level": 5,  "title": "Achiever",    "min_xp": 1000},
    {"level": 6,  "title": "Expert",      "min_xp": 1500},
    {"level": 7,  "title": "Master",      "min_xp": 2200},
    {"level": 8,  "title": "Grandmaster", "min_xp": 3000},
    {"level": 9,  "title": "Legend",      "min_xp": 4000},
    {"level": 10, "title": "Champion",    "min_xp": 5500},
]

# List of (name, emoji, key, desc) tuples — iterable by app.py
BADGE_DEFINITIONS = [
    ("First Quiz",    "🎯", "first_quiz",    "Completed your first quiz"),
    ("Perfect Score", "💯", "perfect_score", "Got 100% on a quiz"),
    ("3-Day Streak",  "🔥", "streak_3",      "Studied 3 days in a row"),
    ("Forest Grower", "🌳", "forest_5",      "Planted 5 focus trees"),
    ("Rising Star",   "⭐", "level_5",       "Reached Level 5"),
    ("Planner",       "📅", "plan_creator",  "Created a study plan"),
    ("Note Taker",    "📝", "note_taker",    "Saved your first note"),
    ("Speed Learner", "⚡", "speed_learner", "Completed quiz in under 60s"),
]
# Dict form for internal lookups
_BADGE_DICT = {key: {"name": name, "icon": emoji, "desc": desc}
               for name, emoji, key, desc in BADGE_DEFINITIONS}

MISSION_DEFINITIONS = [
    {"id": "daily_quiz",   "name": "Take a Quiz",        "icon": "🎯", "xp": 30,  "target": 1},
    {"id": "study_30",     "name": "Study 30 Minutes",   "icon": "⏱️", "xp": 50,  "target": 30},
    {"id": "read_news",    "name": "Read Study News",    "icon": "📰", "xp": 15,  "target": 1},
    {"id": "plant_tree",   "name": "Plant a Focus Tree", "icon": "🌱", "xp": 25,  "target": 1},
    {"id": "check_topics", "name": "Complete 3 Topics",  "icon": "✅", "xp": 40,  "target": 3},
]


def _ensure_xp_tables(c):
    c.execute("""
        CREATE TABLE IF NOT EXISTS xp_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            amount INTEGER,
            reason TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            badge_id TEXT,
            awarded_at TEXT DEFAULT (datetime('now')),
            UNIQUE(student_name, badge_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            mission_id TEXT,
            progress INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            mission_date TEXT,
            UNIQUE(student_name, mission_id, mission_date)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            subject TEXT,
            score INTEGER,
            total INTEGER,
            difficulty TEXT,
            time_taken INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS difficulty_settings (
            student_name TEXT PRIMARY KEY,
            difficulty TEXT DEFAULT 'medium',
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)


# ─── XP Functions ────────────────────────────────────────────────────────────

def add_xp(student_name: str, amount: int, reason: str = "") -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _ensure_xp_tables(c)
    c.execute(
        "INSERT INTO xp_log (student_name, amount, reason) VALUES (?, ?, ?)",
        (student_name, amount, reason)
    )
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM xp_log WHERE student_name=?", (student_name,))
    total = c.fetchone()[0]
    conn.commit()
    conn.close()
    return total


def get_level_data(student_name: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _ensure_xp_tables(c)
    c.execute("SELECT COALESCE(SUM(amount), 0) FROM xp_log WHERE student_name=?", (student_name,))
    total_xp = c.fetchone()[0]
    conn.close()

    current = XP_LEVELS[0]
    next_level = None
    for i, lvl in enumerate(XP_LEVELS):
        if total_xp >= lvl["min_xp"]:
            current = lvl
            next_level = XP_LEVELS[i + 1] if i + 1 < len(XP_LEVELS) else None

    xp_in_level = total_xp - current["min_xp"]
    xp_needed = (next_level["min_xp"] - current["min_xp"]) if next_level else 1
    progress_pct = min(int((xp_in_level / xp_needed) * 100), 100) if xp_needed else 100

    return {
        "total_xp": total_xp,
        "level": current["level"],
        "title": current["title"],
        "progress_pct": progress_pct,
        "xp_in_level": xp_in_level,
        "xp_needed": xp_needed,
        "next_level": next_level,
    }


# ─── Badge Functions ──────────────────────────────────────────────────────────

def get_badges(student_name: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _ensure_xp_tables(c)
    c.execute("SELECT badge_id, awarded_at FROM badges WHERE student_name=?", (student_name,))
    rows = c.fetchall()
    conn.close()
    result = []
    for badge_id, awarded_at in rows:
        if badge_id in _BADGE_DICT:
            b = _BADGE_DICT[badge_id].copy()
            b["id"] = badge_id
            b["awarded_at"] = awarded_at
            result.append(b)
    return result


def award_badge(student_name: str, badge_id: str) -> bool:
    """Returns True if badge was newly awarded, False if already had it."""
    if badge_id not in _BADGE_DICT:
        return False
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _ensure_xp_tables(c)
    try:
        c.execute(
            "INSERT INTO badges (student_name, badge_id) VALUES (?, ?)",
            (student_name, badge_id)
        )
        conn.commit()
        awarded = True
    except sqlite3.IntegrityError:
        awarded = False
    conn.close()
    return awarded


# ─── Mission Functions ────────────────────────────────────────────────────────

def init_daily_missions(student_name: str) -> list:
    today = str(date.today())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _ensure_xp_tables(c)
    for m in MISSION_DEFINITIONS:
        c.execute("""
            INSERT OR IGNORE INTO missions (student_name, mission_id, progress, completed, mission_date)
            VALUES (?, ?, 0, 0, ?)
        """, (student_name, m["id"], today))
    conn.commit()

    c.execute("SELECT mission_id, progress, completed FROM missions WHERE student_name=? AND mission_date=?",
              (student_name, today))
    rows = {r[0]: {"progress": r[1], "completed": r[2]} for r in c.fetchall()}
    conn.close()

    result = []
    for m in MISSION_DEFINITIONS:
        entry = m.copy()
        state = rows.get(m["id"], {"progress": 0, "completed": 0})
        entry["progress"]  = state["progress"]
        entry["completed"] = bool(state["completed"])
        # Aliases expected by app.py
        entry["current"] = entry["progress"]
        entry["label"]   = entry["name"]
        entry["emoji"]   = entry["icon"]
        entry["status"]  = "completed" if entry["completed"] else "pending"
        result.append(entry)
    return result


def update_mission(student_name: str, mission_id: str, increment: int = 1) -> dict:
    today = str(date.today())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _ensure_xp_tables(c)

    mission_def = next((m for m in MISSION_DEFINITIONS if m["id"] == mission_id), None)
    if not mission_def:
        conn.close()
        return {"completed": False, "xp_earned": 0}

    c.execute("""
        INSERT OR IGNORE INTO missions (student_name, mission_id, progress, completed, mission_date)
        VALUES (?, ?, 0, 0, ?)
    """, (student_name, mission_id, today))

    c.execute("SELECT progress, completed FROM missions WHERE student_name=? AND mission_id=? AND mission_date=?",
              (student_name, mission_id, today))
    row = c.fetchone()
    current_progress, already_done = row if row else (0, 0)

    if already_done:
        conn.close()
        return {"completed": True, "xp_earned": 0}

    new_progress = current_progress + increment
    newly_completed = new_progress >= mission_def["target"]

    c.execute("""
        UPDATE missions SET progress=?, completed=?
        WHERE student_name=? AND mission_id=? AND mission_date=?
    """, (new_progress, 1 if newly_completed else 0, student_name, mission_id, today))
    conn.commit()
    conn.close()

    xp_earned = mission_def["xp"] if newly_completed else 0
    if newly_completed:
        add_xp(student_name, xp_earned, f"Mission: {mission_def['name']}")

    return {"completed": newly_completed, "xp_earned": xp_earned}


def get_missions(student_name: str) -> list:
    return init_daily_missions(student_name)


# ─── Quiz Performance & Difficulty ───────────────────────────────────────────

def update_quiz_performance(student_name: str, subject: str, score: int,
                             total: int, difficulty: str, time_taken: int = 0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _ensure_xp_tables(c)
    c.execute("""
        INSERT INTO quiz_performance (student_name, subject, score, total, difficulty, time_taken)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (student_name, subject, score, total, difficulty, time_taken))

    # Auto-adjust difficulty based on last 3 quizzes
    c.execute("""
        SELECT score, total FROM quiz_performance
        WHERE student_name=? ORDER BY id DESC LIMIT 3
    """, (student_name,))
    recent = c.fetchall()
    if len(recent) >= 2:
        avg = sum(r[0] / r[1] for r in recent) / len(recent)
        if avg >= 0.85:
            new_diff = "hard"
        elif avg <= 0.50:
            new_diff = "easy"
        else:
            new_diff = "medium"
        c.execute("""
            INSERT INTO difficulty_settings (student_name, difficulty)
            VALUES (?, ?)
            ON CONFLICT(student_name) DO UPDATE SET difficulty=?, updated_at=datetime('now')
        """, (student_name, new_diff, new_diff))

    conn.commit()
    conn.close()


def get_difficulty(student_name: str, subject: str = "", topic: str = "") -> int:
    """Returns 1 (easy), 2 (medium), 3 (hard) to match app.py diff_labels."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    _ensure_xp_tables(c)
    c.execute("SELECT difficulty FROM difficulty_settings WHERE student_name=?", (student_name,))
    row = c.fetchone()
    conn.close()
    diff_str = row[0] if row else "medium"
    return {"easy": 1, "medium": 2, "hard": 3}.get(diff_str, 2)
