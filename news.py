"""
news.py — Daily Domain News Feed (Medical / Engineering / Architecture etc.)
"""
import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
import sqlite3
from database import DB_PATH
from datetime import date

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DOMAIN_KEYWORDS = {
    "Doctor":     "medical breakthroughs, healthcare technology, disease research, surgery innovations",
    "Engineer":   "engineering innovations, AI technology, robotics, software development, tech startups",
    "Architect":  "architecture design, sustainable buildings, urban planning, construction technology",
    "Scientist":  "scientific discoveries, space exploration, physics, chemistry, biology research",
    "Lawyer":     "law updates, supreme court verdicts, legal technology, policy changes",
    "Teacher":    "education technology, EdTech, teaching methods, curriculum updates",
    "Other":      "science, technology, innovation, research, education"
}

def init_news_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS news_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT,
            date TEXT,
            news_json TEXT
        )
    """)
    conn.commit()
    conn.close()

def fetch_domain_news(goal, force_refresh=False):
    """Fetch or generate today's news for the user's domain."""
    import json
    today = str(date.today())
    domain = goal or "Other"

    # Check cache
    if not force_refresh:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT news_json FROM news_cache WHERE domain=? AND date=?", (domain, today))
        row = c.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])

    # Generate fresh news via Groq
    keywords = DOMAIN_KEYWORDS.get(domain, DOMAIN_KEYWORDS["Other"])
    prompt = f"""
You are a news curator for students aspiring to become {domain}s.
Generate 6 recent, realistic, and interesting news items about: {keywords}

Today's date: {today}

Return ONLY valid JSON array:
[
  {{
    "headline": "Short punchy headline",
    "summary": "2-3 sentence explanation of what happened and why it matters",
    "category": "Category name",
    "emoji": "relevant emoji",
    "relevance": "Why this matters for a future {domain}"
  }}
]
Make them sound like real recent news. Be specific with technologies, countries, institutions.
No preamble, only JSON.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    raw = response.choices[0].message.content.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    news_items = json.loads(raw)

    # Save to cache
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO news_cache (domain, date, news_json) VALUES (?, ?, ?)",
              (domain, today, json.dumps(news_items)))
    conn.commit()
    conn.close()

    return news_items


def news_page():
    init_news_db()
    st.title("📰 Daily Domain News")

    username = st.session_state.get("username", "user")
    goal = st.session_state.get("user_goal", "Other")

    st.markdown(f"Today's latest updates for **future {goal}s** — {date.today().strftime('%B %d, %Y')} 📅")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh News", use_container_width=True):
            with st.spinner("Fetching latest news..."):
                news = fetch_domain_news(goal, force_refresh=True)
                st.session_state["news_cache"] = news
            st.rerun()

    if "news_cache" not in st.session_state:
        with st.spinner(f"📡 Loading today's {goal} news..."):
            news = fetch_domain_news(goal)
            st.session_state["news_cache"] = news

    news = st.session_state.get("news_cache", [])

    if not news:
        st.warning("Could not load news. Click Refresh to try again.")
        return

    # Display news cards
    for i in range(0, len(news), 2):
        col1, col2 = st.columns(2)
        for col, idx in zip([col1, col2], [i, i+1]):
            if idx < len(news):
                item = news[idx]
                with col:
                    st.markdown(f"""
                    <div style='background: #fafafa; border: 1px solid #e0e0e0;
                         border-radius: 16px; padding: 20px; margin-bottom: 15px;
                         border-left: 4px solid #2e7d32;'>
                        <div style='font-size: 28px;'>{item.get('emoji','📰')}</div>
                        <div style='font-weight: bold; font-size: 15px; margin: 8px 0;'>
                            {item.get('headline','')}
                        </div>
                        <div style='color: #555; font-size: 13px; margin-bottom: 10px;'>
                            {item.get('summary','')}
                        </div>
                        <div style='background: #e8f5e9; padding: 8px 12px; border-radius: 8px;
                             font-size: 12px; color: #2e7d32;'>
                            💡 <b>Why it matters:</b> {item.get('relevance','')}
                        </div>
                        <div style='margin-top: 8px;'>
                            <span style='background: #f5f5f5; padding: 3px 10px; border-radius: 20px;
                                  font-size: 11px; color: #666;'>
                                📂 {item.get('category','')}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("📡 News generated by AI based on your career domain. Refresh daily for new updates.")
