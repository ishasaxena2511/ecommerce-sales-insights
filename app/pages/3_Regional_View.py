"""Regional Geo-Spatial & Territory Performance — E-Commerce Sales BI Platform.

Focuses on India-wide geographic sales distribution, state-level revenue and profit,
and regional category margin heatmaps.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# Configure wide page layout
st.set_page_config(
    page_title="Regional Performance | E-Commerce Sales BI",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Resolve repo root and register in sys.path
PAGES_DIR: Path = Path(__file__).resolve().parent
APP_DIR: Path = PAGES_DIR.parent
REPO_ROOT: Path = APP_DIR.parent
for _p in [str(REPO_ROOT), str(APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Import chart and filter utilities
try:
    from utils.charts import (
        THEME,
        create_india_geo_bubble_map,
        create_region_category_margin_heatmap,
        create_state_sales_profit_chart,
        render_takeaway,
    )
    from utils.filters import render_sidebar_filters
except (ModuleNotFoundError, ImportError):
    from app.utils.charts import (
        THEME,
        create_india_geo_bubble_map,
        create_region_category_margin_heatmap,
        create_state_sales_profit_chart,
        render_takeaway,
    )
    from app.utils.filters import render_sidebar_filters

from src.metrics import (
    completed_orders,
    format_inr,
    group_summary,
    kpi_summary,
)


@st.cache_data
def load_clean_dataset() -> pd.DataFrame:
    """Loads and caches the cleaned sales dataset."""
    data_path = REPO_ROOT / "data" / "processed" / "ecommerce_sales_clean.csv"
    if not data_path.exists():
        st.error(f"Processed dataset not found at `{data_path}`. Run `python src/clean_data.py` first.")
        st.stop()
    df = pd.read_csv(data_path)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


@st.cache_data
def load_city_coordinates() -> pd.DataFrame:
    """Loads geospatial coordinates for Indian cities."""
    coords_path = REPO_ROOT / "data" / "raw" / "city_coordinates.csv"
    if not coords_path.exists():
        st.error(f"Coordinates dataset not found at `{coords_path}`.")
        st.stop()
    return pd.read_csv(coords_path)


def main() -> None:
    raw_df = load_clean_dataset()
    coords_df = load_city_coordinates()

    # Sidebar global filters
    filtered_df = render_sidebar_filters(raw_df)
    comp_df = completed_orders(filtered_df)

    # Executive Banner
    st.markdown(
        """<div class="page-header">
<h1 class="page-header-title" style="color: #FFFFFF !important; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 6px 0;"><span style="color: #FFFFFF !important;">Regional Geo-Spatial &amp; Territory View</span></h1>
<p class="page-header-subtitle" style="color: #CBD5E1 !important; margin: 0; font-size: 0.88rem;">Geographic footprint across India, city tier performance, state revenue vs profit contribution, and regional category margin heatmaps.</p>
</div>""",
        unsafe_allow_html=True,
    )

    if comp_df.empty:
        st.warning("⚠️ No completed orders match current filter criteria to evaluate regional distribution.")
        st.stop()

    # Regional top-level summary metrics
    reg_summary = group_summary(filtered_df, by="region")
    top_reg = reg_summary.iloc[0] if not reg_summary.empty else None
    top_margin_reg = reg_summary.sort_values(by="margin_pct", ascending=False).iloc[0] if not reg_summary.empty else None

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Active City Hubs", f"{comp_df['city'].nunique()} Cities")
    with k2:
        st.metric("Active States / UTs", f"{comp_df['state'].nunique()} States")
    with k3:
        if top_reg is not None:
            st.metric("Top Revenue Region", f"{top_reg['region']}", f"{top_reg['sales_contribution_pct']:.1f}% Share")
    with k4:
        if top_margin_reg is not None:
            st.metric("Top Margin Region", f"{top_margin_reg['region']}", f"{top_margin_reg['margin_pct']:.1f}% Margin")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Section 1: India Geo-Spatial Bubble Map
    # -------------------------------------------------------------------------
    with st.container(border=True):
        city_agg = (
            comp_df.groupby("city")
            .agg(
                sales_amount=("sales_amount", "sum"),
                profit_amount=("profit_amount", "sum"),
                orders=("order_id", "nunique"),
            )
            .reset_index()
        )
        city_agg["profit_margin_pct"] = np.where(
            city_agg["sales_amount"] > 0,
            (city_agg["profit_amount"] / city_agg["sales_amount"] * 100.0).round(2),
            0.0,
        )

        fig_map = create_india_geo_bubble_map(city_agg, coords_df)
        st.plotly_chart(fig_map, use_container_width=True)

        # Dynamic Takeaway for Bubble Map
        merged_cities = city_agg.merge(coords_df, left_on="city", right_on="City", how="inner")
        if not merged_cities.empty:
            top_city = merged_cities.sort_values(by="sales_amount", ascending=False).iloc[0]
            # City with highest margin that had at least median sales
            med_sales = merged_cities["sales_amount"].median()
            qualified_cities = merged_cities[merged_cities["sales_amount"] >= med_sales]
            best_margin_city = (
                qualified_cities.sort_values(by="profit_margin_pct", ascending=False).iloc[0]
                if not qualified_cities.empty
                else merged_cities.sort_values(by="profit_margin_pct", ascending=False).iloc[0]
            )

            map_takeaway = (
                f"<strong>{top_city['city']}</strong> leads urban commerce with {format_inr(top_city['sales_amount'])} "
                f"across {top_city['orders']} orders ({top_city['profit_margin_pct']:.1f}% margin), while "
                f"<strong>{best_margin_city['city']}</strong> yields peak realized margin at "
                f"{best_margin_city['profit_margin_pct']:.1f}% ({format_inr(best_margin_city['sales_amount'])} sales)."
            )
            render_takeaway(map_takeaway)

    # -------------------------------------------------------------------------
    # Section 2: State-wise Bars & Regional Margin Heatmap
    # -------------------------------------------------------------------------
    col1, col2 = st.columns([1.15, 1.25])

    with col1:
        with st.container(border=True):
            state_df = group_summary(filtered_df, by="state")
            fig_state = create_state_sales_profit_chart(state_df, top_n_states=12)
            st.plotly_chart(fig_state, use_container_width=True)

            # Dynamic Takeaway for State Bars
            if not state_df.empty:
                top_st = state_df.sort_values(by="sales", ascending=False).iloc[0]
                top_prof_st = state_df.sort_values(by="profit", ascending=False).iloc[0]
                state_takeaway = (
                    f"<strong>{top_st['state']}</strong> generates the highest sales volume at {format_inr(top_st['sales'])} "
                    f"({top_st['sales_contribution_pct']:.1f}% share), and <strong>{top_prof_st['state']}</strong> delivers "
                    f"the largest gross profit of {format_inr(top_prof_st['profit'])} ({top_prof_st['margin_pct']:.1f}% margin)."
                )
                render_takeaway(state_takeaway)

    with col2:
        with st.container(border=True):
            fig_heatmap = create_region_category_margin_heatmap(comp_df)
            st.plotly_chart(fig_heatmap, use_container_width=True)

            # Dynamic Takeaway for Heatmap
            pivot_tbl = comp_df.pivot_table(
                index="region",
                columns="product_category",
                values=["sales_amount", "profit_amount"],
                aggfunc="sum",
            )
            if not pivot_tbl.empty and "profit_amount" in pivot_tbl and "sales_amount" in pivot_tbl:
                m_matrix = (pivot_tbl["profit_amount"] / pivot_tbl["sales_amount"] * 100.0).round(1)
                # Find max and min cells
                stacked = m_matrix.stack()
                if not stacked.empty:
                    max_cell = stacked.idxmax()
                    max_val = stacked.max()
                    min_cell = stacked.idxmin()
                    min_val = stacked.min()
                    heatmap_takeaway = (
                        f"Peak regional profitability occurs in <strong>{max_cell[1]}</strong> in the "
                        f"<strong>{max_cell[0]}</strong> region ({max_val:.1f}% margin), whereas "
                        f"<strong>{min_cell[1]}</strong> in <strong>{min_cell[0]}</strong> yields the lowest "
                        f"margin at {min_val:.1f}%."
                    )
                    render_takeaway(heatmap_takeaway)


if __name__ == "__main__":
    main()
