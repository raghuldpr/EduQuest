"""
notebook.py — NotebookLM-style AI Notes + Podcast Script Generator
"""
import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from database import DB_PATH
import sqlite3

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def init_notebook_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS notebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            title TEXT,
            content TEXT,
            summary TEXT,
            key_points TEXT,
            flashcards TEXT,
            podcast_script TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def ai_process_notes(title, content):
    """Generate summary, key points, flashcards from notes."""
    prompt = f"""
You are a study assistant. A student has uploaded notes titled "{title}".
Here is the content:
{content[:6000]}

Generate a structured study pack in JSON:
{{
  "summary": "3-4 sentence overview of the entire content",
  "key_points": ["point 1", "point 2", "point 3", ...],
  "flashcards": [
    {{"question": "Q1?", "answer": "A1"}},
    {{"question": "Q2?", "answer": "A2"}}
  ],
  "mind_map_topics": ["Topic 1", "Topic 2", "Topic 3"]
}}
Return ONLY valid JSON. No preamble.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    import json
    raw = response.choices[0].message.content.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()
    return json.loads(raw)


def generate_podcast_script(title, content, host1="Alex", host2="Sam"):
    """Generate a 2-host podcast script from notes — NotebookLM style."""
    prompt = f"""
You are creating an educational podcast script based on study notes.
Topic: "{title}"
Content: {content[:5000]}

Create a natural, engaging 2-host podcast conversation between {host1} and {host2}.
They should:
- Explain the topic in simple conversational language
- Ask each other questions to clarify concepts
- Give real-world examples and analogies
- Include 1-2 fun facts
- Summarize key points at the end
- Be approximately 5-7 minutes when read aloud (~700-900 words)

Format:
{host1}: [dialogue]
{host2}: [dialogue]
...

Make it feel like a real podcast, not a lecture. Start directly with the conversation.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content


def ask_from_notes(content, question):
    """Answer a question strictly from the uploaded notes."""
    prompt = f"""
A student uploaded these notes:
{content[:5000]}

Their question: {question}

Answer ONLY from the notes above. If the answer isn't in the notes, say so.
Give a clear, concise explanation with examples if possible.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=800
    )
    return response.choices[0].message.content


def notebook_page():
    init_notebook_db()
    st.title("📓 AI Notebook")
    st.markdown("Upload your notes → AI summarizes, creates flashcards, and makes a podcast! 🎙️")

    username = st.session_state.get("username", "user")

    tab1, tab2, tab3 = st.tabs(["📤 Upload & Process", "🗂️ My Notebooks", "🎙️ Podcast Generator"])

    # ---- TAB 1: UPLOAD ----
    with tab1:
        st.markdown("### 📤 Upload Your Notes")
        note_title = st.text_input("Note Title", placeholder="e.g. Data Structures - Trees")

        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"])
        with col2:
            manual_text = st.text_area("Or paste your notes here", height=200,
                placeholder="Paste your notes, textbook content, or any study material...")

        if st.button("🤖 Process with AI", use_container_width=True, type="primary"):
            if not note_title:
                st.error("Please enter a title!")
            elif not uploaded_file and not manual_text.strip():
                st.error("Please upload a file or paste some notes!")
            else:
                content = ""
                if uploaded_file:
                    if uploaded_file.name.endswith(".pdf"):
                        try:
                            import pdfplumber, io
                            with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                                content = "\n".join(p.extract_text() or "" for p in pdf.pages)
                        except:
                            st.error("Could not read PDF. Try pasting text instead.")
                            st.stop()
                    else:
                        content = uploaded_file.read().decode("utf-8", errors="ignore")
                else:
                    content = manual_text

                with st.spinner("🤖 AI is reading and processing your notes..."):
                    result = ai_process_notes(note_title, content)
                    st.session_state["current_note"] = {
                        "title": note_title,
                        "content": content,
                        "result": result
                    }

                    # Save to DB
                    import json
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO notebooks (username, title, content, summary, key_points, flashcards)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (username, note_title, content,
                          result.get("summary", ""),
                          json.dumps(result.get("key_points", [])),
                          json.dumps(result.get("flashcards", []))))
                    conn.commit()
                    st.session_state["last_notebook_id"] = c.lastrowid
                    conn.close()

                st.success("✅ Notes processed!")

        # Show results
        if "current_note" in st.session_state:
            note = st.session_state["current_note"]
            result = note["result"]
            st.markdown("---")

            # Summary
            st.markdown("### 📋 Summary")
            st.info(result.get("summary", ""))

            # Key Points
            st.markdown("### 🎯 Key Points")
            for i, pt in enumerate(result.get("key_points", []), 1):
                st.markdown(f"**{i}.** {pt}")

            # Flashcards
            st.markdown("### 🃏 Flashcards")
            flashcards = result.get("flashcards", [])
            if flashcards:
                if "fc_index" not in st.session_state:
                    st.session_state.fc_index = 0
                if "fc_show_answer" not in st.session_state:
                    st.session_state.fc_show_answer = False

                idx = st.session_state.fc_index % len(flashcards)
                fc = flashcards[idx]

                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #e3f2fd, #bbdefb);
                     padding: 25px; border-radius: 16px; text-align: center; font-size: 18px;'>
                    <b>Q: {fc['question']}</b>
                </div>""", unsafe_allow_html=True)

                if st.session_state.fc_show_answer:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
                         padding: 20px; border-radius: 16px; text-align: center; margin-top: 10px;'>
                        💡 {fc['answer']}
                    </div>""", unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("👁️ Show Answer", use_container_width=True):
                        st.session_state.fc_show_answer = True
                        st.rerun()
                with c2:
                    if st.button("⏭️ Next Card", use_container_width=True):
                        st.session_state.fc_index += 1
                        st.session_state.fc_show_answer = False
                        st.rerun()
                with c3:
                    st.caption(f"Card {idx+1} of {len(flashcards)}")

            # Ask from notes
            st.markdown("### 🤖 Ask AI from Your Notes")
            q = st.text_input("Ask anything about these notes...", placeholder="What is a binary tree?")
            if st.button("Ask", use_container_width=True):
                with st.spinner("Searching your notes..."):
                    ans = ask_from_notes(note["content"], q)
                    st.markdown(f"""
                    <div style='background:#f9f9f9; padding:15px; border-radius:12px; border-left: 4px solid #2e7d32;'>
                    {ans}
                    </div>""", unsafe_allow_html=True)

    # ---- TAB 2: MY NOTEBOOKS ----
    with tab2:
        st.markdown("### 🗂️ Saved Notebooks")
        import json
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, title, summary, created_at FROM notebooks WHERE username=? ORDER BY id DESC",
                  (username,))
        rows = c.fetchall()
        conn.close()

        if not rows:
            st.info("No notebooks yet. Upload some notes!")
        else:
            for row in rows:
                with st.expander(f"📓 {row[1]} — {row[3][:10]}"):
                    st.markdown(f"**Summary:** {row[2]}")
                    if st.button("🎙️ Generate Podcast", key=f"pod_{row[0]}"):
                        conn2 = sqlite3.connect(DB_PATH)
                        c2 = conn2.cursor()
                        c2.execute("SELECT content FROM notebooks WHERE id=?", (row[0],))
                        content_row = c2.fetchone()
                        conn2.close()
                        if content_row:
                            with st.spinner("🎙️ Creating podcast script..."):
                                script = generate_podcast_script(row[1], content_row[0])
                                st.session_state[f"podcast_{row[0]}"] = script
                    if f"podcast_{row[0]}" in st.session_state:
                        st.markdown("#### 🎙️ Podcast Script")
                        st.text_area("Script", st.session_state[f"podcast_{row[0]}"],
                                     height=400, key=f"script_{row[0]}")
                        st.download_button("⬇️ Download Script",
                                           st.session_state[f"podcast_{row[0]}"],
                                           file_name=f"{row[1]}_podcast.txt")

    # ---- TAB 3: PODCAST ----
    with tab3:
        st.markdown("### 🎙️ Generate a Podcast from Any Topic")
        st.markdown("Type a topic or paste content → AI creates a 2-host podcast script!")

        pod_title = st.text_input("Topic / Title", placeholder="e.g. Machine Learning Basics")
        pod_content = st.text_area("Paste content or just describe the topic", height=200,
            placeholder="Paste notes, or just write: 'Explain neural networks simply'")
        host1 = st.text_input("Host 1 name", value="Alex")
        host2 = st.text_input("Host 2 name", value="Sam")

        if st.button("🎙️ Generate Podcast Script", use_container_width=True, type="primary"):
            if not pod_title:
                st.error("Enter a title!")
            else:
                with st.spinner("🎙️ Writing your podcast..."):
                    if not pod_content.strip():
                        pod_content = f"Explain {pod_title} in detail with examples."
                    script = generate_podcast_script(pod_title, pod_content, host1, host2)
                    st.session_state["quick_podcast"] = script

        if "quick_podcast" in st.session_state:
            st.markdown("---")
            st.markdown("### 🎙️ Your Podcast Script")

            # Color-code by host
            script = st.session_state["quick_podcast"]
            lines = script.split("\n")
            for line in lines:
                if line.startswith(host1 + ":"):
                    st.markdown(f"""<div style='background:#e3f2fd; padding:8px 15px;
                        border-radius:8px; margin:4px 0;'><b style='color:#1565c0;'>{host1}</b>:
                        {line[len(host1)+1:].strip()}</div>""", unsafe_allow_html=True)
                elif line.startswith(host2 + ":"):
                    st.markdown(f"""<div style='background:#e8f5e9; padding:8px 15px;
                        border-radius:8px; margin:4px 0;'><b style='color:#2e7d32;'>{host2}</b>:
                        {line[len(host2)+1:].strip()}</div>""", unsafe_allow_html=True)
                elif line.strip():
                    st.markdown(f"*{line}*")

            st.download_button("⬇️ Download Script", script,
                               file_name=f"{pod_title}_podcast.txt",
                               use_container_width=True)
