"""investigation_card.py

This module contains the investigation card for the frontend.
"""

from typing import Any

import streamlit as st


def render_investigation_card(investigation_results: dict[str, Any]):
    if not investigation_results:
        return

    # Extract investigation data
    investigation_id = investigation_results.get("investigation_id", "Unknown")
    start_time = investigation_results.get("start_time", "Unknown")
    end_time = investigation_results.get("end_time", "Unknown")
    status = investigation_results.get("status", "Unknown")

    # Extract analysis data
    analysis = investigation_results.get("analysis", {})
    severity = analysis.get("severity", {})
    severity_level = severity.get("level", "Medium")
    severity_confidence = severity.get("confidence", "low")
    severity_reasoning = severity.get("reasoning", "No reasoning provided")

    root_cause = analysis.get("root_cause", "Not determined")
    confidence_level = analysis.get("confidence_level", "low")
    recommended_fixes = analysis.get("recommended_fixes", [])
    correlations = analysis.get("correlations", [])
    prevention_measures = analysis.get("prevention_measures", [])

    # Extract investigation steps
    investigation_data = investigation_results.get("investigation_results", {})
    steps = investigation_data.get("steps", [])

    # Determine severity color
    severity_colors = {"Critical": "#FF4444", "High": "#FF8800", "Medium": "#FFD700", "Low": "#00FF88"}
    severity_color = severity_colors.get(severity_level, "#FFD700")

    # Determine confidence color
    confidence_color = (
        "#00FFB3" if confidence_level == "high" else "#FFD700" if confidence_level == "medium" else "#FF6B6B"
    )

    # Header with severity assessment (minimal HTML)
    st.markdown(
        f"""
        <div style="background: linear-gradient(100deg, #1A1B1C 70%, #2A2B2C 100%); border-radius: 0.8em; padding: 1.2em 1.5em; margin: 0.5em 0 1.5em 2em; box-shadow: 0 2px 12px rgba(0,0,0,0.1); border: 1px solid #444; border-left: 4px solid {severity_color};">
            <div style="display: flex; align-items: center; gap: 0.5em; margin-bottom: 1em;">
                <span style="font-size: 1.2em;">🔍</span>
                <span style="color: #7FDBFF; font-size: 1.1em; font-weight: bold;">Investigation Results</span>
                <span style="margin-left: auto; font-size: 0.9em; color: #888;">ID: {investigation_id}</span>
            </div>
            <div style="background: rgba(255,255,255,0.05); border-radius: 0.5em; padding: 1em; margin-bottom: 1em;">
                <div style="display: flex; align-items: center; gap: 0.5em; margin-bottom: 0.5em;">
                    <span style="font-size: 1.1em;">🚨</span>
                    <span style="color: {severity_color}; font-size: 1.2em; font-weight: bold;">{severity_level} SEVERITY</span>
                    <span style="color: {confidence_color}; font-size: 0.9em; margin-left: auto;">({severity_confidence.upper()} CONFIDENCE)</span>
                </div>
                <div style="color: #B0B0B0; font-size: 0.9em; font-style: italic;">{severity_reasoning}</div>
            </div>
            <div style="color: #B0B0B0; font-size: 0.95em; margin-bottom: 1em;">
                <div style="margin-bottom: 0.5em;"><strong>Investigation Status:</strong> <span style="color: {'#00FFB3' if status == 'completed' else '#FFD700'}">{status.upper()}</span></div>
                <div style="margin-bottom: 0.5em;"><strong>Started:</strong> {start_time} | <strong>Completed:</strong> {end_time}</div>
            </div>
        </div>
        """,  # noqa: E501
        unsafe_allow_html=True,
    )

    with st.expander("📊 Investigation Analysis", expanded=False):
        st.markdown("### 🧩 Investigation Steps")
        if investigation_results.get("investigation_strategy"):
            st.markdown("**📋 Investigation Strategy:**")
            st.markdown(f"*{investigation_results.get('investigation_strategy', 'Systematic debugging approach')}*")
            st.markdown("---")

        for i, step in enumerate(steps, 1):
            step_name = step.get("name", "Unknown")
            step_result = step.get("result", {})
            step_description = step.get("description", "")
            step_explanation = step.get("explanation", "")
            status = "NO DATA"
            status_icon = "❓"
            status_color = "#FFD700"
            if step.get("success"):
                status = "SUCCESS"
                status_icon = "✅"
                status_color = "#00FFB3"
            elif step_result.get("status") == "failed":
                status = "FAILED"
                status_icon = "❌"
                status_color = "#FF6B6B"

            cols = st.columns([0.1, 0.7, 0.2])
            with cols[0]:
                st.markdown(
                    f"<div style='background:{status_color};color:#000;border-radius:50%;width:2em;height:2em;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:1.1em'>{i}</div>",  # noqa: E501
                    unsafe_allow_html=True,
                )
            with cols[1]:
                st.markdown(f"**{step_name}**")
                if step_explanation:
                    st.markdown(
                        f"<span style='color:#888;font-size:0.95em'><i>{step_explanation}</i></span>",
                        unsafe_allow_html=True,
                    )
                if step_description:
                    st.markdown(
                        f"<span style='color:#aaa;font-size:0.92em'>{step_description}</span>", unsafe_allow_html=True
                    )
            with cols[2]:
                st.markdown(
                    f"<span style='color:{status_color};font-weight:bold;font-size:1.1em'>{status_icon} {status}</span>",  # noqa: E501
                    unsafe_allow_html=True,
                )

            # Results (use st.code, st.json, st.write, etc.)
            if step_name == "Code Context Analysis" and step_result.get("code_snippet"):
                st.code("".join(step_result["code_snippet"]), language="python")
            elif step_name == "Kubernetes Pod Logs" and step_result.get("logs"):
                st.code("\n".join(step_result["logs"][-20:]), language="text")
            elif step_name == "System Resources Check" and step_result.get("status") == "success":
                st.write(
                    {
                        "CPU Usage (%)": step_result.get("cpu_percent"),
                        "Memory Usage (%)": step_result.get("memory_percent"),
                        "Available Memory (GB)": step_result.get("memory_available_gb"),
                        "Disk Usage (%)": step_result.get("disk_percent"),
                        "Free Disk (GB)": step_result.get("disk_free_gb"),
                    }
                )
            elif step_result:
                st.json(step_result, expanded=False)
            st.markdown("---")

        # Show expected correlations if available
        if investigation_results.get("expected_correlations"):
            st.markdown("**🔗 Expected Correlations:**")
            st.markdown(f"*{investigation_results.get('expected_correlations')}*")

        # Root Cause Analysis and other summary info
        st.markdown("### 🎯 Root Cause Analysis")
        st.markdown(f"```\n{root_cause}\n```")
        st.markdown(
            f"**📊 Analysis Confidence:** <span style='color:{confidence_color}'>{confidence_level.upper()}</span>",
            unsafe_allow_html=True,
        )
        st.markdown("**🔧 Recommended Fixes**")
        if recommended_fixes:
            for fix in recommended_fixes:
                st.markdown(f"- {fix}")
        else:
            st.markdown("*No specific fixes recommended.*")
        if correlations:
            st.markdown("**🔗 Correlations Found**")
            for correlation in correlations:
                st.markdown(f"- {correlation}")
        if prevention_measures:
            st.markdown("**🛡️ Prevention Measures**")
            for measure in prevention_measures:
                st.markdown(f"- {measure}")
