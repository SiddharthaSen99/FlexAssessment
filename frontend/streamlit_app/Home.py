import os
import streamlit as st
import requests


st.set_page_config(page_title="Flex Living Reviews", layout="wide")

st.title("Flex Living Reviews Dashboard")
st.caption("Manager tools to assess property performance and curate public reviews.")

api_base = os.getenv("API_BASE_URL", "http://localhost:8000")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Backend health")
    try:
        resp = requests.get(f"{api_base}/health", timeout=10)
        ok = resp.status_code == 200 and resp.json().get("status") == "ok"
        st.success("API is running" if ok else "API returned unexpected response")
    except Exception as e:
        st.error(f"Cannot reach API at {api_base}: {e}")

with col2:
    st.subheader("Quick start")
    st.markdown(
        "- Use the sidebar to navigate to the Manager Dashboard to filter and approve reviews.\n"
        "- Go to the Review Display page to preview the public reviews section."
    )
