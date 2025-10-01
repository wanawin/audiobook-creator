import streamlit as st
from gtts import gTTS
import fitz  # PyMuPDF
import re
import io

st.title("📚 PDF Chapters ➜ Expressive MP3")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
chapter_range = st.text_input("Chapters (e.g. 10-12)")

if uploaded_file and chapter_range:
    # Extract PDF text
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in pdf:
        full_text += page.get_text("text") + "\n"

    # Use regex that matches just plain numbers on their own line
    parts = re.split(r"(?m)^\s*(\d+)\s*$", full_text)
    # parts will be like: ['', '1', 'Chapter1 text', '2', 'Chapter2 text', ...]

    # Build dict {chapter_num: text}
    chapters = {}
    for i in range(1, len(parts), 2):
        try:
            num = int(parts[i])
            content = parts[i + 1].strip()
            chapters[num] = content
        except:
            continue

    # Parse requested range
    start, end = map(int, chapter_range.split("-"))
    selected = [chapters[c] for c in range(start, end + 1) if c in chapters]

    if not selected:
        st.error("⚠️ No chapters found in that range.")
    else:
        combined_text = "\n\n".join(selected)

        # Convert to speech with gTTS
        tts = gTTS(combined_text, lang="en", slow=False)
        mp3_bytes = io.BytesIO()
        tts.write_to_fp(mp3_bytes)
        mp3_bytes.seek(0)

        st.audio(mp3_bytes, format="audio/mp3")
        st.download_button("Download MP3", data=mp3_bytes,
                           file_name=f"chapters_{start}-{end}.mp3",
                           mime="audio/mp3")
