import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from aitax import Advisor


@st.cache_resource
def get_advisor():
    return Advisor()


st.set_page_config(page_title="AiTax", page_icon=":robot_face:", layout="wide")
st.title("AiTax — Doradca podatkowy wspomagany sztuczną inteligencją")

with st.spinner("Ładowanie bazy wiedzy (layer1 → layer4)..."):
    advisor = get_advisor()

sources = {c["source"] for c in advisor.store.chunks}
st.caption(
    f"Załadowano {len(advisor.store.chunks)} fragmentów z {len(sources)} dokumentów. "
    "System działa lokalnie — dane nie są wysyłane do zewnętrznych serwerów."
)

if "history" not in st.session_state:
    st.session_state.history = []

# Historia konwersacji
for q, a in st.session_state.history:
    with st.chat_message("user"):
        st.write(q)
    with st.chat_message("assistant"):
        st.markdown(a)

# Pole wejściowe — append PRZED renderowaniem sidebaru, żeby download_button
# zawierał aktualne pytanie (Streamlit oblicza data= w momencie renderowania elementu)
question = st.chat_input("Zadaj pytanie podatkowe...")
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("Analizuję..."):
            answer = advisor.ask(question)
        st.markdown(answer)
    st.session_state.history.append((question, answer))

# Pasek boczny — renderowany po append, więc download_button widzi pełną historię
with st.sidebar:
    st.header("Sesja")
    if st.session_state.history:
        export_lines = []
        for i, (q, a) in enumerate(st.session_state.history, 1):
            export_lines.append(f"--- Pytanie {i} ---\n{q}\n\n--- Odpowiedź {i} ---\n{a}\n")
        export_text = "\n".join(export_lines)
        st.download_button(
            label="Pobierz historię sesji (.txt)",
            data=export_text.encode("utf-8"),
            file_name="aitax_sesja.txt",
            mime="text/plain",
        )
        if st.button("Wyczyść historię"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Historia sesji jest pusta.")

    st.divider()
    st.caption(
        "**Zastrzeżenie**: AiTax to prototyp edukacyjny. "
        "Informacje nie stanowią profesjonalnej porady podatkowej. "
        "W razie wątpliwości skonsultuj się z licencjonowanym doradcą podatkowym."
    )
