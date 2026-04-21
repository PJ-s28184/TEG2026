import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from aitax import Advisor


@st.cache_resource
def get_advisor():
    return Advisor()


st.set_page_config(page_title="AiTax", page_icon="💼")
st.title("AiTax — prototyp doradcy podatkowego")

with st.spinner("Ładowanie bazy wiedzy (layer1 → layer4)..."):
    advisor = get_advisor()

sources = {c["source"] for c in advisor.store.chunks}
st.caption(f"Załadowano {len(advisor.store.chunks)} fragmentów z {len(sources)} dokumentów.")

if "history" not in st.session_state:
    st.session_state.history = []

for q, a in st.session_state.history:
    with st.chat_message("user"):
        st.write(q)
    with st.chat_message("assistant"):
        st.write(a)

question = st.chat_input("Zadaj pytanie...")
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Myślę..."):
            answer = advisor.ask(question)
        st.write(answer)
    st.session_state.history.append((question, answer))
