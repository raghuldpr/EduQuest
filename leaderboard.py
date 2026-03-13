import sqlite3
from database import DB_PATH
from datetime import date, timedelta

def get_leaderboard(period="all"):
    """Get leaderboard ranked by study + focus hours."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Date filter
    if period == "today":
        date_filter = f"AND date='{date.today()}'"
    elif period == "week":
        week_start = str(date.today() - timedelta(days=7))
        date_filter = f"AND date>='{week_start}'"
    else:
        date_filter = ""

    # Forest focus minutes per user
    c.execute(f"""
        SELECT student_name, 
               SUM(duration) as focus_mins,
               COUNT(CASE WHEN status='completed' THEN 1 END) as trees,
               SUM(coins) as coins
        FROM forest_sessions 
        WHERE status='completed' {date_filter}
        GROUP BY student_name
    """)
    forest_rows = c.fetchall()
    forest_map = {r[0]: {"focus_mins": r[1] or 0, "trees": r[2] or 0, "coins": r[3] or 0}
                  for r in forest_rows}

    # Study progress (done topics) per user
    c.execute(f"""
        SELECT student_name, COUNT(*) as done_topics
        FROM progress
        WHERE status='done'
        GROUP BY student_name
    """)
    progress_rows = c.fetchall()
    progress_map = {r[0]: r[1] for r in progress_rows}

    # Get all users
    c.execute("SELECT username, full_name FROM users")
    users = c.fetchall()
    conn.close()

    leaderboard = []
    for username, full_name in users:
        focus = forest_map.get(username, {})
        focus_mins = focus.get("focus_mins", 0)
        trees = focus.get("trees", 0)
        coins = focus.get("coins", 0)
        done_topics = progress_map.get(username, 0)

        # Score formula: focus hours * 10 + topics done * 5 + trees * 3
        score = int((focus_mins / 60) * 10 + done_topics * 5 + trees * 3)

        leaderboard.append({
            "username": username,
            "full_name": full_name,
            "focus_hrs": round(focus_mins / 60, 1),
            "topics_done": done_topics,
            "trees": trees,
            "coins": coins,
            "score": score
        })

    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    # Add rank and medal
    medals = ["🥇", "🥈", "🥉"]
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
        entry["medal"] = medals[i] if i < 3 else f"#{i+1}"

    return leaderboard


def get_user_rank(username, period="all"):
    lb = get_leaderboard(period)
    for entry in lb:
        if entry["username"] == username:
            return entry
    return None
