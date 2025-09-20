"""dashboard_tab.py

This module contains the dashboard tab for the frontend.
"""

import requests  # type: ignore
import streamlit as st
from settings import API_URL


def fetch_reports():
    try:
        report_list_resp = requests.get(f"{API_URL}/list_reports")
        if report_list_resp.ok:
            return report_list_resp.json().get("reports", [])
        else:
            st.error("Failed to fetch report list.")
            return []
    except Exception as e:
        st.error(f"Failed to fetch report list: {e}")
        return []


def generate_report():
    resp = requests.post(
        f"{API_URL}/generate_report",
        json={
            "loki_base_url": st.session_state.get("loki_url_input", st.session_state.get("loki_url")),
            "job_name": st.session_state.get("loki_job_input"),
            "kube_config_path": st.session_state.get("kube_config_input", st.session_state.get("kube_config_path")),
            "open_ai_api_key": st.session_state.get("openai_api_key_input"),
        },
    )
    if resp.ok:
        st.sidebar.success("Report generated!")
    else:
        st.sidebar.error(f"Failed to generate report: {resp.json().get('reason')}")


def render_generate_refresh_row():
    if st.button("🔄 Refresh", key="refresh_reports_btn"):
        st.session_state["reports_loading"] = True
        st.session_state["reports_cache"] = None
    if st.button("Generate Report Now"):
        generate_report()


def render_dashboard_tab():
    st.header("🔍 Reports")
    st.caption("List of reports for infrastructure and application health.")
    render_generate_refresh_row()

    if "reports_loading" not in st.session_state:
        st.session_state["reports_loading"] = False
    if "reports_cache" not in st.session_state:
        st.session_state["reports_cache"] = None

    if st.session_state["reports_loading"] or st.session_state["reports_cache"] is None:
        with st.spinner("Loading reports..."):
            st.session_state["reports_cache"] = fetch_reports()
            st.session_state["reports_loading"] = False

    reports = st.session_state.get("reports_cache", [])
    if reports is None:
        pass  # error already shown
    elif not reports:
        st.info("No reports found yet.")
    else:
        for report_file in reports:
            with st.expander(report_file):
                report_resp = requests.get(f"{API_URL}/get_report/{report_file}")
                if report_resp.ok:
                    st.markdown(report_resp.json()["content"])
                else:
                    st.error("Failed to load report.")
