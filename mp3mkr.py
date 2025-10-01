import streamlit as st
import pyttsx3
import tempfile
import PyPDF2
import re
import os

st.title("📖 PDF to Expressive MP3 (Offline)")

uploaded = st.file_uploader("Upload PDF", type=["pdf"])
chapters_input = st.text_input("Chapters to export (e.g. 10-12 or 10,11,12)")

if uploaded and chapters_input:
    # ---- Read PDF ----
    reader = PyPDF2.PdfReader(uploaded)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += "\n" + text

    # ---- Split into chapters ----
    # handles either "Chapter 10" OR just "10" at line start
    parts = re.split(r'(?:chapter\s*)?(\b\d+\b)', full_text, flags=re.IGNORECASE)
    # parts = [before first chapter, "1", text, "2", text, ...]
    chapters = {}
    for i in range(1, len(parts), 2):
        num = parts[i].strip()
        body = parts[i+1].strip()
        if num.isdigit():
            chapters[int(num)] = body

    # ---- Parse user input ----
    requested = []
    for chunk in chapters_input.split(","):
        if "-" in chunk:
            start, end = chunk.split("-")
            requested.extend(range(int(start), int(end)+1))
        else:
            requested.append(int(chunk))

    combined = ""
    for c in requested:
        if c in chapters:
            combined += f"Chapter {c}\n\n{chapters[c]}\n\n"

    if not combined.strip():
        st.error("⚠️ No chapters found. Make sure your numbers match the PDF headings.")
    else:
        st.success(f"Found {len(requested)} chapters")

        if st.button("Generate Expressive MP3"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                engine = pyttsx3.init()
                # Optional: make voice a bit expressive
                rate = engine.getProperty('rate')
                engine.setProperty('rate', rate - 30)
                voices = engine.getProperty('voices')
                if voices:
                    engine.setProperty('voice', voices[0].id)
                engine.save_to_file(combined, tmpfile.name)
                engine.runAndWait()
                st.audio(tmpfile.name)
                with open(tmpfile.name, "rb") as f:
                    st.download_button("⬇️ Download MP3", f, file_name="chapters.mp3")
