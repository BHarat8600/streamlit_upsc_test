"""Question generation and a local 24-hour cache."""

import json
from pathlib import Path
import time

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

CACHE_FILE = Path(__file__).parent / "data" / "questions_cache.json"
EXPIRY_DURATION = 86400  # 24 hours

template = PromptTemplate(
    input_variables=["subject"],
    template="""
You are a UPSC civil services prelims paper-setter. Create one high-quality MCQ for the subject: {subject}.
Return only valid JSON, without Markdown code fences:

{{
  "question": "...",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "B",
  "explanation": "..."
}}
"""
)

# Cache utils
def load_cache():
    if CACHE_FILE.exists():
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_cache(cache):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def is_cache_valid(timestamp):
    return (time.time() - timestamp) < EXPIRY_DURATION

def generate_questions(subject, api_key):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=1.5, groq_api_key=api_key)
    new_questions = []
    for _ in range(15):
        result = (template | llm).invoke({"subject": subject})
        try:
            q_json = json.loads(result.content.strip())
            if (
                isinstance(q_json, dict)
                and isinstance(q_json.get("question"), str)
                and isinstance(q_json.get("options"), list)
                and len(q_json["options"]) == 4
                and all(isinstance(option, str) and option.startswith(f"{letter}.")
                        for letter, option in zip("ABCD", q_json["options"]))
                and q_json.get("answer") in ("A", "B", "C", "D")
                and isinstance(q_json.get("explanation"), str)
            ):
                new_questions.append(q_json)
        except (json.JSONDecodeError, TypeError):
            # Skip responses that are not valid JSON.
            continue
    return new_questions

def get_questions(subject, api_key):
    cache = load_cache()
    if subject in cache and is_cache_valid(cache[subject]["timestamp"]):
        return cache[subject]["questions"]
    else:
        questions = generate_questions(subject, api_key)
        cache[subject] = {
            "questions": questions,
            "timestamp": time.time()
        }
        if questions:
            save_cache(cache)
        return questions

