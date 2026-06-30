import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import json
import os
import time
import re

# Constants
CACHE_FILE = "questions_cache.json"
EXPIRY_DURATION = 86400  # 24 hours

# Langchain & API setup
GROQ_API_KEY = st.secrets.get("LLM_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=1.5, groq_api_key=GROQ_API_KEY)

template = PromptTemplate(
    input_variables=["subject"],
    template="""
You are a UPSC civil services prelims paper-setter. Analyse previous 10 year of upsc civil services and past 1 year current affier, Create one high-quality MCQ for the subject: {subject}.
Format output strictly as JSON (without code block markers like 
):

{{
  "question": "...",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "B",
  "explanation": "..."
}}
"""
)

st.markdown("""
<style>
/* Entire app container background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #2e3b4e, #1e293b);
    padding: 1rem;
    color: #ffffff !important;
}

/* Force white text throughout */
.stMarkdown, .stText, .stRadio label, .stSelectbox, .stButton {
    color: #ffffff !important;
}

/* Buttons */
.stButton > button {
    background-color: #4CAF50;
    color: white !important;
    font-weight: bold;
    padding: 10px 20px;
    border-radius: 8px;
    border: none;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

/* Radio buttons */
.stRadio > div {
    background-color: #111827;
    padding: 10px;
    border-radius: 6px;
    box-shadow: 0 0 6px rgba(255, 255, 255, 0.1);
    color: #22c55e !important; /* ✅ Tailwind green-500 */
}

/* Title and headers */
h1, h2, h3, h4, h5, h6 {
    color: #e2e8f0 !important;
}

/* Custom question box */
.question-box {
    background: #1f2937;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 0 12px rgba(255,255,255,0.1);
    margin-bottom: 20px;
}

/* Mobile responsiveness */
@media screen and (max-width: 768px) {
    .stButton button {
        font-size: 14px !important;
        padding: 8px 16px !important;
    }
    .stRadio > div {
        font-size: 14px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Cache utils
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def is_cache_valid(timestamp):
    return (time.time() - timestamp) < EXPIRY_DURATION

def generate_questions(subject):
    new_questions = []
    for _ in range(15):
        result = (template | llm).invoke({"subject": subject})
        try:
            # Robust JSON parsing
            content = result.content.strip()
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            q_json = json.loads(content)
            new_questions.append(q_json)
        except Exception as e:
            print("❌ Parse failed:", e)
    return new_questions

def get_questions(subject):
    cache = load_cache()
    if subject in cache and is_cache_valid(cache[subject]["timestamp"]):
        return cache[subject]["questions"]
    else:
        questions = generate_questions(subject)
        cache[subject] = {
            "questions": questions,
            "timestamp": time.time()
        }
        save_cache(cache)
        return questions

# Session state setup
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "subject" not in st.session_state:
    st.session_state.subject = None
if "skipped" not in st.session_state:
    st.session_state.skipped = []

def reset_quiz():
    st.session_state.quiz_started = False
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.current_index = 0
    st.session_state.subject = None
    st.session_state.skipped = []

# --- MAIN APP ---
st.title("UPSC Mock Test MCQ")

if not st.session_state.quiz_started:
    st.subheader("📘 Choose a subject:")
    subjects = ["Polity", "History", "Geography", "Economy"]
    subject = st.selectbox("Subject", subjects)

    if st.button("🚀 Start Test"):
        st.session_state.subject = subject
        with st.spinner("🔄 Kindly wait please... Generating questions..."):
            st.session_state.questions = get_questions(subject)
            st.session_state.quiz_started = True
        st.rerun()
    else:
        st.info("Please select a subject and click 'Start Test' to begin.")

else:
    questions = st.session_state.questions
    index = st.session_state.current_index

    if index < len(questions):
        q = questions[index]
        st.markdown(f"### ❓ Question {index + 1} of {len(questions)}")
        st.markdown(f"**{q['question']}**")
        selected = st.radio("Choose your answer:", q["options"], key=f"q_{index}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Submit Answer"):
                is_correct = selected.strip()[0] == q["answer"].strip()
                st.session_state.answers.append({
                    "question": q["question"],
                    "selected": selected,
                    "correct": q["answer"],
                    "is_correct": is_correct,
                    "explanation": q["explanation"]
                })
                st.session_state.current_index += 1
                st.rerun()
        with col2:
            if st.button("⏭️ Skip"):
                st.session_state.skipped.append(q)
                st.session_state.current_index += 1
                st.rerun()
    else:
        st.balloons()
        st.success("🎉 Test Completed!")
        answers = st.session_state.answers
        total = len(answers)
        correct = sum(1 for a in answers if a["is_correct"])
        incorrect = total - correct
        skipped = len(st.session_state.skipped)
        negative_marks = round((1/3) * incorrect, 2)
        score = round(correct - negative_marks, 2)

        st.markdown(f"### 📊 Final Score: **{score}** (Correct: {correct}, Incorrect: {incorrect}, Skipped: {skipped})")
        st.markdown(f"🟥 Negative marking applied: **-{negative_marks}**")

        with st.expander("📋 Review Your Answers"):
            for i, a in enumerate(answers, 1):
                st.markdown(f"**Q{i}.** {a['question']}")
                st.markdown(f"- Your Answer: `{a['selected']}` | Correct: `{a['correct']}`")
                st.markdown("✅ Correct!" if a["is_correct"] else "❌ Incorrect.")
                st.markdown(f"**Explanation:** {a['explanation']}")
                st.markdown("---")
            if skipped:
                st.markdown("### ⏭️ Skipped Questions")
                for i, sq in enumerate(st.session_state.skipped, 1):
                    st.markdown(f"**Skipped Q{i}.** {sq['question']}")
                    st.markdown(f"**Answer:** {sq['answer']} — {sq['explanation']}")
                    st.markdown("---")

        if st.button("🔁 Restart Quiz"):
            reset_quiz()
            st.rerun()
