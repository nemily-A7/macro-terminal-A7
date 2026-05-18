import streamlit as st
import pandas as pd

def shorten_value(value: float, unit: str = "") -> str:
    """Formats a number with K/M/B suffixes."""
    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)

    suffix = ""
    if abs(val) >= 1e9:
        val /= 1e9
        suffix = "B"
    elif abs(val) >= 1e6:
        val /= 1e6
        suffix = "M"
    elif abs(val) >= 1e3:
        val /= 1e3
        suffix = "K"
    
    # Decimals: if small, 2 decimals. If large, 1 or 0?
    formatted = f"{val:,.2f}{suffix}"
    return formatted

def format_kpi_value(value: float | str | None, unit: str = "") -> tuple[str, str]:
    if value is None:
        return "N/A", ""
    if isinstance(value, (int, float)):
        return shorten_value(value), unit
    return str(value), unit


def render_kpi(label: str, value: float | str | None, unit: str = "", delta: float | None = None, col=None):
    if col is None:
        col = st

    display_val, display_unit = format_kpi_value(value, unit)

    # Custom HTML Card
    # Using simple CSS for 'value', 'label', 'unit'
    html = f"""
    <div style="
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #e0e0e0;
    ">
        <div style="font-size: 14px; color: #666; margin-bottom: 5px;">{label}</div>
        <div style="font-size: 24px; font-weight: bold; color: #333;">
            {display_val}
        </div>
        <div style="font-size: 12px; color: #888; margin-top: 2px;">{display_unit}</div>
    </div>
    """
    
    # Dark mode support logic could be added but sticking to simple structure
    # Streamlit theme independence is tricky with hardcoded colors.
    # Using st.metric for now as base but if truncation is issue, use markdown.
    
    # User complained about truncation. Markdown is safer for long units.
    # BUT hardcoded light colors might break dark mode.
    # Let's use transparent background or system colors.
    
    html_theme_neutral = f"""
    <div style="
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 10px;
        display: flex;
        flex-direction: column;
    ">
        <span style="font-size: 0.9em; opacity: 0.8;">{label}</span>
        <span style="font-size: 1.8em; font-weight: 600;">{display_val}</span>
        <span style="font-size: 0.8em; opacity: 0.6; white-space: normal; line-height: 1.1;">{display_unit}</span>
    </div>
    """
    
    col.markdown(html_theme_neutral, unsafe_allow_html=True)

def placeholder_chart(title: str):
    st.markdown(f"#### {title}")
    st.caption("Chart data unavailable")
