# 🎙️ Lecture Voice-to-Notes Generator

An AI-powered web app that converts lecture audio/video into structured study notes, flashcards, and quizzes.

## ⚙️ Tech Stack
- **Frontend:** Streamlit
- **Speech-to-Text:** OpenAI Whisper (runs locally, free)
- **AI Summarization:** Google Gemini 1.5 Flash
- **PDF Generation:** FPDF2
- **Language:** Python

## 🚀 How to Run Locally

### Step 1 — Clone / Download this folder

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ Whisper also needs `ffmpeg` installed:
> - Windows: https://ffmpeg.org/download.html
> - Mac: `brew install ffmpeg`
> - Linux: `sudo apt install ffmpeg`

### Step 3 — Run the app
```bash
streamlit run app.py
```

### Step 4 — Open in browser
Go to `http://localhost:8501`

### Step 5 — Enter your Google Gemini API Key
Get a free key at: https://aistudio.google.com/app/apikey

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Push this folder to a GitHub repo
2. Go to https://streamlit.io/cloud
3. Connect your GitHub repo
4. Set main file as `app.py`
5. Click Deploy!

---

## 📁 Features
- ✅ Upload audio/video (mp3, mp4, wav, m4a, ogg, webm)
- ✅ Auto transcription with Whisper
- ✅ AI-generated structured study notes
- ✅ 8 flashcards (Q&A format)
- ✅ 5 multiple choice quiz questions with answers
- ✅ Download everything as a PDF

---

Built by M Nanthini | CSE | Capstone Project
