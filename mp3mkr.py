import streamlit as st
import fitz  # PyMuPDF
import re
import io
from gtts import gTTS
import subprocess
import tempfile
import os
import time

st.title("📚 PDF Chapter ➜ Expressive MP3 (Free gTTS w/ Retry)")

uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
chapter_input = st.text_input("Enter chapter number (e.g. 10):")

if uploaded_pdf and chapter_input:
    try:
        chap_num = int(chapter_input)
    except ValueError:
        st.error("Please enter just a number (e.g. 10).")
        st.stop()

    # --- Extract text from PDF ---
    pdf_bytes = uploaded_pdf.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"

    # --- Split on lines that contain only a number ---
    parts = re.split(r'(?m)^\s*(\d+)\s*$', full_text)
    chapters = {}
    for i in range(1, len(parts), 2):
        number = int(parts[i])
        text = parts[i+1].strip()
        chapters[number] = text

    if chap_num not in chapters:
        st.error(f"Chapter {chap_num} not found. Available: {sorted(chapters.keys())}")
    else:
        text = chapters[chap_num]
        st.subheader(f"Chapter {chap_num} Preview")
        st.write(text[:500] + "..." if len(text) > 500 else text)

        if st.button("Generate Expressive MP3"):
            with st.spinner("Generating speech..."):
                tts = gTTS(text, lang="en")

                # Create a temp MP3 (retry up to 5 times)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    temp_high = tmp.name

                for attempt in range(5):
                    try:
                        tts.save(temp_high)
                        break
                    except Exception as e:
                        if attempt == 4:
                            st.error(f"TTS failed after retries: {e}")
                            st.stop()
                        wait = 5 * (attempt + 1)
                        st.warning(f"Hit gTTS limit, retrying in {wait}s...")
                        time.sleep(wait)

                # Compress to 64 kbps
                temp_low = temp_high.replace(".mp3", "_64k.mp3")
                subprocess.run([
                    "ffmpeg", "-y", "-i", temp_high, "-b:a", "64k", temp_low
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                with open(temp_low, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download Chapter {chap_num} (64kbps MP3)",
                        data=f,
                        file_name=f"chapter_{chap_num}_64kbps.mp3",
                        mime="audio/mpeg"
                    )

                os.unlink(temp_high)
                os.unlink(temp_low)
