import streamlit as st
import pyttsx3
import fitz  # PyMuPDF
from pydub import AudioSegment
import tempfile
import os

st.title("📚 PDF Chapters ➜ Offline MP3 (No Limits)")
st.write("Select a page range to convert into an MP3 you can email to your iPad.")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")
start_page = st.number_input("Start page", min_value=1, step=1)
end_page = st.number_input("End page", min_value=1, step=1)

bitrate = st.selectbox("Output bitrate (lower = smaller file)", ["32k", "48k", "64k", "96k"], index=1)

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    max_pages = len(doc)
    st.info(f"PDF has {max_pages} pages")

    # Adjust end_page default after loading PDF
    if end_page < start_page:
        end_page = start_page

    if st.button("Generate MP3"):
        text = ""
        for page_num in range(start_page - 1, min(end_page, max_pages)):
            text += doc[page_num].get_text("text") + "\n"

        if not text.strip():
            st.error("No text found in that page range.")
        else:
            st.write("🔊 Converting text to speech offline...")

            # Use pyttsx3 to create a temporary WAV file
            engine = pyttsx3.init()
            tmp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            engine.save_to_file(text, tmp_wav.name)
            engine.runAndWait()

            # Convert WAV to MP3 with chosen bitrate
            tmp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            audio = AudioSegment.from_wav(tmp_wav.name)
            audio.export(tmp_mp3.name, format="mp3", bitrate=bitrate)

            st.success("✅ MP3 ready!")
            with open(tmp_mp3.name, "rb") as f:
                st.download_button(
                    label="⬇️ Download MP3",
                    data=f,
                    file_name=f"chapter_{start_page}-{end_page}.mp3",
                    mime="audio/mpeg",
                )

            # Cleanup
            os.unlink(tmp_wav.name)
            os.unlink(tmp_mp3.name)
