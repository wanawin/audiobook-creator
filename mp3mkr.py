import streamlit as st
import fitz  # PyMuPDF
import re
import io
from gtts import gTTS
from pydub import AudioSegment

st.title("📖 PDF Chapter → Expressive MP3")

pdf = st.file_uploader("Upload PDF", type="pdf")
chapter = st.text_input("Chapter number (e.g., 10)")

def extract_chapter_text(pdf_file, chapter_num):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            t = page.get_text()
            # very simple header search
            if re.search(rf"\bChapter\s+{chapter_num}\b", t, re.IGNORECASE):
                text += t
    return text.strip()

if pdf and chapter:
    chapter_text = extract_chapter_text(pdf, chapter)
    if chapter_text:
        st.subheader(f"Chapter {chapter} Preview")
        st.write(chapter_text[:500] + "...")
        
        if st.button("Generate Expressive MP3"):
            # break into ~4k char chunks to avoid gTTS 5k limit
            chunks = [chapter_text[i:i+4000] for i in range(0, len(chapter_text), 4000)]
            audio = AudioSegment.silent(duration=0)
            for i, chunk in enumerate(chunks, 1):
                tts = gTTS(chunk, lang='en')
                temp = io.BytesIO()
                tts.write_to_fp(temp)
                temp.seek(0)
                seg = AudioSegment.from_file(temp, format="mp3")
                audio += seg
            # export low bitrate
            out = io.BytesIO()
            audio.export(out, format="mp3", bitrate="48k")  # lower size
            st.download_button("Download MP3", out.getvalue(),
                               file_name=f"chapter_{chapter}.mp3",
                               mime="audio/mpeg")
    else:
        st.error("Couldn’t find that chapter.")
