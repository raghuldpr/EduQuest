import os
import json
from groq import Groq
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_study_plan(name, subjects, exam_date, daily_hours, weak_topics, goal):
    """Generate a personalized study plan using Groq LLM."""

    exam_dt = datetime.strptime(exam_date, "%Y-%m-%d").date()
    today = date.today()
    days_left = (exam_dt - today).days

    if days_left <= 0:
        days_left = 1

    prompt = f"""
You are an expert academic coach. Create a detailed study plan in JSON format.

Student: {name}
Subjects: {', '.join(subjects)}
Exam Date: {exam_date}
Days Available: {days_left}
Daily Study Hours: {daily_hours}
Weak Topics: {', '.join(weak_topics) if weak_topics else 'None specified'}
Goal: {goal}

Rules:
- Allocate MORE time to weak topics
- Include revision days every 5th day
- Last 3 days should be full revision
- Break daily hours across multiple subjects
- Each topic should have a duration in hours

Return ONLY valid JSON in this exact format:
{{
  "student": "{name}",
  "exam_date": "{exam_date}",
  "total_days": {days_left},
  "days": [
    {{
      "day": 1,
      "date": "YYYY-MM-DD",
      "topics": [
        {{
          "subject": "Mathematics",
          "topic": "Calculus - Limits",
          "duration": 1.5,
          "type": "New Topic",
          "priority": "High"
        }}
      ]
    }}
  ]
}}
Generate for all {min(days_left, 30)} days. No explanation, only JSON.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000
    )

    raw = response.choices[0].message.content.strip()

    # Clean up if wrapped in code block
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    plan = json.loads(raw)
    return plan


def reschedule_plan(plan, skipped_topics, current_day):
    """Redistribute skipped topics across remaining days."""
    prompt = f"""
You are a study planner. A student has skipped these topics: {json.dumps(skipped_topics)}.
Current day: {current_day}
Redistribute these topics across the remaining days in the plan.
Return only the updated plan JSON with the same structure.
Original plan: {json.dumps(plan)}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000
    )
    raw = response.choices[0].message.content.strip()
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    return json.loads(raw)
