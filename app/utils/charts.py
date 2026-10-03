"""Reusable Plotly Chart Components for E-Commerce BI Dashboard.

Follows corporate design identity from PROJECT_CONTEXT.md:
- Primary Navy: #0B2545
- Secondary Blue: #13315C
- Accent Teal: #1B998B
- Highlight Amber: #F4A261
- Alert Red: #E63946
- Clean card-friendly layouts with Inter typography
"""

from __future__ import annotations

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def is_dark_mode() -> bool:
    """Checks whether Dark Mode is active in the current Streamlit session. Defaults strictly to Light Mode."""
    try:
        if hasattr(st, "session_state"):
            if "theme_mode" not in st.session_state:
                st.session_state["theme_mode"] = "light"
            return st.session_state["theme_mode"] == "dark"
    except Exception:
        pass
    return False


THEME_LIGHT: Dict[str, str] = {
    "navy": "#0B2545",
    "blue": "#13315C",
    "teal": "#1B998B",
    "amber": "#F4A261",
    "red": "#E63946",
    "green": "#10B981",
    "bg": "#F5F7FA",
    "card": "#FFFFFF",
    "text": "#0B2545",
    "text_secondary": "#64748B",
    "muted": "#64748B",
    "grid": "#E2E8F0",
    "border": "#E2E8F0",
}

THEME_DARK: Dict[str, str] = {
    "navy": "#60A5FA",   # Sky blue accent replacing dark navy on dark canvas
    "blue": "#38BDF8",   # Vibrant cyan blue
    "teal": "#2DD4BF",   # Luminous mint teal
    "amber": "#FBBF24",  # Warm golden amber
    "red": "#F87171",    # Soft coral red
    "green": "#34D399",  # Fresh emerald green
    "bg": "#0F172A",     # Slate 900 canvas
    "card": "#1E293B",   # Slate 800 card container
    "text": "#F8FAFC",   # Slate 50 crisp high contrast text
    "text_secondary": "#94A3B8",  # Slate 400 secondary text
    "muted": "#94A3B8",  # Slate 400 muted labels
    "grid": "#334155",   # Slate 700 subtle gridlines
    "border": "#334155", # Slate 700 container borders
}


class DynamicTheme(dict):
    """Dictionary proxy that resolves color keys dynamically according to the active theme."""

    def __init__(self, light_dict: Dict[str, str], dark_dict: Dict[str, str]) -> None:
        super().__init__(light_dict)
        self._light = dict(light_dict)
        self._dark = dict(dark_dict)

    def _get_active(self) -> Dict[str, str]:
        return self._dark if is_dark_mode() else self._light

    def __getitem__(self, key: str) -> str:
        active = self._get_active()
        return active.get(key, self._light.get(key, "#000000"))

    def get(self, key: str, default: Any = None) -> Any:
        active = self._get_active()
        return active.get(key, default)

    def keys(self):
        return self._get_active().keys()

    def values(self):
        return self._get_active().values()

    def items(self):
        return self._get_active().items()

    def __iter__(self):
        return iter(self._get_active())

    def __len__(self):
        return len(self._get_active())

    def copy(self) -> Dict[str, str]:
        return dict(self._get_active())


THEME = DynamicTheme(THEME_LIGHT, THEME_DARK)

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def get_theme_css() -> str:
    """Generates corporate responsive CSS rules adhering to current light/dark theme."""
    dark = is_dark_mode()
    if dark:
        return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Dark Mode App Canvas */
    .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }

    /* Dark Mode Top Header */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background-color: #0F172A !important;
        border-bottom: 1px solid #334155 !important;
    }
    header[data-testid="stHeader"] * {
        color: #F8FAFC !important;
    }

    /* Dark Mode Sidebar Canvas */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155 !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #E2E8F0 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #F8FAFC !important;
    }

    /* =========================================================================
       SIDEBAR NAVIGATION BAR - 100% VISIBILITY IN DARK MODE
       ========================================================================= */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebar"] nav {
        background-color: transparent !important;
        padding-top: 10px !important;
        margin-bottom: 12px !important;
    }
    [data-testid="stSidebarNav"] *,
    [data-testid="stSidebarNavItems"] *,
    [data-testid="stSidebar"] nav * {
        color: #CBD5E1 !important;
        -webkit-text-fill-color: #CBD5E1 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stSidebarNav"] ul,
    [data-testid="stSidebarNavItems"] ul {
        list-style: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stSidebarNav"] li,
    [data-testid="stSidebarNavItems"] li {
        margin-bottom: 3px !important;
    }
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNav"] a:visited,
    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"],
    [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"] span,
    [data-testid="stSidebarNavItems"] a,
    [data-testid="stSidebarNavItems"] a span,
    [data-testid="stSidebar"] nav a,
    [data-testid="stSidebar"] nav a span {
        color: #E2E8F0 !important;
        -webkit-text-fill-color: #E2E8F0 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        text-decoration: none !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNavItems"] a,
    [data-testid="stSidebar"] nav a {
        background-color: #1E293B !important;
        border-radius: 8px !important;
        margin: 2px 0 !important;
        padding: 8px 12px !important;
        display: flex !important;
        align-items: center !important;
        transition: background-color 0.15s ease, color 0.15s ease !important;
    }
    [data-testid="stSidebarNav"] a:hover,
    [data-testid="stSidebarNavItems"] a:hover,
    [data-testid="stSidebar"] nav a:hover {
        background-color: #334155 !important;
    }
    [data-testid="stSidebarNav"] a:hover span,
    [data-testid="stSidebarNav"] a:hover *,
    [data-testid="stSidebarNavItems"] a:hover span,
    [data-testid="stSidebarNavItems"] a:hover *,
    [data-testid="stSidebar"] nav a:hover * {
        color: #2DD4BF !important;
        -webkit-text-fill-color: #2DD4BF !important;
    }
    /* Active / Selected Page in Dark Mode */
    [data-testid="stSidebarNav"] a[aria-current="page"],
    [data-testid="stSidebarNav"] a[data-testid="stSidebarNavLink"][aria-current="page"],
    [data-testid="stSidebarNav"] li[aria-selected="true"] a,
    [data-testid="stSidebarNavItems"] a[aria-current="page"],
    [data-testid="stSidebar"] nav a[aria-current="page"] {
        background-color: #334155 !important;
        border-radius: 8px !important;
        border-left: 4px solid #2DD4BF !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] span,
    [data-testid="stSidebarNav"] a[aria-current="page"] *,
    [data-testid="stSidebarNav"] a[data-testid="stSidebarNavLink"][aria-current="page"] span,
    [data-testid="stSidebarNav"] li[aria-selected="true"] a span,
    [data-testid="stSidebarNavItems"] a[aria-current="page"] *,
    [data-testid="stSidebar"] nav a[aria-current="page"] * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 800 !important;
    }
    [data-testid="stSidebarNav"] svg,
    [data-testid="stSidebarNavItems"] svg,
    [data-testid="stSidebar"] nav svg {
        fill: #2DD4BF !important;
        color: #2DD4BF !important;
    }

    /* =========================================================================
       SIDEBAR & CANVAS FORM INPUTS - DARK MODE (DATE, MULTISELECT, SELECTBOX, BUTTONS)
       ========================================================================= */
    /* Container backgrounds and inputs */
    [data-testid="stSidebar"] div[data-baseweb="input"],
    [data-testid="stSidebar"] div[data-baseweb="base-input"],
    [data-testid="stSidebar"] div[data-baseweb="select"],
    [data-testid="stSidebar"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-testid="stDateInput"] > div,
    [data-testid="stSidebar"] [data-testid="stDateInput"] div,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] > div,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] div,
    [data-testid="stSidebar"] input,
    div[data-testid="stDateInput"] div[data-baseweb="input"],
    div[data-testid="stDateInput"] div[data-baseweb="base-input"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"],
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"] {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
        border-color: #334155 !important;
    }
    [data-testid="stSidebar"] input::placeholder,
    input::placeholder,
    [data-testid="stSidebar"] div[data-baseweb="select"] div,
    div[data-baseweb="select"] div {
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
    }
    [data-testid="stSidebar"] svg,
    div[data-baseweb="select"] svg {
        fill: #94A3B8 !important;
        color: #94A3B8 !important;
    }
    /* Multiselect tags */
    [data-testid="stSidebar"] span[data-baseweb="tag"],
    span[data-baseweb="tag"] {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border: 1px solid #475569 !important;
        border-radius: 6px !important;
    }
    [data-testid="stSidebar"] span[data-baseweb="tag"] span,
    span[data-baseweb="tag"] span,
    span[data-baseweb="tag"] * {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }
    /* Dropdown menu popovers and calendars mounted to body */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"],
    li[data-baseweb="menu-item"],
    li[data-baseweb="menu-item"] * {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }
    li[data-baseweb="menu-item"]:hover,
    li[data-baseweb="menu-item"]:hover * {
        background-color: #334155 !important;
        color: #2DD4BF !important;
        -webkit-text-fill-color: #2DD4BF !important;
    }
    /* Calendar popover */
    div[data-baseweb="calendar"],
    div[data-baseweb="calendar"] * {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
    }
    div[data-baseweb="calendar"] button:hover {
        background-color: #334155 !important;
    }
    div[data-baseweb="calendar"] [aria-selected="true"] {
        background-color: #2DD4BF !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }
    /* Reset button and secondary buttons */
    [data-testid="stSidebar"] button[kind="secondary"],
    [data-testid="stSidebar"] [data-testid="baseButton-secondary"],
    button[kind="secondary"] {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover,
    [data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover {
        background-color: #334155 !important;
        border-color: #2DD4BF !important;
        color: #2DD4BF !important;
    }

    /* Page & Executive Header Banner */
    .page-header, .exec-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 22px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4) !important;
    }
    .page-header *, .exec-header * {
        color: #FFFFFF !important;
    }
    .page-header h1, .exec-header h1, .page-header-title, .exec-header-title {
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 4px 0;
    }
    .page-header p, .exec-header p, .page-header-subtitle, .exec-header-subtitle {
        color: #CBD5E1 !important;
        font-size: 0.88rem;
        font-weight: 400;
        margin: 0;
    }

    /* Container Card Styling */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #1E293B !important;
        border-radius: 12px;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
        padding: 16px;
    }
    .card-title, .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #F8FAFC !important;
        margin: 0 0 12px 0;
    }

    /* KPI Card Dark Mode Styling */
    .kpi-card {
        background-color: #1E293B !important;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
        border-top: 4px solid #2DD4BF !important;
        border-left: 1px solid #334155 !important;
        border-right: 1px solid #334155 !important;
        border-bottom: 1px solid #334155 !important;
        min-height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8 !important;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #F8FAFC !important;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }
    .kpi-delta-pos {
        font-size: 0.78rem;
        font-weight: 600;
        color: #34D399 !important;
        margin-top: 6px;
    }
    .kpi-delta-neg {
        font-size: 0.78rem;
        font-weight: 600;
        color: #F87171 !important;
        margin-top: 6px;
    }
    .kpi-delta-neutral {
        font-size: 0.78rem;
        font-weight: 500;
        color: #94A3B8 !important;
        margin-top: 6px;
    }

    /* Headings & Text */
    h1, h2, h3, h4, h5, h6 {
        color: #F8FAFC !important;
    }
    p, .stMarkdown p {
        color: #CBD5E1;
    }

    /* Streamlit Metric Dark Styling */
    [data-testid="stMetric"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-weight: 800 !important;
    }

    /* Table & Dataframe styling */
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px;
    }

    /* Top-Right Small Theme Toggle Icon Button — Dark Mode */
    div:has(> #theme-toggle-anchor),
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) {
        display: none !important;
    }
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) + div[data-testid="stElementContainer"] {
        position: absolute !important;
        top: 0 !important;
        right: 0 !important;
        width: 0 !important;
        height: 0 !important;
        overflow: visible !important;
        z-index: 9999999 !important;
    }
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) + div[data-testid="stElementContainer"] button,
    div[data-testid="stVerticalBlock"]:has(#theme-toggle-anchor) button {
        position: fixed !important;
        top: 10px !important;
        right: 68px !important;
        z-index: 9999999 !important;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        min-height: 36px !important;
        max-width: 36px !important;
        max-height: 36px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        background-color: #1E293B !important;
        border: 1px solid #475569 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.45) !important;
        transition: transform 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) + div[data-testid="stElementContainer"] button:hover,
    div[data-testid="stVerticalBlock"]:has(#theme-toggle-anchor) button:hover {
        transform: scale(1.12) !important;
        background-color: #334155 !important;
        border-color: #2DD4BF !important;
        box-shadow: 0 4px 14px rgba(45, 212, 191, 0.35) !important;
    }
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) + div[data-testid="stElementContainer"] button p,
    div[data-testid="stVerticalBlock"]:has(#theme-toggle-anchor) button p {
        font-size: 1.15rem !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Suppress popup notifications and toast */
    [data-testid="stToast"], .stToast {
        display: none !important;
    }
</style>
"""
    else:
        # LOCKED LIGHT MODE (Default)
        return """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Light Mode App Canvas */
    .stApp {
        background-color: #F5F7FA !important;
        color: #0B2545 !important;
    }

    /* Light Mode Top Header */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background-color: #F5F7FA !important;
        border-bottom: 1px solid #E2E8F0 !important;
    }
    header[data-testid="stHeader"] * {
        color: #0B2545 !important;
    }

    /* Light Mode Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #1E293B !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #0B2545 !important;
    }

    /* =========================================================================
       SIDEBAR NAVIGATION BAR - 100% VISIBILITY IN LIGHT MODE
       ========================================================================= */
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebar"] nav {
        background-color: transparent !important;
        padding-top: 10px !important;
        margin-bottom: 12px !important;
    }
    [data-testid="stSidebarNav"] *,
    [data-testid="stSidebarNavItems"] *,
    [data-testid="stSidebar"] nav * {
        color: #0B2545 !important;
        -webkit-text-fill-color: #0B2545 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stSidebarNav"] ul,
    [data-testid="stSidebarNavItems"] ul {
        list-style: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stSidebarNav"] li,
    [data-testid="stSidebarNavItems"] li {
        margin-bottom: 3px !important;
    }
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNav"] a:visited,
    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"],
    [data-testid="stSidebarNav"] [data-testid="stSidebarNavLink"] span,
    [data-testid="stSidebarNavItems"] a,
    [data-testid="stSidebarNavItems"] a span,
    [data-testid="stSidebar"] nav a,
    [data-testid="stSidebar"] nav a span {
        color: #0B2545 !important;
        -webkit-text-fill-color: #0B2545 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        text-decoration: none !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stSidebarNav"] a,
    [data-testid="stSidebarNavItems"] a,
    [data-testid="stSidebar"] nav a {
        background-color: transparent !important;
        border-radius: 8px !important;
        margin: 2px 0 !important;
        padding: 8px 12px !important;
        display: flex !important;
        align-items: center !important;
        transition: background-color 0.15s ease, color 0.15s ease !important;
    }
    [data-testid="stSidebarNav"] a:hover,
    [data-testid="stSidebarNavItems"] a:hover,
    [data-testid="stSidebar"] nav a:hover {
        background-color: #F1F5F9 !important;
    }
    [data-testid="stSidebarNav"] a:hover span,
    [data-testid="stSidebarNav"] a:hover *,
    [data-testid="stSidebarNavItems"] a:hover span,
    [data-testid="stSidebarNavItems"] a:hover *,
    [data-testid="stSidebar"] nav a:hover * {
        color: #1B998B !important;
        -webkit-text-fill-color: #1B998B !important;
    }
    /* Active / Selected Page in Light Mode */
    [data-testid="stSidebarNav"] a[aria-current="page"],
    [data-testid="stSidebarNav"] a[data-testid="stSidebarNavLink"][aria-current="page"],
    [data-testid="stSidebarNav"] li[aria-selected="true"] a,
    [data-testid="stSidebarNavItems"] a[aria-current="page"],
    [data-testid="stSidebar"] nav a[aria-current="page"] {
        background-color: #E2E8F0 !important;
        border-radius: 8px !important;
        border-left: 4px solid #1B998B !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] span,
    [data-testid="stSidebarNav"] a[aria-current="page"] *,
    [data-testid="stSidebarNav"] a[data-testid="stSidebarNavLink"][aria-current="page"] span,
    [data-testid="stSidebarNav"] li[aria-selected="true"] a span,
    [data-testid="stSidebarNavItems"] a[aria-current="page"] *,
    [data-testid="stSidebar"] nav a[aria-current="page"] * {
        color: #0B2545 !important;
        -webkit-text-fill-color: #0B2545 !important;
        font-weight: 800 !important;
    }
    [data-testid="stSidebarNav"] svg,
    [data-testid="stSidebarNavItems"] svg,
    [data-testid="stSidebar"] nav svg {
        fill: #1B998B !important;
        color: #1B998B !important;
    }

    /* Sidebar Form Inputs in Light Mode */
    [data-testid="stSidebar"] div[data-baseweb="input"],
    [data-testid="stSidebar"] div[data-baseweb="base-input"],
    [data-testid="stSidebar"] div[data-baseweb="select"],
    [data-testid="stSidebar"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-testid="stDateInput"] > div,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] > div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
    [data-testid="stSidebar"] input,
    div[data-testid="stDateInput"] div[data-baseweb="input"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #0B2545 !important;
        -webkit-text-fill-color: #0B2545 !important;
        border-color: #CBD5E1 !important;
    }
    [data-testid="stSidebar"] input::placeholder,
    input::placeholder,
    div[data-baseweb="select"] div {
        color: #64748B !important;
    }
    [data-testid="stSidebar"] span[data-baseweb="tag"],
    span[data-baseweb="tag"] {
        background-color: #F1F5F9 !important;
        color: #0B2545 !important;
        border: 1px solid #CBD5E1 !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"],
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #0B2545 !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover,
    button[kind="secondary"]:hover {
        background-color: #F1F5F9 !important;
        border-color: #1B998B !important;
        color: #0B2545 !important;
    }

    /* Page Header Banner */
    .page-header, .exec-header {
        background: linear-gradient(135deg, #0B2545 0%, #13315C 100%) !important;
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 22px;
        box-shadow: 0 4px 16px rgba(11, 37, 69, 0.12) !important;
    }
    .page-header *, .exec-header * {
        color: #FFFFFF !important;
    }
    .page-header h1, .exec-header h1, .page-header-title, .exec-header-title {
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 4px 0;
    }
    .page-header p, .exec-header p, .page-header-subtitle, .exec-header-subtitle {
        color: #CBD5E1 !important;
        font-size: 0.88rem;
        font-weight: 400;
        margin: 0;
    }

    /* Container Card Styling */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #FFFFFF !important;
        border-radius: 12px;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 2px 8px rgba(11, 37, 69, 0.05) !important;
        padding: 16px;
    }
    .card-title, .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0B2545 !important;
        margin: 0 0 12px 0;
    }

    /* KPI Cards with Teal Top Border */
    .kpi-card {
        background-color: #FFFFFF !important;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(11, 37, 69, 0.05) !important;
        border-top: 4px solid #1B998B !important;
        border-left: 1px solid #E2E8F0 !important;
        border-right: 1px solid #E2E8F0 !important;
        border-bottom: 1px solid #E2E8F0 !important;
        min-height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(11, 37, 69, 0.09) !important;
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B !important;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #0B2545 !important;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }
    .kpi-delta-pos {
        font-size: 0.78rem;
        font-weight: 600;
        color: #10B981 !important;
        margin-top: 6px;
    }
    .kpi-delta-neg {
        font-size: 0.78rem;
        font-weight: 600;
        color: #E63946 !important;
        margin-top: 6px;
    }
    .kpi-delta-neutral {
        font-size: 0.78rem;
        font-weight: 500;
        color: #64748B !important;
        margin-top: 6px;
    }

    /* Streamlit Metric Light Styling */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 2px 6px rgba(11, 37, 69, 0.04);
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #0B2545 !important;
        font-weight: 800 !important;
    }

    /* Top-Right Small Theme Toggle Icon Button — Light Mode */
    div:has(> #theme-toggle-anchor),
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) {
        display: none !important;
    }
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) + div[data-testid="stElementContainer"] {
        position: absolute !important;
        top: 0 !important;
        right: 0 !important;
        width: 0 !important;
        height: 0 !important;
        overflow: visible !important;
        z-index: 9999999 !important;
    }
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) + div[data-testid="stElementContainer"] button,
    div[data-testid="stVerticalBlock"]:has(#theme-toggle-anchor) button {
        position: fixed !important;
        top: 10px !important;
        right: 68px !important;
        z-index: 9999999 !important;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        min-height: 36px !important;
        max-width: 36px !important;
        max-height: 36px !important;
        border-radius: 50% !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 2px 8px rgba(11, 37, 69, 0.12) !important;
        transition: transform 0.15s ease, background-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) + div[data-testid="stElementContainer"] button:hover,
    div[data-testid="stVerticalBlock"]:has(#theme-toggle-anchor) button:hover {
        transform: scale(1.12) !important;
        background-color: #F8FAFC !important;
        border-color: #1B998B !important;
        box-shadow: 0 4px 14px rgba(27, 153, 139, 0.25) !important;
    }
    div[data-testid="stElementContainer"]:has(#theme-toggle-anchor) + div[data-testid="stElementContainer"] button p,
    div[data-testid="stVerticalBlock"]:has(#theme-toggle-anchor) button p {
        font-size: 1.15rem !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Suppress popup notifications and toast */
    [data-testid="stToast"], .stToast {
        display: none !important;
    }
</style>
"""


def apply_theme() -> None:
    """Injects responsive theme CSS for the current theme mode into the Streamlit app DOM."""
    st.markdown(get_theme_css(), unsafe_allow_html=True)


def render_theme_toggle_button() -> None:
    """Renders a sleek, circular icon button in the top-right corner to toggle themes."""
    dark = is_dark_mode()
    icon = "☀️" if dark else "🌙"
    tooltip = "Switch to Light Mode" if dark else "Switch to Dark Mode"

    st.markdown('<div id="theme-toggle-anchor"></div>', unsafe_allow_html=True)
    if st.button(icon, key="global_theme_toggle_btn", help=tooltip):
        st.session_state["theme_mode"] = "light" if dark else "dark"
        st.rerun()


# Empty placeholder for backwards compatibility with any legacy imports
COMMON_PAGE_CSS = ""


def render_takeaway(text: str, is_alert: bool = False) -> None:
    """Renders a prominent data-driven key takeaway badge under charts."""
    dark = is_dark_mode()
    if dark:
        border_color = THEME["red"] if is_alert else THEME["teal"]
        bg_color = "#450A0A" if is_alert else "#064E3B"
        text_color = "#FECACA" if is_alert else "#D1FAE5"
    else:
        border_color = THEME["red"] if is_alert else THEME["teal"]
        bg_color = "#FEF2F2" if is_alert else "#F0FDF9"
        text_color = "#991B1B" if is_alert else "#065F46"

    icon = "⚠️" if is_alert else "💡"
    html = f"""
    <div style="background-color: {bg_color}; border-left: 4px solid {border_color}; padding: 9px 14px; border-radius: 0 8px 8px 0; margin-top: 8px; margin-bottom: 4px; font-size: 0.84rem; color: {text_color}; line-height: 1.45;">
        <strong>{icon} Takeaway:</strong> {text}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def _apply_standard_layout(fig: go.Figure, title: str, height: int = 380) -> go.Figure:
    """Applies standardized font, margin, background, and hover settings."""
    dark = is_dark_mode()
    card_bg = THEME["card"]
    font_color = THEME["text"]
    title_color = "#F8FAFC" if dark else "#0B2545"
    grid_color = THEME["grid"]
    muted_color = THEME["muted"]

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(family=FONT_FAMILY, size=14, color=title_color),
            x=0.01,
            y=0.96,
        ),
        font=dict(family=FONT_FAMILY, size=11, color=font_color),
        plot_bgcolor=card_bg,
        paper_bgcolor=card_bg,
        height=height,
        margin=dict(l=20, r=20, t=50, b=25),
        legend=dict(
            font=dict(family=FONT_FAMILY, size=10, color=font_color),
            title=dict(font=dict(color=font_color)),
        ),
        hoverlabel=dict(
            bgcolor="#0F172A" if dark else "#FFFFFF",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color="#F8FAFC" if dark else "#0B2545",
            bordercolor=grid_color,
        ),
    )
    try:
        fig.update_xaxes(
            title=dict(font=dict(color=muted_color)),
            tickfont=dict(color=muted_color),
            gridcolor=grid_color,
        )
        fig.update_yaxes(
            title=dict(font=dict(color=muted_color)),
            tickfont=dict(color=muted_color),
            gridcolor=grid_color,
        )
        if hasattr(fig.layout, "yaxis2") and fig.layout.yaxis2 is not None:
            fig.update_layout(
                yaxis2=dict(
                    title=dict(font=dict(color=muted_color, size=11)),
                    tickfont=dict(color=muted_color),
                )
            )
        fig.update_traces(
            selector=dict(type="pie"),
            textfont=dict(color=font_color),
        )
        for trace in fig.data:
            if hasattr(trace, "marker") and trace.marker is not None:
                if hasattr(trace.marker, "colorbar") and trace.marker.colorbar is not None:
                    trace.marker.colorbar.title.font.color = font_color
                    trace.marker.colorbar.tickfont.color = muted_color
        if hasattr(fig.layout, "coloraxis") and fig.layout.coloraxis is not None:
            if hasattr(fig.layout.coloraxis, "colorbar") and fig.layout.coloraxis.colorbar is not None:
                fig.layout.coloraxis.colorbar.title.font.color = font_color
                fig.layout.coloraxis.colorbar.tickfont.color = muted_color
    except Exception:
        pass
    return fig


# -----------------------------------------------------------------------------
# Overview Charts
# -----------------------------------------------------------------------------
def create_monthly_trend_chart(trend_df: pd.DataFrame) -> go.Figure:
    """Creates a line/bar hybrid chart showing monthly revenue, profit, and MoM growth markers."""
    fig = go.Figure()
    if trend_df.empty:
        fig.add_annotation(text="No data available for selected filter", showarrow=False)
        return _apply_standard_layout(fig, "Monthly Sales Trajectory")

    fig.add_trace(
        go.Bar(
            x=trend_df["year_month"],
            y=trend_df["sales"],
            name="Sales (₹)",
            marker_color=THEME["teal"],
            opacity=0.85,
            hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.2f}<extra></extra>",
            yaxis="y1",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=trend_df["year_month"],
            y=trend_df["profit"],
            name="Profit (₹)",
            mode="lines+markers",
            line=dict(color=THEME["navy"], width=2.5),
            marker=dict(size=6, color=THEME["navy"]),
            hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:,.2f}<extra></extra>",
            yaxis="y1",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=trend_df["year_month"],
            y=trend_df["mom_growth_pct"],
            name="MoM Growth %",
            mode="markers",
            marker=dict(
                size=8,
                color=trend_df["mom_growth_pct"].apply(
                    lambda g: THEME["teal"] if (pd.notna(g) and g >= 0) else THEME["red"]
                ),
                symbol="diamond",
            ),
            hovertemplate="<b>%{x}</b><br>MoM Growth: %{y:+.1f}%<extra></extra>",
            yaxis="y2",
        )
    )

    fig.update_layout(
        xaxis=dict(gridcolor=THEME["grid"], tickangle=-45, showline=True, linecolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Revenue (₹)", font=dict(color=THEME["muted"], size=11)), gridcolor=THEME["grid"]),
        yaxis2=dict(
            title=dict(text="MoM %", font=dict(color=THEME["muted"], size=11)),
            tickfont=dict(color=THEME["muted"]),
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=True,
            zerolinecolor=THEME["grid"],
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=THEME["text"])),
    )
    return _apply_standard_layout(fig, "Monthly Sales & Profit Trajectory", height=370)


def create_category_bar_chart(cat_df: pd.DataFrame) -> go.Figure:
    """Creates a horizontal bar chart displaying revenue and gross margin by category."""
    fig = go.Figure()
    if cat_df.empty:
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_standard_layout(fig, "Category Revenue")

    sorted_df = cat_df.sort_values(by="sales", ascending=True)
    fig.add_trace(
        go.Bar(
            y=sorted_df["product_category"],
            x=sorted_df["sales"],
            orientation="h",
            marker=dict(
                color=sorted_df["margin_pct"],
                colorscale=[[0, THEME["amber"]], [0.5, THEME["teal"]], [1, THEME["navy"]]],
                colorbar=dict(title=dict(text="Margin %", font=dict(size=10, color=THEME["text"])), tickfont=dict(color=THEME["muted"]), thickness=10, len=0.7),
            ),
            text=[f"₹{s/1e5:.1f}L ({m:.1f}%)" if s >= 1e5 else f"₹{s/1e3:.0f}K ({m:.1f}%)" for s, m in zip(sorted_df["sales"], sorted_df["margin_pct"])],
            textposition="auto",
            insidetextfont=dict(color="#0B2545" if not is_dark_mode() else "#FFFFFF", size=10),
            outsidetextfont=dict(color=THEME["text"], size=10),
            hovertemplate="<b>%{y}</b><br>Sales: ₹%{x:,.2f}<br>Contribution: %{customdata:.1f}%<extra></extra>",
            customdata=sorted_df["sales_contribution_pct"],
        )
    )
    fig.update_layout(
        xaxis=dict(title=dict(text="Sales (₹)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        yaxis=dict(title="", tickfont=dict(size=11, color=THEME["text"])),
    )
    return _apply_standard_layout(fig, "Category Revenue & Margin %", height=370)


def create_region_donut_chart(reg_df: pd.DataFrame) -> go.Figure:
    """Creates a donut chart illustrating regional sales contribution."""
    fig = go.Figure()
    if reg_df.empty:
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_standard_layout(fig, "Region Contribution")

    color_palette = [THEME["teal"], THEME["navy"], THEME["blue"], THEME["amber"], "#8338EC"]
    fig.add_trace(
        go.Pie(
            labels=reg_df["region"],
            values=reg_df["sales"],
            hole=0.52,
            marker=dict(colors=color_palette[: len(reg_df)]),
            textinfo="label+percent",
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>Sales: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>",
            showlegend=False,
        )
    )
    return _apply_standard_layout(fig, "Regional Sales Share", height=370)


def create_top_products_chart(prod_df: pd.DataFrame) -> go.Figure:
    """Creates a horizontal bar chart displaying top products by completed sales."""
    fig = go.Figure()
    if prod_df.empty:
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_standard_layout(fig, "Top Products")

    sorted_df = prod_df.sort_values(by="sales", ascending=True).tail(10)
    short_names = [name[:26] + "..." if len(name) > 28 else name for name in sorted_df["product_name"]]

    fig.add_trace(
        go.Bar(
            y=short_names,
            x=sorted_df["sales"],
            orientation="h",
            marker=dict(color=THEME["navy"]),
            text=[f"₹{s/1e5:.2f}L" if s >= 1e5 else f"₹{s/1e3:.1f}K" for s in sorted_df["sales"]],
            textposition="outside",
            outsidetextfont=dict(color=THEME["text"], size=10),
            hovertemplate="<b>%{customdata}</b><br>Sales: ₹%{x:,.2f}<extra></extra>",
            customdata=sorted_df["product_name"],
        )
    )
    max_sales = float(sorted_df["sales"].max()) if not sorted_df.empty else 1.0
    fig.update_layout(
        xaxis=dict(
            title=dict(text="Sales (₹)", font=dict(size=11, color=THEME["muted"])),
            gridcolor=THEME["grid"],
            range=[0, max_sales * 1.30],
        ),
        yaxis=dict(title="", tickfont=dict(size=10, color=THEME["text"])),
    )
    return _apply_standard_layout(fig, "Top 10 Products by Revenue", height=390)


# -----------------------------------------------------------------------------
# Page 2: Profitability Charts
# -----------------------------------------------------------------------------
def create_category_profit_bar(cat_df: pd.DataFrame) -> go.Figure:
    """Creates a horizontal bar chart of realized gross profit by category."""
    fig = go.Figure()
    if cat_df.empty:
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_standard_layout(fig, "Category Gross Profit")

    sorted_df = cat_df.sort_values(by="profit", ascending=True)
    colors = [THEME["teal"] if p >= 0 else THEME["red"] for p in sorted_df["profit"]]

    fig.add_trace(
        go.Bar(
            y=sorted_df["product_category"],
            x=sorted_df["profit"],
            orientation="h",
            marker=dict(color=colors),
            text=[f"₹{p/1e5:.2f}L ({m:.1f}%)" if abs(p) >= 1e5 else f"₹{p/1e3:.1f}K ({m:.1f}%)" for p, m in zip(sorted_df["profit"], sorted_df["margin_pct"])],
            textposition="auto",
            insidetextfont=dict(color="#0B2545" if not is_dark_mode() else "#FFFFFF", size=10),
            outsidetextfont=dict(color=THEME["text"], size=10),
            hovertemplate="<b>%{y}</b><br>Gross Profit: ₹%{x:,.2f}<br>Profit Margin: %{customdata:.1f}%<extra></extra>",
            customdata=sorted_df["margin_pct"],
        )
    )
    fig.update_layout(
        xaxis=dict(title=dict(text="Gross Profit (₹)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        yaxis=dict(title="", tickfont=dict(size=11, color=THEME["text"])),
    )
    return _apply_standard_layout(fig, "Gross Profit by Product Category", height=370)


def create_category_product_treemap(comp_df: pd.DataFrame) -> go.Figure:
    """Creates a hierarchical treemap (Category -> Product) sized by sales and colored by margin."""
    if comp_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_standard_layout(fig, "Category & Product Hierarchy")

    grouped = (
        comp_df.groupby(["product_category", "product_name"])
        .agg(sales_amount=("sales_amount", "sum"), profit_amount=("profit_amount", "sum"))
        .reset_index()
    )
    grouped["profit_margin_pct"] = np.where(
        grouped["sales_amount"] > 0,
        ((grouped["profit_amount"] / grouped["sales_amount"]) * 100.0).round(2),
        0.0,
    )

    fig = px.treemap(
        grouped,
        path=["product_category", "product_name"],
        values="sales_amount",
        color="profit_margin_pct",
        color_continuous_scale=[[0, THEME["red"]], [0.35, THEME["amber"]], [0.65, THEME["teal"]], [1.0, THEME["navy"]]],
        color_continuous_midpoint=15.0,
    )
    fig.update_traces(
        textinfo="label+value+percent entry",
        hovertemplate="<b>%{label}</b><br>Sales: ₹%{value:,.2f}<br>Margin: %{color:.1f}%<extra></extra>",
    )
    fig.update_layout(
        coloraxis_colorbar=dict(title=dict(text="Margin %", font=dict(size=10)), thickness=12, len=0.8),
    )
    return _apply_standard_layout(fig, "Category & Product Hierarchy (Size = Sales, Color = Margin %)", height=450)


def create_discount_band_chart(discount_df: pd.DataFrame) -> go.Figure:
    """Creates a dual-axis chart showing sales volume vs realized profit margin across discount tiers."""
    fig = go.Figure()
    if discount_df.empty:
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_standard_layout(fig, "Discount Band vs Margin")

    # Sales bars
    fig.add_trace(
        go.Bar(
            x=discount_df["discount_band"].astype(str),
            y=discount_df["sales"],
            name="Sales (₹)",
            marker_color=THEME["navy"],
            opacity=0.85,
            hovertemplate="<b>Band: %{x}</b><br>Sales: ₹%{y:,.2f}<extra></extra>",
            yaxis="y1",
        )
    )

    # Margin line
    fig.add_trace(
        go.Scatter(
            x=discount_df["discount_band"].astype(str),
            y=discount_df["margin_pct"],
            name="Profit Margin %",
            mode="lines+markers+text",
            line=dict(color=THEME["teal"], width=3),
            marker=dict(size=8, color=THEME["teal"]),
            text=[f"{m:.1f}%" for m in discount_df["margin_pct"]],
            textposition="top center",
            hovertemplate="<b>Band: %{x}</b><br>Margin: %{y:.1f}%<extra></extra>",
            yaxis="y2",
        )
    )

    fig.update_layout(
        xaxis=dict(title=dict(text="Discount Band", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Sales (₹)", font=dict(color=THEME["muted"], size=11)), gridcolor=THEME["grid"]),
        yaxis2=dict(
            title=dict(text="Margin %", font=dict(color=THEME["teal"], size=11)),
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=True,
            zerolinecolor=THEME["red"],
            zerolinewidth=1.5,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    )
    return _apply_standard_layout(fig, "Discount Band vs Gross Margin %", height=380)


def create_discount_scatter_chart(comp_df: pd.DataFrame) -> go.Figure:
    """Creates a scatter plot of discount % vs realized margin % categorized by product category."""
    if comp_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_standard_layout(fig, "Discount % vs Margin %")

    category_palette = {
        "Electronics": THEME["navy"],
        "Fashion": THEME["teal"],
        "Home & Kitchen": THEME["blue"],
        "Beauty & Personal Care": "#D946EF",
        "Books & Stationery": THEME["amber"],
        "Sports & Fitness": "#10B981",
        "Grocery & Gourmet": "#8B5CF6",
    }

    fig = px.scatter(
        comp_df,
        x="discount_percent",
        y="profit_margin_pct",
        color="product_category",
        color_discrete_map=category_palette,
        size="sales_amount",
        hover_name="product_name",
        hover_data={"discount_percent": ":.1f%", "profit_margin_pct": ":.1f%", "sales_amount": ":,.0f", "product_category": True},
        opacity=0.75,
    )

    # Reference zero margin line
    fig.add_hline(y=0, line_dash="dash", line_color=THEME["red"], annotation_text="Break-even (0% Margin)", annotation_position="bottom right")

    fig.update_layout(
        xaxis=dict(title=dict(text="Discount Applied (%)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Realized Profit Margin (%)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        legend=dict(orientation="h", yanchor="top", y=-0.20, xanchor="center", x=0.5, font=dict(size=9), title=dict(text="")),
    )
    fig = _apply_standard_layout(fig, "Discount % vs Margin % by Product Category", height=430)
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=65))
    return fig


# -----------------------------------------------------------------------------
# Page 3: Regional Charts
# -----------------------------------------------------------------------------
def create_india_geo_bubble_map(city_df: pd.DataFrame, coords_df: pd.DataFrame) -> go.Figure:
    """Creates an interactive India bubble map of city sales and profit margin."""
    if city_df.empty or coords_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No geographical data available", showarrow=False)
        return _apply_standard_layout(fig, "India Regional Sales Hubs")

    merged = city_df.merge(coords_df, left_on="city", right_on="City", how="inner")
    if merged.empty:
        fig = go.Figure()
        fig.add_annotation(text="No matching city coordinates found", showarrow=False)
        return _apply_standard_layout(fig, "India Regional Sales Hubs")

    fig = px.scatter_geo(
        merged,
        lat="Latitude",
        lon="Longitude",
        size="sales_amount",
        color="profit_margin_pct",
        hover_name="city",
        scope="asia",
        color_continuous_scale=[[0, THEME["red"]], [0.35, THEME["amber"]], [0.65, THEME["teal"]], [1.0, THEME["navy"]]],
        color_continuous_midpoint=15.0,
        hover_data={"State": True, "sales_amount": ":,.0f", "profit_margin_pct": ":.1f%", "Latitude": False, "Longitude": False},
        size_max=32,
    )
    dark = is_dark_mode()
    fig.update_geos(
        fitbounds="locations",
        visible=True,
        showcountries=True,
        countrycolor="#475569" if dark else "#CBD5E1",
        showsubunits=True,
        subunitcolor="#334155" if dark else "#E2E8F0",
        showland=True,
        landcolor="#1E293B" if dark else "#F8FAFC",
        showocean=True,
        oceancolor="#0F172A" if dark else "#EDF2F7",
    )
    fig.update_layout(
        coloraxis_colorbar=dict(title=dict(text="Margin %", font=dict(size=10)), thickness=12, len=0.8),
    )
    return _apply_standard_layout(fig, "Geographic Sales & Margin Distribution (India City Hubs)", height=480)


def create_state_sales_profit_chart(state_df: pd.DataFrame, top_n_states: int = 12) -> go.Figure:
    """Creates a grouped bar chart of sales and profit for top Indian states."""
    fig = go.Figure()
    if state_df.empty:
        fig.add_annotation(text="No state data available", showarrow=False)
        return _apply_standard_layout(fig, "State-wise Performance")

    top_states = state_df.sort_values(by="sales", ascending=False).head(top_n_states)

    fig.add_trace(
        go.Bar(
            x=top_states["state"],
            y=top_states["sales"],
            name="Sales (₹)",
            marker_color=THEME["navy"],
            hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=top_states["state"],
            y=top_states["profit"],
            name="Profit (₹)",
            marker_color=THEME["teal"],
            hovertemplate="<b>%{x}</b><br>Profit: ₹%{y:,.2f}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        xaxis=dict(tickangle=-35, gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Amount (₹)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    )
    return _apply_standard_layout(fig, f"Top {len(top_states)} States: Sales & Gross Profit Comparison", height=390)


def create_region_category_margin_heatmap(comp_df: pd.DataFrame) -> go.Figure:
    """Creates a heatmap matrix of Region x Product Category showing realized profit margin %."""
    if comp_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return _apply_standard_layout(fig, "Region × Category Margin Heatmap")

    pivot = comp_df.pivot_table(
        index="region",
        columns="product_category",
        values=["sales_amount", "profit_amount"],
        aggfunc="sum",
    )
    margin_matrix = ((pivot["profit_amount"] / pivot["sales_amount"]) * 100.0).round(1)

    regions = list(margin_matrix.index)
    categories = list(margin_matrix.columns)
    z_values = margin_matrix.values

    # Text annotations
    text_values = [[f"{val:.1f}%" if pd.notna(val) else "—" for val in row] for row in z_values]

    fig = go.Figure(
        data=go.Heatmap(
            z=z_values,
            x=categories,
            y=regions,
            text=text_values,
            texttemplate="%{text}",
            textfont=dict(family=FONT_FAMILY, size=11, color="#0B2545"),
            colorscale=[[0, "#FCA5A5"], [0.4, "#FEF3C7"], [0.7, "#A7F3D0"], [1.0, "#34D399"]],
            colorbar=dict(title=dict(text="Margin %", font=dict(size=10)), thickness=12, len=0.8),
            hovertemplate="<b>Region:</b> %{y}<br><b>Category:</b> %{x}<br><b>Margin:</b> %{z:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        xaxis=dict(title="", tickangle=-20),
        yaxis=dict(title="", tickfont=dict(size=11, color=THEME["text"])),
    )
    return _apply_standard_layout(fig, "Region × Category Profit Margin % Heatmap", height=380)


# -----------------------------------------------------------------------------
# Page 4: Customers & Products Charts
# -----------------------------------------------------------------------------
def create_segment_analysis_chart(segment_df: pd.DataFrame) -> go.Figure:
    """Creates a multi-bar chart comparing Sales, Orders, AOV, and Margin % across customer segments."""
    fig = go.Figure()
    if segment_df.empty:
        fig.add_annotation(text="No segment data available", showarrow=False)
        return _apply_standard_layout(fig, "Customer Segment Financials")

    # Clustered Bar: Sales and Orders
    fig.add_trace(
        go.Bar(
            x=segment_df["customer_segment"],
            y=segment_df["sales"],
            name="Sales (₹)",
            marker_color=THEME["navy"],
            yaxis="y1",
            text=[f"₹{s/1e5:.1f}L" if s >= 1e5 else f"₹{s/1e3:.0f}K" for s in segment_df["sales"]],
            textposition="auto",
            insidetextfont=dict(color="#0B2545" if not is_dark_mode() else "#FFFFFF", size=10),
            outsidetextfont=dict(color=THEME["text"], size=10),
            hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.2f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=segment_df["customer_segment"],
            y=segment_df["margin_pct"],
            name="Margin %",
            mode="lines+markers+text",
            line=dict(color=THEME["teal"], width=2.5),
            marker=dict(size=8, color=THEME["teal"]),
            text=[f"{m:.1f}%" for m in segment_df["margin_pct"]],
            textposition="top center",
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        xaxis=dict(gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Sales (₹)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        yaxis2=dict(
            title=dict(text="Margin %", font=dict(color=THEME["teal"], size=11)),
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=THEME["text"])),
    )
    return _apply_standard_layout(fig, "Customer Segment Sales & Profit Margin %", height=380)


def create_customer_pareto_chart(cust_df: pd.DataFrame) -> go.Figure:
    """Creates a Pareto 80/20 cumulative spend curve."""
    fig = go.Figure()
    if cust_df.empty:
        fig.add_annotation(text="No customer data available", showarrow=False)
        return _apply_standard_layout(fig, "Customer Pareto Curve")

    total_customers = len(cust_df)
    cust_sorted = cust_df.sort_values(by="total_spend", ascending=False).reset_index(drop=True)
    cust_sorted["customer_pct"] = ((cust_sorted.index + 1) / total_customers * 100.0).round(2)

    # Find the customer % at 80% cumulative spend
    pareto_80_row = cust_sorted[cust_sorted["cumulative_pct"] >= 80.0].head(1)
    pareto_cust_pct = float(pareto_80_row["customer_pct"].iloc[0]) if not pareto_80_row.empty else 20.0

    # Shaded curve
    fig.add_trace(
        go.Scatter(
            x=cust_sorted["customer_pct"],
            y=cust_sorted["cumulative_pct"],
            mode="lines",
            name="Cumulative Spend %",
            line=dict(color=THEME["teal"], width=3),
            fill="tozeroy",
            fillcolor="rgba(27, 153, 139, 0.08)",
            hovertemplate="Top %{x:.1f}% Customers<br>Drive %{y:.1f}% Revenue<extra></extra>",
        )
    )

    # 45-degree parity line
    fig.add_trace(
        go.Scatter(
            x=[0, 100],
            y=[0, 100],
            mode="lines",
            name="Equal Parity",
            line=dict(color=THEME["muted"], width=1.5, dash="dash"),
            hoverinfo="skip",
        )
    )

    # 80% revenue benchmark horizontal & vertical lines
    fig.add_hline(y=80, line_dash="dot", line_color=THEME["red"], annotation_text="80% Revenue", annotation_position="bottom right")
    fig.add_vline(x=pareto_cust_pct, line_dash="dot", line_color=THEME["red"], annotation_text=f"{pareto_cust_pct:.1f}% Customers", annotation_position="top left")

    fig.update_layout(
        xaxis=dict(title=dict(text="Cumulative % of Customers", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"], range=[0, 100]),
        yaxis=dict(title=dict(text="Cumulative % of Sales", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"], range=[0, 102]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10, color=THEME["text"])),
    )
    return _apply_standard_layout(fig, f"Customer Pareto 80/20 Curve (Top {pareto_cust_pct:.1f}% drive 80% sales)", height=390)


def create_bestselling_products_chart(prod_df: pd.DataFrame, metric: str = "units") -> go.Figure:
    """Creates a horizontal bar chart of top 10 products by units or by sales revenue."""
    fig = go.Figure()
    title_suffix = "Units Sold" if metric == "units" else "Sales Revenue"
    if prod_df.empty:
        fig.add_annotation(text="No product data available", showarrow=False)
        return _apply_standard_layout(fig, f"Top Products by {title_suffix}")

    sorted_df = prod_df.sort_values(by=metric, ascending=True).tail(10)
    short_names = [name[:26] + "..." if len(name) > 28 else name for name in sorted_df["product_name"]]

    text_labels = [f"{u:,} units" if metric == "units" else (f"₹{s/1e5:.2f}L" if s >= 1e5 else f"₹{s/1e3:.1f}K") for u, s in zip(sorted_df["units"], sorted_df["sales"])]
    bar_color = THEME["teal"] if metric == "units" else THEME["navy"]

    fig.add_trace(
        go.Bar(
            y=short_names,
            x=sorted_df[metric],
            orientation="h",
            marker=dict(color=bar_color),
            text=text_labels,
            textposition="auto",
            insidetextfont=dict(color="#FFFFFF" if is_dark_mode() else "#0B2545", size=10),
            outsidetextfont=dict(color=THEME["text"], size=10),
            hovertemplate="<b>%{customdata}</b><br>Value: %{x:,}<extra></extra>",
            customdata=sorted_df["product_name"],
        )
    )
    max_sales = float(sorted_df["sales"].max()) if not sorted_df.empty else 1.0
    fig.update_layout(
        xaxis=dict(
            title=dict(text={title_suffix: title_suffix}.get(title_suffix, title_suffix), font=dict(size=11, color=THEME["muted"])),
            gridcolor=THEME["grid"],
            range=[0, max_sales * 1.30],
        ),
        yaxis=dict(title="", tickfont=dict(size=10, color=THEME["text"])),
    )
    return _apply_standard_layout(fig, f"Top 10 Products by {title_suffix}", height=380)


def create_product_contribution_chart(prod_df: pd.DataFrame) -> go.Figure:
    """Creates a horizontal bar chart displaying revenue contribution % of top products."""
    fig = go.Figure()
    if prod_df.empty:
        fig.add_annotation(text="No product data available", showarrow=False)
        return _apply_standard_layout(fig, "Product Sales Share %")

    sorted_df = prod_df.sort_values(by="sales_contribution_pct", ascending=True).tail(10)
    short_names = [name[:26] + "..." if len(name) > 28 else name for name in sorted_df["product_name"]]

    fig.add_trace(
        go.Bar(
            y=short_names,
            x=sorted_df["sales_contribution_pct"],
            orientation="h",
            marker=dict(color=THEME["blue"]),
            text=[f"{p:.1f}%" for p in sorted_df["sales_contribution_pct"]],
            textposition="outside",
            outsidetextfont=dict(color=THEME["text"], size=10),
            hovertemplate="<b>%{customdata}</b><br>Contribution: %{x:.2f}%<extra></extra>",
            customdata=sorted_df["product_name"],
        )
    )
    max_contrib = float(sorted_df["sales_contribution_pct"].max()) if not sorted_df.empty else 1.0
    fig.update_layout(
        xaxis=dict(
            title=dict(text="Revenue Contribution (%)", font=dict(size=11, color=THEME["muted"])),
            gridcolor=THEME["grid"],
            range=[0, max_contrib * 1.30],
        ),
        yaxis=dict(title="", tickfont=dict(size=10, color=THEME["text"])),
    )
    return _apply_standard_layout(fig, "Top 10 Products Revenue Contribution %", height=380)


# -----------------------------------------------------------------------------
# Page 5: Operations Charts
# -----------------------------------------------------------------------------
def create_payment_method_bar(pay_df: pd.DataFrame) -> go.Figure:
    """Creates a clustered bar chart of Sales and Order volume by Payment Method."""
    fig = go.Figure()
    if pay_df.empty:
        fig.add_annotation(text="No payment data available", showarrow=False)
        return _apply_standard_layout(fig, "Payment Method Volume")

    sorted_df = pay_df.sort_values(by="sales", ascending=False)

    fig.add_trace(
        go.Bar(
            x=sorted_df["payment_method"],
            y=sorted_df["sales"],
            name="Sales (₹)",
            marker_color=THEME["navy"],
            yaxis="y1",
            hovertemplate="<b>%{x}</b><br>Sales: ₹%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=sorted_df["payment_method"],
            y=sorted_df["orders"],
            name="Order Count",
            marker_color=THEME["teal"],
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Orders: %{y:,}<extra></extra>",
        )
    )

    fig.update_layout(
        barmode="group",
        xaxis=dict(gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Sales (₹)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        yaxis2=dict(
            title=dict(text="Orders", font=dict(size=11, color=THEME["teal"])),
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    )
    return _apply_standard_layout(fig, "Payment Method: Sales & Order Volume", height=380)


def create_upi_share_trend_chart(upi_trend_df: pd.DataFrame) -> go.Figure:
    """Creates a monthly line chart of UPI transaction share % over time."""
    fig = go.Figure()
    if upi_trend_df.empty:
        fig.add_annotation(text="No UPI trend data available", showarrow=False)
        return _apply_standard_layout(fig, "Monthly UPI Share Trend")

    avg_upi = upi_trend_df["upi_order_share_pct"].mean()

    fig.add_trace(
        go.Scatter(
            x=upi_trend_df["year_month"],
            y=upi_trend_df["upi_order_share_pct"],
            mode="lines+markers",
            name="UPI Order Share %",
            line=dict(color=THEME["teal"], width=2.5),
            marker=dict(size=6, color=THEME["teal"]),
            hovertemplate="<b>%{x}</b><br>UPI Share: %{y:.1f}%<extra></extra>",
        )
    )

    fig.add_hline(
        y=avg_upi,
        line_dash="dash",
        line_color=THEME["muted"],
        annotation_text=f"Avg: {avg_upi:.1f}%",
        annotation_position="bottom right",
    )

    fig.update_layout(
        xaxis=dict(tickangle=-45, gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="UPI Share (%)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    )
    return _apply_standard_layout(fig, "Monthly UPI Share of Completed Orders (%)", height=380)


def create_shipping_delay_chart(ship_deliv_df: pd.DataFrame) -> go.Figure:
    """Creates a bar chart of Delay Rate % by Shipping Mode."""
    fig = go.Figure()
    if ship_deliv_df.empty:
        fig.add_annotation(text="No shipping delivery data available", showarrow=False)
        return _apply_standard_layout(fig, "Shipping Mode Delay Rate")

    df = ship_deliv_df.copy()
    if "delay_rate" not in df.columns:
        df["delay_rate"] = (100.0 - df["on_time_pct"]).round(2)

    sorted_df = df.sort_values(by="delay_rate", ascending=False)
    colors = [THEME["red"] if dr >= 8.0 else THEME["amber"] if dr >= 4.0 else THEME["teal"] for dr in sorted_df["delay_rate"]]

    fig.add_trace(
        go.Bar(
            x=sorted_df["shipping_mode"],
            y=sorted_df["delay_rate"],
            marker_color=colors,
            text=[f"{dr:.1f}%" for dr in sorted_df["delay_rate"]],
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Delay Rate: %{y:.1f}%<br>Delivered: %{customdata[0]}<br>Delayed: %{customdata[1]}<extra></extra>",
            customdata=list(zip(sorted_df["delivered"], sorted_df["delayed"])),
        )
    )

    fig.update_layout(
        xaxis=dict(title="", gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Delay Rate (%)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
    )
    return _apply_standard_layout(fig, "Fulfillment Delay Rate % by Shipping Mode", height=380)


def create_delivery_status_donut(status_df: pd.DataFrame) -> go.Figure:
    """Creates a donut chart representing distribution across all delivery statuses."""
    fig = go.Figure()
    if status_df.empty:
        fig.add_annotation(text="No delivery data available", showarrow=False)
        return _apply_standard_layout(fig, "Order Fulfillment Status")

    color_map = {
        "Delivered": THEME["teal"],
        "Delayed": THEME["amber"],
        "Returned": "#8338EC",
        "Cancelled": THEME["red"],
    }
    colors = [color_map.get(s, THEME["blue"]) for s in status_df["status"]]

    fig.add_trace(
        go.Pie(
            labels=status_df["status"],
            values=status_df["count"],
            hole=0.52,
            marker=dict(colors=colors),
            textinfo="label+percent",
            textposition="outside",
            hovertemplate="<b>%{label}</b><br>Orders: %{value:,}<br>Share: %{percent}<extra></extra>",
            showlegend=False,
        )
    )
    return _apply_standard_layout(fig, "Order Fulfillment Status Breakdown", height=380)


def create_regional_delay_chart(reg_deliv_df: pd.DataFrame) -> go.Figure:
    """Creates a bar chart of Delay Rate % by Region."""
    fig = go.Figure()
    if reg_deliv_df.empty:
        fig.add_annotation(text="No regional delivery data available", showarrow=False)
        return _apply_standard_layout(fig, "Regional Delay Rate")

    df = reg_deliv_df.copy()
    if "delay_rate" not in df.columns:
        df["delay_rate"] = (100.0 - df["on_time_pct"]).round(2)

    sorted_df = df.sort_values(by="delay_rate", ascending=False)
    colors = [THEME["red"] if dr >= 10.0 else THEME["amber"] if dr >= 6.0 else THEME["teal"] for dr in sorted_df["delay_rate"]]

    fig.add_trace(
        go.Bar(
            x=sorted_df["region"],
            y=sorted_df["delay_rate"],
            marker_color=colors,
            text=[f"{dr:.1f}%" for dr in sorted_df["delay_rate"]],
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Delay Rate: %{y:.1f}%<extra></extra>",
        )
    )

    fig.update_layout(
        xaxis=dict(title="", gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Delay Rate (%)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
    )
    return _apply_standard_layout(fig, "Regional Fulfillment Delay Rate %", height=380)


def create_category_return_chart(cat_deliv_df: pd.DataFrame) -> go.Figure:
    """Creates a bar chart of Return Rate % across Product Categories."""
    fig = go.Figure()
    if cat_deliv_df.empty:
        fig.add_annotation(text="No category return data available", showarrow=False)
        return _apply_standard_layout(fig, "Category Return Rate")

    sorted_df = cat_deliv_df.sort_values(by="return_rate", ascending=False)
    colors = [THEME["red"] if r >= 6.0 else THEME["amber"] if r >= 4.0 else THEME["teal"] for r in sorted_df["return_rate"]]

    fig.add_trace(
        go.Bar(
            x=sorted_df["product_category"],
            y=sorted_df["return_rate"],
            marker_color=colors,
            text=[f"{r:.1f}%" for r in sorted_df["return_rate"]],
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Return Rate: %{y:.1f}%<br>Returned Orders: %{customdata}<extra></extra>",
            customdata=sorted_df["returned"],
        )
    )

    fig.update_layout(
        xaxis=dict(title="", tickangle=-25, gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Return Rate (%)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
    )
    return _apply_standard_layout(fig, "Product Category Return Rate %", height=380)


def create_cancellation_trend_chart(monthly_cancel_df: pd.DataFrame) -> go.Figure:
    """Creates a monthly line chart of order cancellation rate % over time."""
    fig = go.Figure()
    if monthly_cancel_df.empty:
        fig.add_annotation(text="No cancellation trend data available", showarrow=False)
        return _apply_standard_layout(fig, "Monthly Cancellation Rate")

    avg_cancel = monthly_cancel_df["cancel_rate"].mean()

    fig.add_trace(
        go.Scatter(
            x=monthly_cancel_df["year_month"],
            y=monthly_cancel_df["cancel_rate"],
            mode="lines+markers",
            name="Cancellation Rate %",
            line=dict(color=THEME["red"], width=2.5),
            marker=dict(size=6, color=THEME["red"]),
            hovertemplate="<b>%{x}</b><br>Cancellation Rate: %{y:.1f}%<extra></extra>",
        )
    )

    fig.add_hline(
        y=avg_cancel,
        line_dash="dash",
        line_color=THEME["muted"],
        annotation_text=f"Avg: {avg_cancel:.1f}%",
        annotation_position="bottom right",
    )

    fig.update_layout(
        xaxis=dict(tickangle=-45, gridcolor=THEME["grid"]),
        yaxis=dict(title=dict(text="Cancellation Rate (%)", font=dict(size=11, color=THEME["muted"])), gridcolor=THEME["grid"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=10)),
    )
    return _apply_standard_layout(fig, "Monthly Order Cancellation Rate Trajectory (%)", height=380)
