import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
import json


# 🔐 Replace with your actual Groq API key
GROQ_API_KEY = st.secrets.get("LLM_API_KEY")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=1.5,
    groq_api_key=GROQ_API_KEY
)

template = PromptTemplate(
    input_variables=["subject"],
    template="""
You are a UPSC civil services prelims paper-setter. Create one high-quality MCQ for the subject: {subject}.
Format output strictly as JSON (without code block markers like ```):

{{
  "question": "...",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "B",
  "explanation": "..."
}}
"""
)


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


def generate_questions(subject):
    st.session_state.questions = []
    for _ in range(15):
        result = (template | llm).invoke({"subject": subject})
        try:
            q_json = json.loads(result.content.strip())
            st.session_state.questions.append(q_json)
        except Exception as e:
            print("❌ Failed to parse question:", e, "\nReturned content:\n", result.content)



def reset_quiz():
    st.session_state.quiz_started = False
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.current_index = 0
    st.session_state.subject = None


# --- UI ---

st.title("🧠 UPSC MCQ Generator")

if not st.session_state.quiz_started:
    st.subheader("Choose a subject to start the quiz:")
    subjects = ["Polity", "History", "Geography", "Economy"]
    subject = st.selectbox("Subject", subjects)

    if st.button("Start Test"):
        st.session_state.subject = subject
        st.session_state.quiz_started = True
        generate_questions(subject)

else:
    questions = st.session_state.questions
    index = st.session_state.current_index

    if index < len(questions):
        q = questions[index]
        st.write(f"**Question {index + 1} of {len(questions)}:**")
        st.markdown(q["question"])
        selected = st.radio("Options", q["options"], key=f"q_{index}")

        if st.button("Submit Answer"):
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

    else:
        st.success("🎉 Test Completed!")
        answers = st.session_state.answers
        total = len(answers)
        correct = sum(1 for a in answers if a["is_correct"])
        percent = round((correct / total) * 100, 2)

        st.markdown(f"**Score:** {correct}/{total} ({percent}%)")

        with st.expander("📋 Review Answers"):
            for i, a in enumerate(answers, 1):
                st.write(f"**Q{i}.** {a['question']}")
                st.write(f"Your Answer: {a['selected']} | Correct: {a['correct']}")
                st.write(f"✅ Correct!" if a["is_correct"] else "❌ Incorrect.")
                st.markdown(f"**Explanation:** {a['explanation']}")
                st.markdown("---")

        if st.button("Restart Quiz"):
            reset_quiz()
            st.experimental_rerun()
