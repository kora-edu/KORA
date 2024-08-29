import streamlit as st

#on_click=st.switch_page("./pages/try_out.py")
st.set_page_config("Kora AI", layout="centered", initial_sidebar_state="collapsed")
st.title("Welcome to Kora")
st.page_link(page="./pages/try_out.py", label="Try it out", icon="🤖")
