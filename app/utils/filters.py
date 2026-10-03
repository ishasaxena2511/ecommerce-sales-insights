"""Sidebar Filtering Module for E-Commerce BI Dashboard.

Provides consistent global filters across all dashboard pages:
- Date Range (Min / Max with reset)
- Region (Multi-select)
- Product Category (Multi-select)
- Customer Segment (Multi-select)
- Payment Method (Multi-select)
- Reset button restoring default full dataset selection
- Friendly empty-state handler preventing crashes
"""

from __future__ import annotations

from typing import List, Tuple
import pandas as pd
import streamlit as st

try:
    from utils.charts import apply_theme, is_dark_mode, render_theme_toggle_button
except (ModuleNotFoundError, ImportError):
    from app.utils.charts import apply_theme, is_dark_mode, render_theme_toggle_button


def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Renders standardized sidebar filters and returns the filtered DataFrame.

    If the resulting filtered dataset is empty, displays a user-friendly warning
    and gracefully halts further page execution via st.stop().

    Args:
        df: Input cleaned sales DataFrame.

    Returns:
        Filtered DataFrame according to user selection.
    """
    # 0. Enforce active theme styles
    apply_theme()

    # 1. Mount Small Theme Toggle Icon Button in the Top-Right Corner
    render_theme_toggle_button()

    # 2. Sidebar Header: Filters & Controls
    dark = is_dark_mode()
    header_color = "#F8FAFC" if dark else "#0B2545"
    sub_color = "#94A3B8" if dark else "#64748B"
    border_color = "#334155" if dark else "#E5E7EB"

    st.sidebar.markdown(
        f"""
        <div style="padding-bottom: 10px; border-bottom: 1px solid {border_color}; margin-bottom: 14px;">
            <h3 style="margin: 0; color: {header_color}; font-size: 1.15rem; font-weight: 700;">Filters &amp; Controls</h3>
            <span style="font-size: 0.8rem; color: {sub_color};">Slice metrics across dimensions</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Reset button
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True, type="secondary"):
        for key in [
            "sb_date_range",
            "sb_regions",
            "sb_categories",
            "sb_segments",
            "sb_payments",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # 1. Date Range Filter
    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()

    date_selection = st.sidebar.date_input(
        "📅 Date Range",
        value=st.session_state.get("sb_date_range", (min_date, max_date)),
        min_value=min_date,
        max_value=max_date,
        key="sb_date_range",
    )

    if isinstance(date_selection, (tuple, list)) and len(date_selection) == 2:
        start_date, end_date = date_selection
    elif isinstance(date_selection, (tuple, list)) and len(date_selection) == 1:
        start_date = date_selection[0]
        end_date = max_date
    else:
        start_date, end_date = min_date, max_date

    # Persist in session state for cross-period analysis
    st.session_state["filter_start_date"] = pd.to_datetime(start_date)
    st.session_state["filter_end_date"] = pd.to_datetime(end_date)

    # 2. Region Filter (Multi-select)
    all_regions = sorted(df["region"].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect(
        "📍 Region",
        options=all_regions,
        default=st.session_state.get("sb_regions", []),
        placeholder="All Regions",
        key="sb_regions",
    )

    # 3. Product Category Filter (Multi-select)
    all_categories = sorted(df["product_category"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect(
        "🏷️ Product Category",
        options=all_categories,
        default=st.session_state.get("sb_categories", []),
        placeholder="All Categories",
        key="sb_categories",
    )

    # 4. Customer Segment Filter (Multi-select)
    all_segments = sorted(df["customer_segment"].dropna().unique().tolist())
    selected_segments = st.sidebar.multiselect(
        "👥 Customer Segment",
        options=all_segments,
        default=st.session_state.get("sb_segments", []),
        placeholder="All Segments",
        key="sb_segments",
    )

    # 5. Payment Method Filter (Multi-select)
    all_payments = sorted(df["payment_method"].dropna().unique().tolist())
    selected_payments = st.sidebar.multiselect(
        "💳 Payment Method",
        options=all_payments,
        default=st.session_state.get("sb_payments", []),
        placeholder="All Payment Methods",
        key="sb_payments",
    )

    # Apply Filtering
    filtered_df = df.copy()

    # Apply date range
    filtered_df = filtered_df[
        (filtered_df["order_date"].dt.date >= start_date)
        & (filtered_df["order_date"].dt.date <= end_date)
    ]

    # Apply dimension selections (empty selection implies 'All')
    if selected_regions:
        filtered_df = filtered_df[filtered_df["region"].isin(selected_regions)]

    if selected_categories:
        filtered_df = filtered_df[filtered_df["product_category"].isin(selected_categories)]

    if selected_segments:
        filtered_df = filtered_df[filtered_df["customer_segment"].isin(selected_segments)]

    if selected_payments:
        filtered_df = filtered_df[filtered_df["payment_method"].isin(selected_payments)]

    # Sidebar Data Status Summary
    summary_bg = "#0F172A" if dark else "#F8FAFC"
    summary_border = "#334155" if dark else "#E2E8F0"
    summary_text = "#94A3B8" if dark else "#475569"
    strong_color = "#F8FAFC" if dark else "#1E293B"

    st.sidebar.markdown(
        f"""
        <div style="margin-top: 24px; padding: 10px 14px; background-color: {summary_bg}; border-radius: 8px; border: 1px solid {summary_border}; font-size: 0.8rem; color: {summary_text};">
            <strong style="color: {strong_color};">Filtered Rows:</strong> {len(filtered_df):,} of {len(df):,}<br>
            <strong style="color: {strong_color};">Date Span:</strong> {start_date} to {end_date}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Graceful Empty Selection Handling
    if filtered_df.empty:
        st.warning(
            "⚠️ **No records match your selected filter criteria.**  \n"
            "Please broaden your date range or clear specific filters in the left sidebar to resume viewing insights."
        )
        st.stop()

    return filtered_df
