import streamlit as st
import json

from corep_assistant.rag_pipeline import run_query
from corep_assistant.validator import validate

st.title("COREP Reporting Assistant — Prototype")

scenario = st.text_area("Enter reporting scenario")

if st.button("Generate COREP Mapping"):

    output, docs = run_query(scenario)

    data = json.loads(output)

    flags = validate(data["fields"])
    data["validation_flags"] = flags

    st.subheader("Structured Output")
    st.json(data)

    st.subheader("Template Extract")

    for f in data["fields"]:
        st.write(
            f"{f['field_code']} — {f['description']} — {f['value']}"
        )

    st.subheader("Audit Log")

    for d in docs:
        st.write(d.metadata)
