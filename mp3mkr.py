import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
import re
import pyttsx3
from pathlib import Path
import tempfile

st.set_page_config(page_title="Book to Audio (Free TTS)", page_icon="📖")
st.title("📖 PDF Chapters to MP3 (Offline / Free TTS)")

st.markdown(
    """
    Upload your PDF, enter the chapter range (e.g. `10-12`), and create an MP3
    **without needing an API key**. This uses local TTS (`pyttsx3`).
    """
)

uploaded_file = st.file_uploader("Upload PDF", type="pdf")
chapters_input = st.text_input("Chapters (e.g. 10-12)")

if uploaded_file and chapters_input:
    try:
        # Read PDF text
        pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        full_text = ""
        for page in pdf:
            full_text += page.get_text()

        # Parse chapters range
        m = re.match(r"(\d+)\s*-\s*(\d+)", chapters_input)
        if not m:
            st.error("Please enter range like 10-12")
        else:
            start_ch, end_ch = int(m.group(1)), int(m.group(2))

            # Split on headings like "Chapter 10" OR just "10" at line start
            parts = re.split(r'(?i)(?:chapter\s+)?(\b\d+\b)', full_text)

            chapters = []
            for i in range(1, len(parts), 2):
                title = parts[i]
                body = parts[i+1] if i+1 < len(parts) else ""
                match = re.search(r'(\d+)', title)
                if match:
                    num = int(match.group(1))
                    if start_ch <= num <= end_ch:
                        clean_body = re.sub(r'\s+\d+\s+', ' ', body)
                        chapters.append(f"{title.strip()}\n{clean_body.strip()}")

            if not chapters:
                st.warning("No chapters found in that range.")
            else:
                combined_text = "\n\n".join(chapters)
                st.subheader("Extracted Text Preview")
                st.text_area("Combined Text", combined_text[:5000], height=300)

                if st.button("Generate MP3 (Free TTS)"):
                    with st.spinner("Generating MP3... (this may take a few minutes)"):
                        engine = pyttsx3.init()
                        # Optional: set slower rate & voice for clarity
                        rate = engine.getProperty('rate')
                        engine.setProperty('rate', rate - 30)
                        voices = engine.getProperty('voices')
                        if voices:
                            engine.setProperty('voice', voices[0].id)
                        # Generate temporary MP3
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        temp_path = Path(temp_file.name)
                        engine.save_to_file(combined_text, str(temp_path))
                        engine.runAndWait()
                        temp_file.close()
                    st.success("MP3 ready!")
                    with open(temp_path, "rb") as f:
                        st.download_button(
                            label="Download MP3",
                            data=f,
                            file_name="chapters.mp3",
                            mime="audio/mpeg"
                        )
    except Exception as e:
        st.error(f"Error: {e}")
