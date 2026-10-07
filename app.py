from pathlib import Path

import streamlit as st

from questions import get_questions

st.set_page_config(page_title="UPSC Mock Test")
st.markdown(
    "<style>" + (Path(__file__).parent / "assets" / "style.css").read_text(encoding="utf-8") + "</style>",
    unsafe_allow_html=True,
)

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
    for key in list(st.session_state):
        if key.startswith("q_"):
            del st.session_state[key]
    st.session_state.quiz_started = False
    st.session_state.questions = []
    st.session_state.answers = []
    st.session_state.current_index = 0
    st.session_state.subject = None
    st.session_state.skipped = []


st.title("UPSC Mock Test MCQ")

if not st.session_state.quiz_started:
    st.subheader("📘 Choose a subject:")
    subjects = ["Polity", "History", "Geography", "Economy"]
    subject = st.selectbox("Subject", subjects)

    if st.button("Start Test"):
        try:
            api_key = st.secrets.get("LLM_API_KEY")
        except FileNotFoundError:
            api_key = None
        if not api_key:
            st.error("Add LLM_API_KEY to .streamlit/secrets.toml before starting a test.")
            st.stop()
        try:
            with st.spinner("Generating questions. This may take a minute..."):
                questions = get_questions(subject, api_key)
        except Exception:
            st.error("Could not load questions. Check your API key and connection, then try again.")
            st.stop()
        if not questions:
            st.error("No valid questions were generated. Please try again.")
            st.stop()
        st.session_state.subject = subject
        st.session_state.questions = questions
        st.session_state.quiz_started = True
        st.rerun()

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
