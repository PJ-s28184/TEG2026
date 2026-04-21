import streamlit as st
from datetime import date

st.set_page_config(
    page_title="AiTax — Interaktywny Doradca Podatkowy AI",
    page_icon="💼",
    layout="wide",
)


# Helpers
def send_payload(endpoint_name: str, payload: dict):
    """
    Mock function for forwarding data to backend.
    Replace this with a real API call later, e.g. requests.post(...).
    """
    st.session_state.setdefault("sent_payloads", []).append(
        {
            "endpoint": endpoint_name,
            "payload": payload,
            "sent_at": str(date.today()),
        }
    )

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": (
                "Cześć! Jestem AiTax. Mogę pomóc w pytaniach o odliczenia, "
                "porównanie scenariuszy podatkowych, przygotowanie dokumentów "
                "oraz wyjaśnianie przepisów prostym językiem."
            ),
        }
    ]

if "sent_payloads" not in st.session_state:
    st.session_state.sent_payloads = []


# Sidebar
with st.sidebar:
    st.title("AiTax")
    st.caption("Mockup frontendowy w Streamlit")

    st.markdown("### Tryb działania")
    app_mode = st.radio(
        "Wybierz widok",
        [
            "Konsultacja AI",
            "Profil podatnika",
            "Porównanie scenariuszy",
            "Dokumenty i raportowanie",
            "Admin / Debug payloadów",
        ],
    )

    st.markdown("### Status systemu")
    st.success("Frontend aktywny")
    st.info("Backend AI: do podpięcia")
    st.info("Baza wektorowa: do podpięcia")
    st.info("Graf wiedzy: do podpięcia")

    st.markdown("### Ustawienia użytkownika")
    user_type = st.selectbox(
        "Typ użytkownika",
        [
            "Osoba indywidualna",
            "Freelancer",
            "Student",
            "Samozatrudniony",
            "Właściciel małego biznesu",
        ],
    )
    language = st.selectbox("Język interfejsu", ["Polski"])
    show_references = st.toggle("Pokazuj referencje do przepisów", value=True)
    show_explanations = st.toggle("Pokazuj uzasadnienia krok po kroku", value=True)


# Header
st.title(" AiTax — Interaktywny Doradca Podatkowy AI")
st.markdown(
    "System do zadawania pytań podatkowych, symulacji scenariuszy oraz "
    "przygotowania danych do dalszej analizy przez backend AI."
)

col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Tryb", app_mode)
col_b.metric("Typ użytkownika", user_type)
col_c.metric("Referencje", "ON" if show_references else "OFF")
col_d.metric("Wyjaśnienia", "ON" if show_explanations else "OFF")

st.divider()

# View 1: Chat / Consultation
if app_mode == "Konsultacja AI":
    left, right = st.columns([2.2, 1])

    with left:
        st.subheader("Konsultacja z AiTax")
        st.caption("Widok rozmowy z doradcą AI")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        prompt = st.chat_input("Np. Jakie wydatki mogę odliczyć jako freelancer?")
        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            send_payload(
                "chat_query",
                {
                    "message": prompt,
                    "user_type": user_type,
                    "show_references": show_references,
                    "show_explanations": show_explanations,
                },
            )

            mock_answer = (
                "To jest odpowiedź przykładowa z frontendu. W docelowej wersji w tym miejscu "
                "pojawi się odpowiedź wygenerowana przez backend AiTax na podstawie RAG, "
                "grafu wiedzy i modelu językowego."
            )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": mock_answer}
            )
            st.rerun()

    with right:
        st.subheader("Szybkie akcje")
        quick_question = st.selectbox(
            "Wybierz gotowe pytanie",
            [
                "Jakie wydatki może odliczyć freelancer?",
                "Jakie dokumenty są potrzebne do rozliczenia rocznego?",
                "Wyjaśnij prostym językiem wybrany przepis podatkowy.",
                "Porównaj ryczałt i skalę podatkową.",
            ],
        )

        if st.button("Wyślij gotowe pytanie", use_container_width=True):
            st.session_state.chat_history.append(
                {"role": "user", "content": quick_question}
            )
            send_payload(
                "chat_query",
                {
                    "message": quick_question,
                    "user_type": user_type,
                    "show_references": show_references,
                    "show_explanations": show_explanations,
                },
            )
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": "Frontend wysłał pytanie do dalszego przetwarzania. Tutaj pojawi się odpowiedź backendu.",
                }
            )
            st.rerun()

        st.markdown("### Co ten widok ma obsługiwać")
        st.markdown(
            "- pytania ogólne o podatki  "
            "- wyjaśnianie przepisów  "
            "- follow-upy w tej samej sesji  "
            "- odpowiedzi z referencjami i uzasadnieniem"
        )


# View 2: Taxpayer profile
elif app_mode == "Profil podatnika":
    st.subheader("Profil podatnika i kalkulacja scenariusza")
    st.caption("Formularz wejściowy do przesyłania danych do silnika analizy podatkowej")

    with st.form("taxpayer_profile_form"):
        c1, c2 = st.columns(2)

        with c1:
            full_name = st.text_input("Imię i nazwisko")
            taxpayer_role = st.selectbox(
                "Status podatnika",
                [
                    "Freelancer",
                    "Samozatrudniony",
                    "Właściciel firmy",
                    "Student z dodatkowym dochodem",
                    "Pracownik etatowy",
                ],
            )
            income_main = st.number_input("Roczny dochód główny (PLN)", min_value=0.0, step=1000.0)
            income_other = st.number_input("Dodatkowe źródła dochodu (PLN)", min_value=0.0, step=500.0)
            taxation_form = st.selectbox(
                "Obecna forma rozliczenia",
                ["Skala podatkowa", "Podatek liniowy", "Ryczałt", "Nie wiem"],
            )

        with c2:
            expenses_total = st.number_input("Łączne wydatki firmowe / kwalifikowane (PLN)", min_value=0.0, step=500.0)
            home_office = st.number_input("Koszty biura domowego (PLN)", min_value=0.0, step=100.0)
            software_costs = st.number_input("Koszty oprogramowania (PLN)", min_value=0.0, step=100.0)
            internet_costs = st.number_input("Koszty internetu / telefonu (PLN)", min_value=0.0, step=100.0)
            notes = st.text_area("Dodatkowe informacje", placeholder="Np. mam działalność od połowy roku, pracuję zdalnie, mam koszty sprzętu...")

        submitted = st.form_submit_button("Prześlij profil do analizy", use_container_width=True)

        if submitted:
            payload = {
                "full_name": full_name,
                "taxpayer_role": taxpayer_role,
                "user_type": user_type,
                "income_main": income_main,
                "income_other": income_other,
                "taxation_form": taxation_form,
                "expenses_total": expenses_total,
                "home_office": home_office,
                "software_costs": software_costs,
                "internet_costs": internet_costs,
                "notes": notes,
            }
            send_payload("taxpayer_profile_analysis", payload)
            st.success("Dane zostały zebrane i wysłane do dalszego przetwarzania.")
            st.json(payload)

    st.markdown("### Oczekiwany wynik backendu")
    st.markdown(
        "- szacowany podatek  "
        "- lista potencjalnych odliczeń  "
        "- rozbicie obliczeń krok po kroku  "
        "- sugestie optymalizacji"
    )


# View 3: Scenario comparison
elif app_mode == "Porównanie scenariuszy":
    st.subheader("Porównanie scenariuszy podatkowych")
    st.caption("Widok do wysyłania wariantów \"co-jeśli\" do backendu")

    with st.form("scenario_compare_form"):
        base_income = st.number_input("Roczny dochód (PLN)", min_value=0.0, step=1000.0, value=80000.0)
        base_expenses = st.number_input("Roczne wydatki (PLN)", min_value=0.0, step=1000.0, value=20000.0)

        st.markdown("### Porównywane opcje")
        compare_scale = st.checkbox("Skala podatkowa", value=True)
        compare_linear = st.checkbox("Podatek liniowy 19%", value=True)
        compare_lump_sum = st.checkbox("Ryczałt", value=True)

        lump_sum_rate = st.selectbox("Stawka ryczałtu (jeśli dotyczy)", ["8.5%", "12%", "15%", "17%"])
        optimization_goal = st.selectbox(
            "Cel użytkownika",
            [
                "Najniższy podatek",
                "Najprostsze rozliczenie",
                "Najbezpieczniejszy wariant",
                "Porównanie wszystkich opcji",
            ],
        )

        compare_submit = st.form_submit_button("Porównaj scenariusze", use_container_width=True)

        if compare_submit:
            payload = {
                "income": base_income,
                "expenses": base_expenses,
                "compare_scale": compare_scale,
                "compare_linear": compare_linear,
                "compare_lump_sum": compare_lump_sum,
                "lump_sum_rate": lump_sum_rate,
                "optimization_goal": optimization_goal,
                "user_type": user_type,
            }
            send_payload("scenario_comparison", payload)
            st.success("Scenariusze zostały wysłane do analizy.")
            st.json(payload)

    st.markdown("### Miejsce na wynik")
    result_cols = st.columns(3)
    result_cols[0].info("Skala podatkowa\n\nTutaj pojawi się wynik")
    result_cols[1].info("Podatek liniowy\n\nTutaj pojawi się wynik")
    result_cols[2].info("Ryczałt\n\nTutaj pojawi się wynik")

    st.markdown("### Docelowo")
    st.markdown(
        "Tutaj można później dodać tabelę porównawczą, wykres słupkowy oraz rekomendację najlepszego wariantu."
    )


# View 4: Documents / reporting
elif app_mode == "Dokumenty i raportowanie":
    st.subheader("Dokumenty wymagane do rozliczenia i raportowania")
    st.caption("Formularz do wygenerowania checklisty dokumentów")

    with st.form("documents_form"):
        employment_type = st.selectbox(
            "Typ dochodu / aktywności",
            [
                "Umowa o pracę",
                "Samozatrudnienie",
                "Freelancing",
                "Mała firma",
                "Wiele źródeł dochodu",
            ],
        )
        has_business_costs = st.checkbox("Mam koszty uzyskania przychodu / koszty firmowe", value=True)
        has_assets = st.checkbox("Posiadam środki trwałe / sprzęt do amortyzacji")
        needs_annual_return = st.checkbox("Chcę przygotować checklistę do rozliczenia rocznego", value=True)
        extra_context = st.text_area(
            "Dodatkowy kontekst",
            placeholder="Np. mam faktury za internet, laptop, samochód, pracuję z domu...",
        )

        docs_submit = st.form_submit_button("Wygeneruj checklistę", use_container_width=True)

        if docs_submit:
            payload = {
                "employment_type": employment_type,
                "has_business_costs": has_business_costs,
                "has_assets": has_assets,
                "needs_annual_return": needs_annual_return,
                "extra_context": extra_context,
                "user_type": user_type,
            }
            send_payload("documents_checklist", payload)
            st.success("Zapytanie o checklistę zostało wysłane.")
            st.json(payload)

    st.markdown("### Podgląd oczekiwanego rezultatu")
    st.checkbox("PIT-11 / odpowiednie formularze", value=True)
    st.checkbox("Faktury kosztowe", value=False)
    st.checkbox("Dowody opłat za internet / telefon", value=False)
    st.checkbox("Dokumentacja środków trwałych", value=False)
    st.checkbox("Potwierdzenia ulg i odliczeń", value=False)


# View 5: Debug / payloads
else:
    st.subheader("Admin / Debug payloadów")
    st.caption("Widok pomocniczy do testowania frontendu przed podpięciem backendu")

    if st.session_state.sent_payloads:
        st.write(f"Liczba wysłanych payloadów: {len(st.session_state.sent_payloads)}")
        for i, item in enumerate(reversed(st.session_state.sent_payloads), start=1):
            with st.expander(f"Payload #{i} — {item['endpoint']}"):
                st.json(item)
    else:
        st.info("Jeszcze nie wysłano żadnych danych.")

    if st.button("Wyczyść historię payloadów", use_container_width=True):
        st.session_state.sent_payloads = []
        st.success("Historia payloadów została wyczyszczona.")


st.divider()
st.caption(
    "To jest mockup frontendowy. Obecnie formularze i chat tylko zbierają dane i przygotowują je do dalszego przesłania do backendu AiTax."
)