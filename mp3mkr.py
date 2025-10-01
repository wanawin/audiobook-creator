import streamlit as st
import pyttsx3
from pydub import AudioSegment
import tempfile
import os

st.set_page_config(page_title="Audiobook Maker", page_icon="🎧")

st.title("📚 Offline Audiobook Creator")
st.write("Paste one chapter of text and generate an MP3 you can download to play on iPad.")

text = st.text_area("Chapter text", height=300, placeholder="Paste your chapter text here...")

# Initialize TTS engine and list available voices
engine = pyttsx3.init()
voices = engine.getProperty('voices')
voice_options = [f"{i}: {v.name}" for i, v in enumerate(voices)]
selected_voice = st.selectbox("Select Voice", voice_options)

bitrate = st.selectbox("Choose MP3 bitrate (lower = smaller file)", ["32k", "48k", "64k", "96k", "128k"], index=2)

if st.button("Generate MP3"):
    if not text.strip():
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Generating MP3..."):
            # Save to WAV first
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
                wav_path = tmp_wav.name
            voice_index = int(selected_voice.split(":")[0])
            engine.setProperty("voice", voices[voice_index].id)
            engine.save_to_file(text, wav_path)
            engine.runAndWait()

            # Convert WAV to MP3 with chosen bitrate
            mp3_path = wav_path.replace(".wav", ".mp3")
            audio = AudioSegment.from_wav(wav_path)
            audio.export(mp3_path, format="mp3", bitrate=bitrate)

            with open(mp3_path, "rb") as f:
                st.success("✅ MP3 generated!")
                st.download_button(
                    label="⬇️ Download MP3",
                    data=f,
                    file_name="chapter.mp3",
                    mime="audio/mpeg"
                )

            os.remove(wav_path)
            os.remove(mp3_path)
