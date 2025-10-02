"""app.py

This file supports the streamlit frontend"""

import os

import requests  # type: ignore
import streamlit as st
from bugs_tab import render_bugs_tab
from settings import API_URL


def render_investigation_js():
    """Render JavaScript for investigation functionality."""
    st.markdown(
        """
    <script>
    function startInvestigation(file, line, summary) {
        // This function will be called by the investigation button
        // The actual functionality is handled by Streamlit buttons
        console.log('Investigation requested for:', file, line, summary);
    }
    </script>
    """,
        unsafe_allow_html=True,
    )


def render_sidebar_config():
    st.sidebar.header("Connection & Scheduler Settings")
    if "loki_status" not in st.session_state:
        st.session_state["loki_status"] = None
    if "k8s_status" not in st.session_state:
        st.session_state["k8s_status"] = None
    # Prefill from backend runtime config if available
    try:
        cfg_resp = requests.get(f"{API_URL}/config", timeout=5)
        cfg_json = cfg_resp.json() if cfg_resp.ok else {"config": {}}
        backend_cfg = cfg_json.get("config", {})
    except Exception:
        backend_cfg = {}

    with st.sidebar.form("config_form"):
        loki_base_url = st.text_input(
            "Loki URL",
            value=st.session_state.get(
                "loki_url_input",
                backend_cfg.get("loki_base_url", os.getenv("LOKI_URL", "http://host.docker.internal:3100")),
            ),
            key="loki_url_input",
        )
        job_name = st.text_input(
            "Loki Job Name",
            value=st.session_state.get(
                "loki_job_input", backend_cfg.get("job_name", os.getenv("LOKI_JOB_NAME", "cpu_monitor"))
            ),
            key="loki_job_input",
        )
        kube_config_path = st.text_input(
            "K8s Config Path",
            value=st.session_state.get(
                "kube_config_input", backend_cfg.get("kube_config_path", os.getenv("KUBE_CONFIG_PATH", "/.kube/config"))
            ),
            key="kube_config_input",
        )
        open_ai_api_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.get(
                "openai_api_key_input",
                "" if not backend_cfg.get("open_ai_api_key") else "********",
            ),
            type="password",
            key="openai_api_key_input",
        )
        submitted = st.form_submit_button("Update")
        if submitted:
            handle_sidebar_submit(loki_base_url, job_name, kube_config_path, open_ai_api_key)


def handle_sidebar_submit(loki_base_url, job_name, kube_config_path, open_ai_api_key):
    loki_ok = False
    k8s_ok = False
    openai_ok = False
    try:
        resp = requests.get(
            f"{API_URL}/check_loki",
            params={"loki_url": loki_base_url, "loki_job_name": job_name},
        )
        if resp.ok:
            st.session_state["loki_status"] = "success"
            st.success("Loki connection successful!")
            loki_ok = True
        else:
            st.session_state["loki_status"] = "fail"
            st.warning(f"Loki connection failed: {resp.json().get('reason', 'Unknown error')}")
    except Exception as e:
        st.session_state["loki_status"] = "fail"
        st.warning(f"Loki connection failed: {e}")
    try:
        resp = requests.get(
            f"{API_URL}/check_k8s",
            params={"kube_config_path": kube_config_path},
        )
        if resp.ok:
            st.session_state["k8s_status"] = "success"
            st.success("K8s connection successful!")
            k8s_ok = True
        else:
            st.session_state["k8s_status"] = "fail"
            st.warning(f"K8s connection failed: {resp.json().get('reason', 'Unknown error')}")
            k8s_ok = True
    except Exception as e:
        st.session_state["k8s_status"] = "fail"
        st.warning(f"K8s connection failed: {e}")
    try:
        resp = requests.post(
            f"{API_URL}/check_openai",
            json={"openai_api_key": open_ai_api_key},
        )
        if resp.ok:
            st.session_state["openai_status"] = "success"
            st.success("OpenAI connection successful!")
            openai_ok = True
        else:
            st.session_state["openai_status"] = "fail"
            st.warning(f"OpenAI connection failed: {resp.json().get('reason', 'Unknown error')}")
    except Exception as e:
        st.session_state["openai_status"] = "fail"
        st.warning(f"OpenAI connection failed: {e}")
    if loki_ok and k8s_ok and openai_ok:
        resp = requests.post(
            f"{API_URL}/update_config",
            json={
                "loki_base_url": loki_base_url,
                "job_name": job_name,
                "kube_config_path": kube_config_path,
                "open_ai_api_key": open_ai_api_key,
            },
        )
        if resp.ok:
            st.sidebar.success("Config updated.")
        else:
            st.sidebar.error("Failed to update config.")
    else:
        st.sidebar.error("Please fix the validation errors above before submitting.")


def main():
    st.set_page_config(page_title="Dingus", page_icon="/assets/logo-light.png")
    st.title("Dingus Report Dashboard")

    # Add JavaScript for investigation functionality
    render_investigation_js()

    render_sidebar_config()
    tabs = st.tabs(["Latest Bugs"])
    with tabs[0]:
        render_bugs_tab()


if __name__ == "__main__":
    main()
