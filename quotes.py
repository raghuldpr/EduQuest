"""
quotes.py — Goal-based motivational quotes for distraction popups
"""

GOAL_QUOTES = {
    "Doctor": [
        "Every minute you study today saves a life tomorrow. 🩺",
        "Future Dr. {name} — your patients are counting on you.",
        "MBBS doesn't come easy. Close Instagram, open your textbook.",
        "The doctor you want to be is built in moments like this.",
        "Your stethoscope is waiting. So is your syllabus.",
        "One day your patient will thank you for studying right now.",
        "Medical school is hard. Instagram can wait. Lives cannot.",
        "You chose medicine to make a difference. Make one right now.",
    ],
    "Engineer": [
        "The bridge you'll build one day starts with the concepts you learn today. ⚙️",
        "Future Engineer {name} — great systems are built one study session at a time.",
        "Every algorithm you master today powers the product you'll build tomorrow.",
        "Engineers solve problems. Right now the problem is distraction. Solve it.",
        "Your code won't debug itself. Close the app, open your IDE.",
        "The next big tech innovation could come from you — but only if you study.",
        "Silicon Valley wasn't built on scrolling. Get back to work.",
        "GATE, placements, campus — all need you focused RIGHT NOW.",
    ],
    "Architect": [
        "The buildings you'll design one day start with the designs you study today. 🏛️",
        "Future Architect {name} — great structures are built on strong foundations.",
        "Every blueprint starts with a student who chose studying over scrolling.",
        "Your portfolio won't build itself. Close Instagram, open AutoCAD.",
        "The skyline you'll shape is being designed right now — in your mind.",
        "Architecture is art meets engineering. Master both. Not Instagram.",
        "Frank Lloyd Wright didn't get distracted. Neither should you.",
    ],
    "Scientist": [
        "The discovery that changes the world might be yours — if you study. 🔬",
        "Future Scientist {name} — breakthroughs happen to those who prepare.",
        "Every Nobel Prize winner started by closing distractions and opening books.",
        "Your hypothesis needs testing. Instagram doesn't count as research.",
        "Science waits for no one. Get back to your studies.",
    ],
    "Lawyer": [
        "Future Lawyer {name} — every case you'll win starts with studying today. ⚖️",
        "The courtroom demands sharp minds. Sharpen yours now.",
        "Your arguments won't write themselves. Close the app.",
        "Great lawyers are made in study sessions like this one.",
    ],
    "Teacher": [
        "The students you'll inspire are waiting for you to become great first. 📚",
        "Future Teacher {name} — your knowledge is your greatest tool.",
        "Every student you'll teach deserves a teacher who studied hard.",
        "Shape minds. Start by shaping your own. Close Instagram.",
    ],
    "Other": [
        "Your future self is watching. Make them proud. 💪",
        "Success doesn't scroll through Instagram. Get back to work, {name}.",
        "Every second of focus today is an investment in your future.",
        "Discipline is choosing your goals over your distractions.",
        "The person you want to become is built right now, in this moment.",
        "Hard work today. Easy life tomorrow. Close the app.",
    ]
}

BLOCKED_APPS = [
    "instagram.com", "facebook.com", "twitter.com", "x.com",
    "tiktok.com", "snapchat.com", "reddit.com", "9gag.com",
    "netflix.com", "primevideo.com", "hotstar.com"
]

YOUTUBE_STUDY_KEYWORDS = [
    "lecture", "tutorial", "study", "learn", "course",
    "explained", "how to", "education", "class", "lesson",
    "notes", "revision", "exam", "NPTEL", "khan academy"
]

import random

def get_quote(goal, name="Student"):
    quotes = GOAL_QUOTES.get(goal, GOAL_QUOTES["Other"])
    quote = random.choice(quotes)
    return quote.replace("{name}", name)

def is_distraction_site(url):
    url = url.lower()
    return any(site in url for site in BLOCKED_APPS)

def is_study_youtube(url, title=""):
    combined = (url + " " + title).lower()
    return any(kw in combined for kw in YOUTUBE_STUDY_KEYWORDS)
