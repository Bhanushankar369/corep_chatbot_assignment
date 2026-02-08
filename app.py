import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/query"

st.title("COREP Reporting Assistant — Prototype")

scenario = st.text_area("Enter reporting scenario")

if st.button("Generate COREP Mapping"):
    if not scenario.strip():
        st.warning("Please enter a scenario")
        st.stop()

    with st.spinner("Querying regulatory assistant..."):
        response = requests.post(
            API_URL,
            json={"scenario": scenario},
            timeout=60
        )

    if response.status_code != 200:
        st.error(response.text)
        st.stop()

    data = response.json()

    st.subheader("Structured Output")
    st.json(data["llm_output"])

    st.subheader("Validation Flags")
    st.write(data["validation_flags"])

    st.subheader("Template Extract")
    for f in data["llm_output"].get("fields", []):
        st.write(
            f"{f['field_code']} — {f['description']} — {f['value']}"
        )

    st.subheader("Audit Log")
    for m in data["audit_log"]:
        st.write(m)
