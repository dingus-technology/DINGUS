"""bug_card.py

This module contains the bug card for the frontend.
"""

import json
from typing import Any

import streamlit as st


def render_bug_card(
    file: str,
    line: int,
    summary: str,
    evidence: Any,
    human_explanation: str,
    raw_response: str,
    bug_found_time: str,
    scan_time: str,
    message: str,
    ai_insights: str | None = None,
    remove_callback=None,
):
    """Render a single bug card with all details in one styled card."""

    evidence_block = ""
    key_log_messages_block = message
    parsed_evidence = evidence
    if evidence:
        try:
            if isinstance(evidence, str):
                parsed_evidence = json.loads(evidence)
            if isinstance(parsed_evidence, list):
                for item in parsed_evidence:
                    evidence_block += f"<code>{item}</code><br>"
            elif isinstance(parsed_evidence, dict):
                for k, v in parsed_evidence.items():
                    evidence_block += f"<code>{k}: {v}</code><br>"
            else:
                evidence_block = f"<code>{str(evidence)}</code>"
        except Exception:
            evidence_block = f"<code>{str(evidence) if evidence else 'No evidence available.'}</code>"
    else:
        evidence_block = "No evidence available."

    # Main card HTML
    card_html = f"""
    <div style="background: linear-gradient(100deg, #232526 70%, #414345 100%); border-radius: 1em; padding: 1.5em 2em; margin-bottom: 1.0em; box-shadow: 0 4px 24px rgba(0,0,0,0.15); border: 1px solid #333;">
        <div style="display: flex; align-items: center; gap: 1em;">
            <span style="font-size: 2em;">🐞</span>
            <span style="font-size: 1.2em; font-weight: bold; color: #FAFAFA;">
                Bug in <code>{file}</code> at line <code>{line}</code>
            </span>
        </div>
        <div style="margin-top: 0.3em; color: #888; font-size: 0.95em;">
            <b>Bug found:</b> {bug_found_time} &nbsp;|&nbsp; <b>Scan time:</b> {scan_time}
        </div>
        <div style="margin-top: 0.7em; color: #FFD700; font-size: 1.1em;">
            <b>Summary:</b> {summary}
        </div>
        <div style="margin-top: 1em; color: #FF6B6B; font-size: 1em; font-weight: bold;">
            <span>🚨 Key Log Message:</span>
        </div>
        <div style="background: #2A1B1B; color: #FFB3B3; border-left: 5px solid #FF6B6B; border-radius: 0.5em; padding: 1em; margin-bottom: 0.7em; font-size: 0.95em; font-family: 'Courier New', monospace; line-height: 1.3; max-height: 200px; overflow-y: auto;">
            {key_log_messages_block[:500] + "..." if len(key_log_messages_block) > 500 else key_log_messages_block}
        </div>
        <div style="margin-top: 1em; margin-bottom: 0.5em; color: #A0A0A0; font-size: 0.95em;">
            <b>How to Fix:</b>
        </div>
        <div style="background: #2D2F31; color: #00FFB3; border-left: 5px solid #00FFB3; border-radius: 0.5em; padding: 1em; margin-bottom: 0.7em; font-size: 1.05em;">
            {human_explanation}
        </div>
        <div style="margin-top: 1.2em; color: #A0A0A0; font-size: 1em; font-weight: bold;">
            <span>📝 Evidence & Logs</span>
        </div>
        <div style="margin-bottom: 0.5em; color: #B0B0B0; font-size: 0.97em;">
            The following log lines or evidence were collected to help you understand the context and cause of this bug. Review them to see what led to the issue.
        </div>
        <details style="margin-bottom: 1em;">
            <summary style="cursor: pointer; color: #7FDBFF; font-size: 1em; font-weight: bold;">Logs Snippet</summary>
            <div style="background: #181A1B; color: #FAFAFA; border-radius: 0.7em; padding: 1em; font-size: 0.97em; margin-top: 1em; overflow-x: auto;">
                {evidence_block}
            </div>
        </details>
        <details style="margin-bottom: 1em;">
            <summary style="cursor: pointer; color: #7FDBFF; font-size: 1em; font-weight: bold;">Show AI Insights</summary>
            <div style="background: #181A1B; color: #FAFAFA; border-radius: 0.7em; padding: 1em; font-size: 0.97em; margin-top: 1em; overflow-x: auto;">
                {ai_insights or "No AI insights available."}
            </div>
        </details>
    </div>
    """  # noqa: E501

    st.markdown(card_html, unsafe_allow_html=True)
