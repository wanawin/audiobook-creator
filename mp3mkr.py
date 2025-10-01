import streamlit as st
import pyttsx3
from pydub import AudioSegment
import tempfile
import os

st.set_page_config(page_title="Audiobook Creator", page_icon="🎧")
st.title("📖 Chapter to MP3")

text = st.text_area("Paste chapter text here", height=300)

# Initialize voices
engine = pyttsx3.init()
voices = engine.getProperty("voices")
voice_options = [f"{i}: {v.name}" for i, v in enumerate(voices)]
selected_voice = st.selectbox("Select Voice", voice_options)
bitrate = st.selectbox("MP3 bitrate (smaller = smaller file)", ["32k", "48k", "64k", "96k", "128k"], index=2)

if st.button("Generate MP3"):
    if not text.strip():
        st.warning("Please paste text first.")
    else:
        with st.spinner("Generating audio..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                wav_path = tmp_wav.name
                voice_index = int(selected_voice.split(":")[0])
                engine.setProperty("voice", voices[voice_index].id)
                engine.save_to_file(text, wav_path)
                engine.runAndWait()

            mp3_path = wav_path.replace(".wav", ".mp3")
            audio = AudioSegment.from_wav(wav_path)
            audio.export(mp3_path, format="mp3", bitrate=bitrate)

            with open(mp3_path, "rb") as f:
                st.success("✅ MP3 ready!")
                st.download_button(
                    label="⬇️ Download MP3",
                    data=f,
                    file_name="chapter.mp3",
                    mime="audio/mpeg"
                )

            os.remove(wav_path)
            os.remove(mp3_path)
