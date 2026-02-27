import streamlit as st
import whisper
import google.generativeai as genai
import tempfile
import os
from fpdf import FPDF
import json
import re

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lecture Voice-to-Notes Generator",
    page_icon="🎙️",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #f8f9fc; }

    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    .hero h1 { font-size: 2.2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
    .hero p  { font-size: 1rem; opacity: 0.75; margin-top: 0.5rem; }

    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #eef0f4;
    }
    .card h3 { margin-top: 0; color: #1a1a2e; font-size: 1.05rem; }

    .step-badge {
        display: inline-block;
        background: #0f3460;
        color: white;
        border-radius: 50%;
        width: 28px; height: 28px;
        line-height: 28px;
        text-align: center;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 8px;
    }

    .tag {
        display: inline-block;
        background: #e8f4fd;
        color: #0f3460;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 2px;
    }

    .flashcard {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.8rem;
        color: white;
    }
    .flashcard .q { font-weight: 700; font-size: 0.95rem; margin-bottom: 0.5rem; }
    .flashcard .a { opacity: 0.9; font-size: 0.9rem; }

    .quiz-option {
        background: #f0f4ff;
        border: 1px solid #d0dbff;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin: 4px 0;
        font-size: 0.9rem;
    }
    .quiz-answer {
        background: #e6f9f0;
        border: 1px solid #a3e4c1;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin-top: 6px;
        font-size: 0.88rem;
        color: #1a6b3c;
        font-weight: 600;
    }

    .stButton > button {
        background: linear-gradient(135deg, #0f3460, #533483);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.55rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.88; color: white; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.4rem 1.2rem;
        font-weight: 600;
    }
    div[data-testid="stExpander"] { border-radius: 10px; border: 1px solid #eef0f4; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎙️ Lecture Voice-to-Notes Generator</h1>
    <p>Upload a lecture audio/video → Get structured notes, flashcards & quiz instantly using AI</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("🔑 Google Gemini API Key", type="password", placeholder="Paste your API key here")
    whisper_model = st.selectbox("🤖 Whisper Model", ["base", "small", "medium"], index=0,
                                  help="base = fastest, medium = most accurate")
    st.markdown("---")
    st.markdown("### 📋 How it works")
    for step, desc in [
        ("1", "Upload audio/video file"),
        ("2", "Whisper transcribes speech"),
        ("3", "Gemini generates notes"),
        ("4", "Get flashcards & quiz"),
        ("5", "Download as PDF"),
    ]:
        st.markdown(f'<span class="step-badge">{step}</span> {desc}', unsafe_allow_html=True)
        st.markdown("")

# ── Helper Functions ──────────────────────────────────────────────────────────
@st.cache_resource
def load_whisper(model_size):
    return whisper.load_model(model_size)

def transcribe_audio(file_path, model_size="base"):
    model = load_whisper(model_size)
    result = model.transcribe(file_path)
    return result["text"]

def call_gemini(api_key, prompt):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

def generate_notes(api_key, transcript):
    prompt = f"""You are an expert academic note-taker. Given the following lecture transcript, generate well-structured study notes.

Format your response as follows:
## 📚 Lecture Summary
(2-3 sentence overview)

## 🔑 Key Topics
(List main topics covered)

## 📝 Detailed Notes
(Organized notes with headers and bullet points)

## 💡 Key Definitions
(Important terms and their definitions)

## ⚡ Key Takeaways
(5 most important points to remember)

Transcript:
{transcript}
"""
    return call_gemini(api_key, prompt)

def generate_flashcards(api_key, transcript):
    prompt = f"""Based on this lecture transcript, create 8 high-quality flashcards for studying.

Return ONLY a valid JSON array like this (no markdown, no explanation):
[
  {{"question": "What is X?", "answer": "X is..."}},
  {{"question": "...", "answer": "..."}}
]

Transcript:
{transcript}
"""
    raw = call_gemini(api_key, prompt)
    # Clean markdown code blocks if present
    raw = re.sub(r'```json|```', '', raw).strip()
    return json.loads(raw)

def generate_quiz(api_key, transcript):
    prompt = f"""Based on this lecture transcript, create 5 multiple choice questions.

Return ONLY a valid JSON array like this (no markdown, no explanation):
[
  {{
    "question": "Question text?",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "answer": "A) option1",
    "explanation": "Brief explanation"
  }}
]

Transcript:
{transcript}
"""
    raw = call_gemini(api_key, prompt)
    raw = re.sub(r'```json|```', '', raw).strip()
    return json.loads(raw)

def generate_pdf(notes, flashcards, quiz, topic="Lecture"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_fill_color(15, 52, 96)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, "Lecture Notes", ln=True, align="C", fill=True)
    pdf.ln(4)

    # Notes
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(30, 30, 30)
    for line in notes.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
        if line.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(15, 52, 96)
            pdf.cell(0, 8, line.replace("## ", ""), ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(30, 30, 30)
        elif line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(0, 7, line.replace("### ", ""), ln=True)
            pdf.set_font("Helvetica", "", 11)
        else:
            # Remove markdown bold/italic
            line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            line = re.sub(r'\*(.+?)\*', r'\1', line)
            pdf.multi_cell(0, 6, line)

    # Flashcards
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_fill_color(15, 52, 96)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "Flashcards", ln=True, align="C", fill=True)
    pdf.ln(4)

    for i, fc in enumerate(flashcards, 1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(15, 52, 96)
        pdf.multi_cell(0, 7, f"Q{i}: {fc['question']}")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 7, f"A: {fc['answer']}")
        pdf.ln(3)

    # Quiz
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_fill_color(15, 52, 96)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "Practice Quiz", ln=True, align="C", fill=True)
    pdf.ln(4)

    for i, q in enumerate(quiz, 1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 7, f"Q{i}: {q['question']}")
        pdf.set_font("Helvetica", "", 10)
        for opt in q["options"]:
            pdf.cell(0, 6, f"   {opt}", ln=True)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(26, 107, 60)
        pdf.multi_cell(0, 6, f"Answer: {q['answer']}")
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 6, f"Explanation: {q.get('explanation', '')}")
        pdf.set_text_color(30, 30, 30)
        pdf.ln(3)

    return bytes(pdf.output())

# ── Main App ──────────────────────────────────────────────────────────────────
st.markdown('<div class="card"><h3>📁 Upload Your Lecture</h3>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drag & drop or browse",
    type=["mp3", "mp4", "wav", "m4a", "ogg", "webm"],
    help="Supports audio and video files"
)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    st.audio(uploaded_file)
    st.markdown(f'<span class="tag">📄 {uploaded_file.name}</span> <span class="tag">📦 {round(uploaded_file.size/1024/1024, 2)} MB</span>', unsafe_allow_html=True)
    st.markdown("")

    if not api_key:
        st.warning("⚠️ Please enter your Google Gemini API key in the sidebar to continue.")
    else:
        if st.button("🚀 Generate Notes, Flashcards & Quiz"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                # Step 1: Transcribe
                with st.spinner("🎙️ Transcribing audio with Whisper..."):
                    transcript = transcribe_audio(tmp_path, whisper_model)
                st.success("✅ Transcription complete!")

                with st.expander("📄 View Raw Transcript"):
                    st.write(transcript)

                # Step 2: Generate all content
                with st.spinner("🤖 Generating study notes with Gemini..."):
                    notes = generate_notes(api_key, transcript)

                with st.spinner("🃏 Creating flashcards..."):
                    flashcards = generate_flashcards(api_key, transcript)

                with st.spinner("📝 Building quiz questions..."):
                    quiz = generate_quiz(api_key, transcript)

                st.success("✅ All content generated!")
                st.markdown("---")

                # ── Tabs ──────────────────────────────────────────────────
                tab1, tab2, tab3 = st.tabs(["📝 Study Notes", "🃏 Flashcards", "📝 Quiz"])

                with tab1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown(notes)
                    st.markdown('</div>', unsafe_allow_html=True)

                with tab2:
                    st.markdown(f"**{len(flashcards)} flashcards generated**")
                    for i, fc in enumerate(flashcards, 1):
                        st.markdown(f"""
                        <div class="flashcard">
                            <div class="q">Q{i}: {fc['question']}</div>
                            <div class="a">💡 {fc['answer']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                with tab3:
                    st.markdown(f"**{len(quiz)} quiz questions**")
                    for i, q in enumerate(quiz, 1):
                        st.markdown(f"**Q{i}: {q['question']}**")
                        for opt in q["options"]:
                            st.markdown(f'<div class="quiz-option">{opt}</div>', unsafe_allow_html=True)
                        with st.expander("Show Answer"):
                            st.markdown(f'<div class="quiz-answer">✅ {q["answer"]}</div>', unsafe_allow_html=True)
                            if q.get("explanation"):
                                st.info(q["explanation"])
                        st.markdown("")

                # ── PDF Download ──────────────────────────────────────────
                st.markdown("---")
                st.markdown("### 📥 Download Your Notes")
                with st.spinner("📄 Generating PDF..."):
                    pdf_bytes = generate_pdf(notes, flashcards, quiz)

                st.download_button(
                    label="⬇️ Download PDF (Notes + Flashcards + Quiz)",
                    data=pdf_bytes,
                    file_name="lecture_notes.pdf",
                    mime="application/pdf"
                )

            except json.JSONDecodeError:
                st.error("⚠️ Gemini returned unexpected format for flashcards/quiz. Try again.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                os.unlink(tmp_path)

else:
    st.info("👆 Upload a lecture audio or video file to get started.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#999; font-size:0.8rem;'>Built with Streamlit · OpenAI Whisper · Google Gemini · by Ayusha </p>",
    unsafe_allow_html=True
)
