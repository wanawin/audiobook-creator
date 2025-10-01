import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
import re
import openai
from pathlib import Path

st.set_page_config(page_title="Book to Audio", page_icon="📖")

st.title("📖 PDF Chapters to Expressive MP3")

st.markdown(
    """
    Upload your PDF book, enter the chapter range (e.g. `10-12`),
    and generate an **expressive MP3** for those chapters.
    """
)

openai_api_key = st.text_input("Enter your OpenAI API key", type="password")
uploaded_file = st.file_uploader("Upload PDF", type="pdf")
chapters_input = st.text_input("Chapters (e.g. 10-12)")

if uploaded_file and chapters_input and openai_api_key:
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

            # --- FIXED SPLIT ---
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
                        # remove stray page numbers or single digits floating
                        clean_body = re.sub(r'\s+\d+\s+', ' ', body)
                        chapters.append(f"{title.strip()}\n{clean_body.strip()}")

            if not chapters:
                st.warning("No chapters found in that range.")
            else:
                combined_text = "\n\n".join(chapters)
                st.subheader("Extracted Text Preview")
                st.text_area("Combined Text", combined_text[:5000], height=300)

                # Generate MP3 using OpenAI TTS
                if st.button("Generate Expressive MP3"):
                    openai.api_key = openai_api_key
                    with st.spinner("Generating MP3..."):
                        response = openai.audio.speech.create(
                            model="gpt-4o-mini-tts",
                            voice="alloy",  # expressive voice
                            input=combined_text
                        )
                        mp3_data = response.read()
                        output_file = Path("chapters.mp3")
                        with open(output_file, "wb") as f:
                            f.write(mp3_data)

                    st.success("MP3 ready!")
                    st.download_button(
                        label="Download MP3",
                        data=mp3_data,
                        file_name="chapters.mp3",
                        mime="audio/mpeg"
                    )
    except Exception as e:
        st.error(f"Error: {e}")
