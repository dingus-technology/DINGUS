"""bugs_tab.py

This module contains the bugs tab for the frontend.
"""

import requests  # type: ignore
import streamlit as st
from bug_card import render_bug_card
from settings import API_URL


def fetch_bugs():
    try:
        bug_list_resp = requests.get(f"{API_URL}/bugs")
        if bug_list_resp.ok:
            return bug_list_resp.json().get("bugs", [])
        else:
            st.error("Failed to fetch bug list.")
            return []
    except Exception as e:
        err_msg = str(e)
        if "Failed to establish a new connection" in err_msg or "Max retries exceeded" in err_msg:
            st.info(
                "Backend API is not reachable. Please set Loki URL, Job Name, K8s Config Path, and OpenAI API Key in the sidebar, then click Update."
            )
        else:
            st.error(f"Failed to fetch bug list: {e}")
        return []


def fetch_investigations():
    try:
        investigation_list_resp = requests.get(f"{API_URL}/investigations")
        if investigation_list_resp.ok:
            return investigation_list_resp.json().get("investigations", [])
        else:
            return []
    except Exception as e:
        err_msg = str(e)
        if "Failed to establish a new connection" in err_msg or "Max retries exceeded" in err_msg:
            st.info(
                "Backend API is not reachable. Configure connection details in the sidebar and click Update."
            )
        else:
            st.error(f"Failed to fetch investigations: {e}")
        return []


def start_investigation(bug_info, bug_filename=None):
    """Start an investigation for a bug."""
    try:
        payload = {"bug_info": bug_info}
        if bug_filename:
            payload["bug_filename"] = bug_filename

        resp = requests.post(f"{API_URL}/investigation/start", json=payload)
        if resp.ok:
            result = resp.json()
            st.success(f"Investigation started! ID: {result.get('investigation_id')}")
            return result.get("result")
        else:
            st.error(f"Failed to start investigation: {resp.json().get('reason', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Failed to start investigation: {e}")
        return None


def trigger_scan():
    payload = {
        "loki_base_url": st.session_state.get("loki_url_input"),
        "job_name": st.session_state.get("loki_job_input"),
        "kube_config_path": st.session_state.get("kube_config_input"),
        "open_ai_api_key": st.session_state.get("openai_api_key_input"),
    }
    try:
        resp = requests.post(f"{API_URL}/scan", json=payload)
        if resp.ok:
            st.success("Scan complete!")
            st.session_state["bugs_loading"] = True
            st.session_state["bugs_cache"] = None
        else:
            st.error(f"Scan failed: {resp.json().get('reason', 'Unknown error')}")
    except Exception as e:
        st.error(f"Scan failed: {e}")


def render_scan_refresh_row():
    if st.button("🔍 Scan", key="scan_btn"):
        with st.spinner("Running Scan..."):
            trigger_scan()


def render_bugs_tab():
    st.header("🐞 Bugs")
    st.caption("This list updates automatically when new bugs are detected.")

    if st.button("🔍 Scan Now", key="scan_btn"):
        with st.spinner("Running Scan..."):
            trigger_scan()

    if "bugs_loading" not in st.session_state:
        st.session_state["bugs_loading"] = False
    if "bugs_cache" not in st.session_state:
        st.session_state["bugs_cache"] = None
    if "investigations_cache" not in st.session_state:
        st.session_state["investigations_cache"] = None

    if st.session_state["bugs_loading"] or st.session_state["bugs_cache"] is None:
        with st.spinner("Loading bugs..."):
            st.session_state["bugs_cache"] = fetch_bugs()
            st.session_state["bugs_loading"] = False

    # Fetch investigations
    if st.session_state["investigations_cache"] is None:
        st.session_state["investigations_cache"] = fetch_investigations()

    bugs = st.session_state.get("bugs_cache", [])
    investigations = st.session_state.get("investigations_cache", [])

    if bugs is None:
        pass
    elif not bugs:
        st.info("Living bug free!")
    else:
        for bug_entry in bugs:
            fname = bug_entry.get("filename", "?")
            bug = bug_entry.get("bug", {})

            # Find matching investigation for this bug
            # investigation_results = None
            for inv_entry in investigations:
                inv = inv_entry.get("investigation", {})
                inv_bug_info = inv.get("bug_info", {})

                # Match by file, line, and summary for better accuracy
                if (
                    inv_bug_info.get("file") == bug.get("file")
                    and inv_bug_info.get("line") == bug.get("line")
                    and inv_bug_info.get("summary") == bug.get("summary")
                ):
                    # investigation_results = inv
                    break

                # Fallback: match by investigation ID if it's stored in the bug
                elif bug.get("investigation_id") and inv.get("investigation_id") == bug.get("investigation_id"):
                    # investigation_results = inv
                    break

            def remove_callback(fname=fname):
                try:
                    resp = requests.delete(f"{API_URL}/bug/{fname}")
                    if resp.ok:
                        st.success(f"Removed bug {fname}")
                        st.session_state["bugs_loading"] = True
                        st.session_state["bugs_cache"] = None
                    else:
                        st.error(f"Failed to remove bug: {resp.json().get('reason', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to remove bug: {e}")

            # Render the bug card
            render_bug_card(
                file=bug.get("file", "?"),
                line=bug.get("line", "?"),
                summary=bug.get("summary", bug.get("raw_response", "?")),
                evidence=bug.get("evidence", []),
                human_explanation=bug.get("human_explanation", "No explanation provided."),
                raw_response=bug.get("raw_response", ""),
                bug_found_time=bug.get("bug_found_time", "?"),
                scan_time=bug.get("scan_time", "?"),
                ai_insights=bug.get("ai_insights", None),
                message=bug.get("message", ""),
                remove_callback=remove_callback,
            )

            # TODO: Re-enable investigation card

            # # Render investigation card if investigation results exist
            # if investigation_results:
            #     render_investigation_card(investigation_results)
            # else:
            #     # Show a small indicator that no investigation has been run yet
            #     st.markdown(
            #         '<div style="margin: 0.5em 0 1.5em 2em; color: #888; font-size: 0.9em; font-style: italic;">'
            #         '💡 No investigation results yet. Click "Start Investigation" below to run a deep analysis.'
            #         "</div>",
            #         unsafe_allow_html=True,
            #     )

            # # Add investigation button below the card
            # col1, col2 = st.columns([1, 3])
            # with col1:
            #     # Disable button if investigation is already running
            #     button_disabled = st.session_state.get(f"investigation_loading_{fname}", False)

            #     if st.button("🔍 Start Investigation", key=f"investigation_btn_{fname}", disabled=button_disabled):
            #         # Set loading state
            #         st.session_state[f"investigation_loading_{fname}"] = True
            #         st.rerun()

            # Show loading spinner if investigation is in progress
            # if st.session_state.get(f"investigation_loading_{fname}", False):
            #     with st.spinner("🔍 Running investigation..."):
            #         try:
            #             investigation_result = start_investigation(bug, fname)
            #             if investigation_result:
            #                 st.session_state["investigations_cache"] = None  # Refresh cache
            #                 st.session_state[f"investigation_loading_{fname}"] = False
            #                 st.success("✅ Investigation completed!")
            #                 st.rerun()
            #             else:
            #                 st.session_state[f"investigation_loading_{fname}"] = False
            #                 st.error("❌ Investigation failed!")
            #                 st.rerun()
            #         except Exception as e:
            #             st.session_state[f"investigation_loading_{fname}"] = False
            #             st.error(f"❌ Investigation error: {e}")
            #             st.rerun()
            # st.divider()
