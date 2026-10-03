"""Unit tests for Light and Dark theme modes."""

from __future__ import annotations

import plotly.graph_objects as go
import pytest
import streamlit as st

from app.utils.charts import (
    THEME,
    THEME_DARK,
    THEME_LIGHT,
    _apply_standard_layout,
    get_theme_css,
    is_dark_mode,
)


def test_theme_keys_present():
    """Ensures all essential corporate palette keys exist in light and dark themes."""
    essential_keys = ["navy", "blue", "teal", "amber", "red", "green", "bg", "card", "text", "muted", "grid"]
    for k in essential_keys:
        assert k in THEME_LIGHT, f"Missing {k} in THEME_LIGHT"
        assert k in THEME_DARK, f"Missing {k} in THEME_DARK"
        assert k in THEME, f"Missing {k} in THEME proxy"


def test_light_mode_defaults():
    """Validates default light mode color resolution."""
    st.session_state["theme_mode"] = "light"
    assert not is_dark_mode()
    assert THEME["bg"] == "#F5F7FA"
    assert THEME["card"] == "#FFFFFF"
    assert THEME["text"] == "#0B2545"

    css = get_theme_css()
    assert "#F5F7FA" in css
    assert "background-color: #F5F7FA" in css


def test_dark_mode_resolution():
    """Validates dynamic color resolution and CSS generation when switching to dark mode."""
    st.session_state["theme_mode"] = "dark"
    assert is_dark_mode()
    assert THEME["bg"] == "#0F172A"
    assert THEME["card"] == "#1E293B"
    assert THEME["text"] == "#F8FAFC"
    assert THEME["teal"] == "#2DD4BF"

    css = get_theme_css()
    assert "#0F172A" in css
    assert "#1E293B" in css
    assert "background-color: #0F172A" in css


def test_chart_layout_adapts_to_theme():
    """Verifies that _apply_standard_layout sets background and font colors according to theme."""
    # Test Dark Mode Layout
    st.session_state["theme_mode"] = "dark"
    fig = go.Figure()
    fig = _apply_standard_layout(fig, "Test Dark Chart")
    assert fig.layout.plot_bgcolor == "#1E293B"
    assert fig.layout.paper_bgcolor == "#1E293B"
    assert fig.layout.font.color == "#F8FAFC"

    # Test Light Mode Layout
    st.session_state["theme_mode"] = "light"
    fig_light = go.Figure()
    fig_light = _apply_standard_layout(fig_light, "Test Light Chart")
    assert fig_light.layout.plot_bgcolor == "#FFFFFF"
    assert fig_light.layout.paper_bgcolor == "#FFFFFF"
    assert fig_light.layout.font.color == "#0B2545"


def test_sidebar_nav_and_icon_button_css():
    """Ensures navigation links and top-right icon button are styled for light and dark modes."""
    # Light Mode checks
    st.session_state["theme_mode"] = "light"
    light_css = get_theme_css()
    assert '[data-testid="stSidebarNav"]' in light_css
    assert "color: #0B2545 !important;" in light_css  # High contrast text for nav links
    assert "#theme-toggle-anchor" in light_css
    assert "position: fixed !important;" in light_css  # Top-right floating icon button

    # Dark Mode checks
    st.session_state["theme_mode"] = "dark"
    dark_css = get_theme_css()
    assert '[data-testid="stSidebarNav"]' in dark_css
    assert "color: #CBD5E1 !important;" in dark_css
    assert "background-color: #1E293B !important;" in dark_css
