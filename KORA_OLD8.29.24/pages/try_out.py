import streamlit as st
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
import openai 

from latexcompiler import LC
openai.api_key= st.secrets.openai_key
st.header('Kora demo')
gpt_model="gpt-3.5-turbo"
but_disabled = True
file_selected = False

subject_topics = ['Select topic','Mathematics', 'Physics theory', 'Comp-sci']
diffiulty_years = ['Select difficulty level', 'Primary', 'Intermediate', 'Highschool', 'U-grad yr1', 'U-grad yr2-3','Graduate']

subject = st.selectbox('Choose focus topic  ->',
                       (subject_topics)
        )
year_level = st.selectbox('Rough scholar level of understanding required  ->',
                        (diffiulty_years)
        )

def printCurrentFile():
        global file_selected
        file_selected = not file_selected
        st.write(uploaded_file)

selected_temp = st.slider('LLM temperature select (lower = less hallucinations, default=0.3)', 0.1, 1.0, 0.3, 0.05)
uploaded_file = st.file_uploader('Upload PDF', 'pdf', accept_multiple_files=True, on_change=printCurrentFile)
selected_sIndex = subject_topics.index(subject)
selected_YrIndex = diffiulty_years.index(year_level)

# Function to get response from OpenAI GPT
# def get_gpt_response(prompt):
#     sys_prompt = f'You are a helpful and intelligent tutor that has the capability to describe "{subject} "in all ranges of levels of understanding'
#     completion = client.chat.completions.create(
#     model = gpt_model,
#   messages=[
#     {"role": "system", "content": sys_prompt},
#     {"role": "user", "content": prompt}
#   ]
# )
#     return completion.choices[0].message


# code for reading a directory, and indexing it for llama llms
if "messages" not in st.session_state.keys():
     st.session_state.messages = [
        {"role": "assistant", "content": "Enter both a subject, and topic level along with PDF(s) to begin our chat"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
     reader = SimpleDirectoryReader(input_dir="./data", recursive=True)

     data = reader.load_data()
     Settings.llm = OpenAI(gpt_model, selected_temp, system_prompt=f"You are a helpful and intelligent tutor that has the capability to describe {subject} in all ranges of levels of understanding")
     Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002", embed_batch_size=100)
     Settings.transformations = [SentenceSplitter(chunk_size=1024)]
     index = VectorStoreIndex.from_documents(documents=data, transformations=Settings.transformations) 
                 #so fking annoying this was depricated and theres no tutorials OR DOCS on how to pass these args but this works GG
     print("loaded data")
     return index

index = load_data()

def generation_init():
    prompt = f"Generate exam problems for the subject: {subject}, to match the scholarly level of {year_level} for europeans regions"
    st.subheader = ("Latex PDF with generated Q's: ")


if "chat_engine" not in st.session_state.keys(): # initialize the chat engine
     st.session_state.chat_engine = OpenAI(chat_mode="condense_question", verbose=True)
     st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
     st.write(message["content"])

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("processing.."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) #adds response to history



if selected_sIndex !=0 and selected_YrIndex !=0 and uploaded_file:
    but_disabled = False
    gen_button = st.button('Generate question', on_click=generation_init, type="primary", disabled=but_disabled)
