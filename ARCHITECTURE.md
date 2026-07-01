# Architecture Overview: UPSC Mock Test MCQ

## Project Overview
This is a Streamlit-based web application that allows users to generate and take mock test Multiple Choice Questions (MCQs) for the UPSC Civil Services Prelims exam. It leverages Large Language Models (LLMs) via the Groq API to generate high-quality questions based on specific subjects.

## Technology Stack
- **Frontend**: Streamlit
- **LLM Orchestration**: LangChain
- **LLM Provider**: Groq (Llama 3.3 70B)
- **Caching**: Local JSON file (`questions_cache.json`)
- **Environment Management**: Streamlit Secrets

## Component Breakdown
1. **UI Layer (app.py)**: Handles user interaction, session state management, and rendering of the quiz interface. It uses custom CSS for styling.
2. **Cache Layer**: Provides a mechanism to store generated questions for 24 hours to reduce API costs and improve performance.
3. **LLM Integration Layer**: Defines the prompt templates and interacts with the Groq API to generate JSON-formatted questions.
4. **Logic Layer**: Manages quiz state (start, progress, scoring, results) and question generation logic.

## Data Flow
1. User selects a subject and clicks "Start Test".
2. The app checks if valid questions exist in the local cache for that subject.
3. If not, it calls the LLM to generate 15 questions.
4. The generated questions are saved to the cache and displayed to the user.
5. User answers questions; the app tracks correct/incorrect answers and calculates a score with negative marking.
6. Final score and review are presented at the end.
