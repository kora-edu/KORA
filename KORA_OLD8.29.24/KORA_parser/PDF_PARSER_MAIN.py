import streamlit as st
import os
import asyncio
import fitz  # PyMuPDF
import re
from openai import AsyncOpenAI

openai_api_key = os.getenv("OPENAI_KEY")

if openai_api_key is None:
    st.error("OPENAI_KEY environment variable is not set")
else:
    st.header('PDF Math Question Extractor')

    gpt_model = "gpt-4"
    client = AsyncOpenAI(api_key=openai_api_key)

    async def get_response(messages):
        try:
            response = await client.chat.completions.create(
                model=gpt_model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error generating response: {e}")
            return None

    def run_async(func, *args):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(func(*args))

    def save_math_questions(file_name, math_questions):
        if math_questions:
            output_dir = "returned_questions"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"{file_name}_math_questions.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(math_questions)
            st.success(f"Math questions saved to {file_path}")
        else:
            st.error("No math questions to save.")

    def extract_questions_from_pdf(file):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        # Use regex to remove numbers and bullet points
        cleaned_text = re.sub(r'(\d+\.\s*|[a-zA-Z]+\.\s*|\(\d+\s*marks\)|\n\s*-)', '', text)
        return cleaned_text

    # File uploader for multiple PDFs
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = os.path.splitext(uploaded_file.name)[0]  # Get the file name without extension
            st.write(f"Uploaded file: {uploaded_file.name}")
            
            # Extract questions from PDF
            pdf_text = extract_questions_from_pdf(uploaded_file)
            
            # Prepare the message to send to GPT
            prompt = f"Extract the math questions from the following text:\n\n{pdf_text}"
            messages = [
                {'role': 'system', 'content': 'You are a helpful and knowledgeable assistant.'},
                {'role': 'user', 'content': prompt},
            ]
            
            # Get response from GPT
            with st.spinner(f"Identifying math questions from {uploaded_file.name}..."):
                math_questions = run_async(get_response, messages)
                
            # Save the math questions to a text file
            save_math_questions(file_name, math_questions)

    for message in st.session_state.get("messages", []):
        st.write(f"{message['role'].capitalize()}: {message['content']}")
