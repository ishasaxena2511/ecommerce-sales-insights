"""Executive Overview — E-Commerce Sales BI Platform.

Main Streamlit Application Page.
Theme:
- Navy #0B2545 (headers / accents)
- Blue #13315C
- Teal #1B998B (primary accent & KPI top borders)
- Background #F5F7FA
- White Cards #FFFFFF with soft shadows
- Inter / system sans-serif typography

Conventions:
- All business numbers computed via src/metrics.py only (zero duplicated calculations in UI).
- Realized revenue & margins computed strictly over Completed orders.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import streamlit as st

# Configure wide responsive page layout
st.set_page_config(
    page_title="Executive Overview | E-Commerce Sales BI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Resolve repo root and app dir, register in sys.path
APP_DIR: Path = Path(__file__).resolve().parent
REPO_ROOT: Path = APP_DIR.parent
for _p in [str(REPO_ROOT), str(APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Domain metrics and chart helpers
try:
    from utils.charts import (
        apply_theme,
        create_category_bar_chart,
        create_monthly_trend_chart,
        create_region_donut_chart,
        create_top_products_chart,
        get_theme_css,
    )
    from utils.filters import render_sidebar_filters
except (ModuleNotFoundError, ImportError):
    from app.utils.charts import (
        apply_theme,
        create_category_bar_chart,
        create_monthly_trend_chart,
        create_region_donut_chart,
        create_top_products_chart,
        get_theme_css,
    )
    from app.utils.filters import render_sidebar_filters
from src.metrics import (
    completed_orders,
    customer_summary,
    format_inr,
    group_summary,
    kpi_summary,
    monthly_trend,
    period_comparison,
    top_n,
)

# -----------------------------------------------------------------------------
# Dynamic Corporate Theme CSS Injection
# -----------------------------------------------------------------------------
apply_theme()


# -----------------------------------------------------------------------------
# Data Ingestion Cache
# -----------------------------------------------------------------------------
@st.cache_data
def load_clean_dataset() -> pd.DataFrame:
    """Loads and caches the production-cleaned e-commerce dataset."""
    data_path = REPO_ROOT / "data" / "processed" / "ecommerce_sales_clean.csv"
    if not data_path.exists():
        st.error(f"Processed dataset not found at `{data_path}`. Run `python src/clean_data.py` first.")
        st.stop()
    df = pd.read_csv(data_path)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def render_kpi(
    label: str,
    value: str,
    delta: Optional[float] = None,
    delta_suffix: str = "% vs prev period",
    is_percentage_points: bool = False,
) -> None:
    """Renders a white rounded KPI card with a teal top border and colored delta badge."""
    if delta is not None:
        sign = "+" if delta > 0 else ""
        pts = " pts" if is_percentage_points else ""
        delta_str = f"{sign}{delta:.1f}{pts} {delta_suffix}"
        if delta > 0:
            delta_html = f'<div class="kpi-delta-pos">▲ {delta_str}</div>'
        elif delta < 0:
            delta_html = f'<div class="kpi-delta-neg">▼ {delta_str}</div>'
        else:
            delta_html = f'<div class="kpi-delta-neutral">● {delta_str}</div>'
    else:
        delta_html = '<div class="kpi-delta-neutral">— Baseline window</div>'

    html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Main Application Flow
# -----------------------------------------------------------------------------
def main() -> None:
    # Ingest data
    raw_df = load_clean_dataset()

    # Render Left Sidebar Filters
    filtered_df = render_sidebar_filters(raw_df)

    # Resolve date boundaries for period comparison
    start_dt = st.session_state.get("filter_start_date", filtered_df["order_date"].min())
    end_dt = st.session_state.get("filter_end_date", filtered_df["order_date"].max())

    # Executive Title Banner
    st.markdown(
        """<div class="exec-header">
<h1 class="exec-header-title" style="color: #FFFFFF !important; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 6px 0;"><span style="color: #FFFFFF !important;">Executive Sales Intelligence Overview</span></h1>
<p class="exec-header-subtitle" style="color: #CBD5E1 !important; margin: 0; font-size: 0.88rem;">Company-style business intelligence monitoring revenue trajectory, margins, fulfillment reliability, and customer retention.</p>
</div>""",
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # TOP SECTION: 5 KPI CARDS
    # -------------------------------------------------------------------------
    kpis = kpi_summary(filtered_df)

    # Compute period comparison vs preceding equal-length period
    try:
        p_comp = period_comparison(filtered_df, start=start_dt, end=end_dt)
        deltas = p_comp["deltas"]
    except Exception:
        deltas = {
            "sales_growth_pct": None,
            "profit_growth_pct": None,
            "orders_growth_pct": None,
            "aov_growth_pct": None,
            "margin_delta_pct": None,
        }

    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

    with kpi_col1:
        render_kpi(
            label="Total Realized Sales",
            value=format_inr(kpis["total_sales"]),
            delta=deltas["sales_growth_pct"],
        )

    with kpi_col2:
        render_kpi(
            label="Total Gross Profit",
            value=format_inr(kpis["total_profit"]),
            delta=deltas["profit_growth_pct"],
        )

    with kpi_col3:
        render_kpi(
            label="Completed Orders",
            value=f"{kpis['total_orders']:,}",
            delta=deltas["orders_growth_pct"],
        )

    with kpi_col4:
        render_kpi(
            label="Average Order Value",
            value=format_inr(kpis["aov"]),
            delta=deltas["aov_growth_pct"],
        )

    with kpi_col5:
        render_kpi(
            label="Gross Profit Margin",
            value=f"{kpis['margin_pct']:.1f}%",
            delta=deltas["margin_delta_pct"],
            is_percentage_points=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # MIDDLE SECTION (3 COLUMNS)
    # -------------------------------------------------------------------------
    mid_col1, mid_col2, mid_col3 = st.columns([1.5, 1.2, 1.0])

    with mid_col1:
        with st.container(border=True):
            trend_df = monthly_trend(filtered_df)
            fig_trend = create_monthly_trend_chart(trend_df)
            st.plotly_chart(fig_trend, use_container_width=True)

    with mid_col2:
        with st.container(border=True):
            cat_df = group_summary(filtered_df, by="product_category")
            fig_cat = create_category_bar_chart(cat_df)
            st.plotly_chart(fig_cat, use_container_width=True)

    with mid_col3:
        with st.container(border=True):
            reg_df = group_summary(filtered_df, by="region")
            fig_reg = create_region_donut_chart(reg_df)
            st.plotly_chart(fig_reg, use_container_width=True)

    # -------------------------------------------------------------------------
    # BOTTOM SECTION (2 COLUMNS)
    # -------------------------------------------------------------------------
    bot_col1, bot_col2 = st.columns([1.2, 1.0])

    with bot_col1:
        with st.container(border=True):
            st.markdown('<h4 class="section-title">Top 10 VIP Customers</h4>', unsafe_allow_html=True)

            cust_df = customer_summary(filtered_df).head(10)
            if not cust_df.empty:
                display_cust = cust_df[
                    ["customer_id", "customer_name", "total_spend", "orders", "aov", "contribution_pct", "tier"]
                ].copy()

                display_cust["total_spend"] = display_cust["total_spend"].apply(format_inr)
                display_cust["aov"] = display_cust["aov"].apply(lambda v: f"₹{v:,.2f}")
                display_cust["contribution_pct"] = display_cust["contribution_pct"].apply(lambda p: f"{p:.2f}%")

                display_cust.columns = [
                    "Customer ID",
                    "Customer Name",
                    "Total Spend",
                    "Orders",
                    "AOV",
                    "Share %",
                    "Tier",
                ]
                st.dataframe(
                    display_cust,
                    use_container_width=True,
                    hide_index=True,
                    height=350,
                )
            else:
                st.info("No customer data available for current selection.")

    with bot_col2:
        with st.container(border=True):
            top_products = top_n(filtered_df, by="product_name", metric="sales", n=10)
            fig_prods = create_top_products_chart(top_products)
            st.plotly_chart(fig_prods, use_container_width=True)


if __name__ == "__main__":
    main()
