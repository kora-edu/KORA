import streamlit as st
from PyPDF2 import PdfReader
from io import BytesIO

st.header('AI tutor')
subject = st.text_input('What subject do you want to generate exam problems for?')

uploaded_file = st.file_uploader('Upload PDF of previous Exam')
if uploaded_file is not None:
    reader = PdfReader(BytesIO(uploaded_file.getvalue()))
    text = ''
    for page in reader.pages:
        page_text = page.extract_text()
        text += page_text
        print(page_text) # print content
        print(subject)  
    st.text_area('PDF Text Content:', text)
