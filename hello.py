import streamlit as st

st.set_page_config(page_title="Hello App", layout="centered")

st.title("Hello Streamlit!")
st.write("Welcome to your first Streamlit app.")

name = st.text_input("Enter your name:")
if name:
    st.success(f"Hello, {name}! 👋")

st.write("---")
st.info("This is a simple Streamlit demo app.")
