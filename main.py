import streamlit as st
import os
from dotenv import load_dotenv
import PyPDF2
from google import genai
import time

# Page Config
st.set_page_config(page_title="AI Internal Knowledge Agent", page_icon="🤖")
st.title("📄 AI Knowledge Agent")
st.markdown("Upload a PDF and ask questions about its content.")

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Sidebar for PDF Upload
with st.sidebar:
    st.header("Setup")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file:
    # Read PDF text
    reader = PyPDF2.PdfReader(uploaded_file)
    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text()
    
    st.success(f"Successfully loaded {len(reader.pages)} pages!")

    # Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your document:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            # Context-Aware Prompt
            full_query = f"Using ONLY the following text: {pdf_text[:15000]}\n\nQuestion: {prompt}"
            
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_query
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"API Error: {e}")