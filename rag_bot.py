import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Simple in-memory context store (replace with ChromaDB for production)
_pdf_context = ""

def load_pdf(uploaded_file):
    """Extract text from uploaded PDF."""
    try:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text
    except Exception as e:
        return f"Could not read PDF: {e}"

def init_rag(pdf_text):
    """Store PDF content for RAG context."""
    global _pdf_context
    _pdf_context = pdf_text[:8000]  # Limit to avoid token overflow

def ask_question(question):
    """Answer question using Groq, with optional PDF context."""
    global _pdf_context

    system_prompt = """You are a helpful study assistant for students. 
Explain concepts clearly and simply. Use examples, analogies, and bullet points.
If the student seems confused, break it down step by step.
Always end with a quick tip or memory trick."""

    user_content = question
    if _pdf_context:
        user_content = f"""Context from student's syllabus:
{_pdf_context}

Student's question: {question}

Answer based on the syllabus context if relevant, otherwise answer from general knowledge."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.5,
        max_tokens=1000
    )
    return response.choices[0].message.content
