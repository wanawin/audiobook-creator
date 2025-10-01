import streamlit as st
import pyttsx3
from pydub import AudioSegment
import tempfile
import os

st.set_page_config(page_title="Offline Audiobook Creator", page_icon="📚")

st.title("📚 Offline Text → MP3 Audiobook")
st.write("Paste text for one chapter below and click *Generate MP3*.")

text = st.text_area("Chapter text", height=300, placeholder="Paste your chapter text here...")

bitrate = st.selectbox(
    "Choose MP3 Bitrate (lower = smaller file)",
    ["32k", "48k", "64k", "96k", "128k"],
    index=1
)

if st.button("Generate MP3"):
    if not text.strip():
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Generating speech..."):
            # Create a temp wav file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                wav_path = tmp_wav.name
            engine = pyttsx3.init()
            engine.save_to_file(text, wav_path)
            engine.runAndWait()

            # Convert wav to mp3 at chosen bitrate
            mp3_path = wav_path.replace(".wav", ".mp3")
            audio = AudioSegment.from_wav(wav_path)
            audio.export(mp3_path, format="mp3", bitrate=bitrate)

            # Show download link
            with open(mp3_path, "rb") as f:
                st.success("✅ MP3 generated!")
                st.download_button(
                    label="⬇️ Download MP3",
                    data=f,
                    file_name="chapter.mp3",
                    mime="audio/mpeg"
                )

            # Clean up wav
            os.remove(wav_path)
