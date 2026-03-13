"""
adaptive.py — Adaptive Challenge Engine
Dynamically adjusts difficulty based on student performance
"""
import os, json
from groq import Groq
from dotenv import load_dotenv
from database import get_difficulty, update_quiz_performance, add_xp, update_mission, award_badge

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DIFFICULTY_LABELS = {1: "Easy", 2: "Medium", 3: "Hard"}
DIFFICULTY_DESC   = {
    1: "simple recall and basic concept questions",
    2: "application and understanding questions",
    3: "analysis, problem-solving and advanced questions"
}

XP_MAP = {1: 10, 2: 20, 3: 30}  # XP per correct answer by difficulty


def generate_adaptive_questions(subject, topic, difficulty, count=5):
    """Generate questions at a specific difficulty level."""
    desc = DIFFICULTY_DESC.get(difficulty, "medium level")
    prompt = f"""Generate {count} multiple choice questions about "{topic}" in {subject}.
Difficulty: {DIFFICULTY_LABELS[difficulty]} — focus on {desc}.

Return ONLY a valid JSON array:
[
  {{
    "question": "Question text?",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "answer": "A) option1",
    "explanation": "Brief explanation",
    "difficulty": {difficulty}
  }}
]
No preamble, only JSON array."""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000
    )
    raw = resp.choices[0].message.content.strip()
    if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:   raw = raw.split("```")[1].split("```")[0].strip()
    return json.loads(raw)


def evaluate_performance(correct, total, current_difficulty):
    """Decide next difficulty based on score."""
    score = correct / max(total, 1)
    if score >= 0.8:
        next_diff  = min(current_difficulty + 1, 3)
        feedback   = "🔥 Excellent! Difficulty increased!"
        status     = "up"
    elif score >= 0.5:
        next_diff  = current_difficulty
        feedback   = "✅ Good job! Keep going at this level."
        status     = "same"
    else:
        next_diff  = max(current_difficulty - 1, 1)
        feedback   = "💡 Let's practice more at a lower level."
        status     = "down"
    return next_diff, feedback, status, score


def get_ai_explanation(subject, topic, question, correct_answer):
    """Get AI explanation for a wrong answer."""
    prompt = f"""A student studying {subject} got this question wrong:
Question: {question}
Correct Answer: {correct_answer}
Topic: {topic}

Give a clear, simple 3-sentence explanation of why this is the correct answer.
Use an analogy or real-world example if possible. Be encouraging."""
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=300
    )
    return resp.choices[0].message.content
