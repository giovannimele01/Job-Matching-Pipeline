import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Job Matcher Pipeline")
st.title("Job Matcher Pipeline")

if st.button("Controlla stato API"):
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        st.json(response.json())
    except requests.exceptions.RequestException as exc:
        st.error(f"Impossibile raggiungere l'API: {exc}")

st.header("Carica documenti")
cv_file = st.file_uploader("CV", type=["pdf", "docx", "txt"])
job_file = st.file_uploader("Job Description", type=["pdf", "docx", "txt"])

if st.button("Genera match"):
    if not cv_file or not job_file:
        st.warning("Carica sia il CV che la Job Description prima di generare il match.")
    else:
        files = {
            "cv": (cv_file.name, cv_file.getvalue()),
            "job_desc": (job_file.name, job_file.getvalue()),
        }
        try:
            with st.spinner("Analisi in corso..."):
                response = requests.post(f"{API_URL}/match", files=files, timeout=120)
        except requests.exceptions.RequestException as exc:
            st.error(f"Impossibile raggiungere l'API: {exc}")
        else:
            if response.status_code == 200:
                result = response.json()
                st.metric("Punteggio match", f"{result['punteggio_match']}/100")
                st.subheader("Lacune tecniche")
                st.write(result["lacune_tecniche"] or "Nessuna")
                st.subheader("Lacune esperienza")
                st.write(result["lacune_esperienza"] or "Nessuna")
                st.subheader("Allineamento interessi")
                st.write(result["allineamento_interessi"] or "Nessuno")
                st.subheader("Report narrativo")
                st.write(result["prompt_finale"])
            else:
                st.error(f"Errore {response.status_code}: {response.json().get('detail')}")

            with st.expander("Log / risposta completa"):
                st.json(response.json() if response.content else {"status_code": response.status_code})
