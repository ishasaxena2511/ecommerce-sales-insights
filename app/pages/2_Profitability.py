"""Profitability & Margin Architecture — E-Commerce Sales BI Platform.

Focuses on category profitability, product hierarchy margins, discount elasticity,
and loss-making SKU diagnostics.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

# Configure wide page layout
st.set_page_config(
    page_title="Profitability & Margins | E-Commerce Sales BI",
    page_icon="💹",
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
        create_category_profit_bar,
        create_category_product_treemap,
        create_discount_band_chart,
        create_discount_scatter_chart,
        render_takeaway,
    )
    from utils.filters import render_sidebar_filters
except (ModuleNotFoundError, ImportError):
    from app.utils.charts import (
        THEME,
        create_category_profit_bar,
        create_category_product_treemap,
        create_discount_band_chart,
        create_discount_scatter_chart,
        render_takeaway,
    )
    from app.utils.filters import render_sidebar_filters

from src.metrics import (
    completed_orders,
    discount_band_analysis,
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


def main() -> None:
    raw_df = load_clean_dataset()

    # Sidebar global filters
    filtered_df = render_sidebar_filters(raw_df)
    comp_df = completed_orders(filtered_df)

    # Executive Banner
    st.markdown(
        """<div class="page-header">
<h1 class="page-header-title" style="color: #FFFFFF !important; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 6px 0;"><span style="color: #FFFFFF !important;">Profitability &amp; Margin Architecture</span></h1>
<p class="page-header-subtitle" style="color: #CBD5E1 !important; margin: 0; font-size: 0.88rem;">Category profit generation, product hierarchy margin mapping, promotional discount erosion, and loss-making SKU management.</p>
</div>""",
        unsafe_allow_html=True,
    )

    if comp_df.empty:
        st.warning("⚠️ No completed orders match current filter criteria to evaluate realized profitability.")
        st.stop()

    # Top mini KPI strip
    kpis = kpi_summary(filtered_df)
    loss_orders_cnt = int((comp_df["profit_amount"] < 0).sum())
    loss_amount_sum = float(abs(comp_df[comp_df["profit_amount"] < 0]["profit_amount"].sum()))

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total Gross Profit", format_inr(kpis["total_profit"]))
    with k2:
        st.metric("Realized Sales", format_inr(kpis["total_sales"]))
    with k3:
        st.metric("Overall Profit Margin", f"{kpis['margin_pct']:.1f}%")
    with k4:
        st.metric("Loss-Making Orders", f"{loss_orders_cnt:,}", f"-{format_inr(loss_amount_sum)}", delta_color="inverse")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Section 1: Category & Product Hierarchy Profit Dynamics
    # -------------------------------------------------------------------------
    col1, col2 = st.columns([1.1, 1.3])

    with col1:
        with st.container(border=True):
            cat_df = group_summary(filtered_df, by="product_category")
            fig_cat_profit = create_category_profit_bar(cat_df)
            st.plotly_chart(fig_cat_profit, use_container_width=True)

            # Dynamic Takeaway for Category Profit Bar
            if not cat_df.empty:
                cat_sorted = cat_df.sort_values(by="profit", ascending=False)
                top_cat = cat_sorted.iloc[0]
                bot_cat = cat_sorted.iloc[-1]
                cat_takeaway = (
                    f"<strong>{top_cat['product_category']}</strong> delivers the highest gross profit at "
                    f"{format_inr(top_cat['profit'])} ({top_cat['margin_pct']:.1f}% margin), while "
                    f"<strong>{bot_cat['product_category']}</strong> generates the lowest profit at "
                    f"{format_inr(bot_cat['profit'])} ({bot_cat['margin_pct']:.1f}% margin)."
                )
                render_takeaway(cat_takeaway)

    with col2:
        with st.container(border=True):
            fig_treemap = create_category_product_treemap(comp_df)
            st.plotly_chart(fig_treemap, use_container_width=True)

            # Dynamic Takeaway for Treemap
            prod_agg = (
                comp_df.groupby(["product_category", "product_name"])
                .agg(sales=("sales_amount", "sum"), profit=("profit_amount", "sum"))
                .reset_index()
            )
            if not prod_agg.empty:
                prod_agg["margin_pct"] = np.where(
                    prod_agg["sales"] > 0,
                    (prod_agg["profit"] / prod_agg["sales"] * 100.0).round(1),
                    0.0,
                )
                top_sales_p = prod_agg.sort_values(by="sales", ascending=False).iloc[0]
                high_vol = prod_agg[prod_agg["sales"] >= prod_agg["sales"].median()]
                top_margin_p = (
                    high_vol.sort_values(by="margin_pct", ascending=False).iloc[0]
                    if not high_vol.empty
                    else prod_agg.sort_values(by="margin_pct", ascending=False).iloc[0]
                )
                treemap_takeaway = (
                    f"Sales volume concentrates heavily in <strong>{top_sales_p['product_name']}</strong> "
                    f"({format_inr(top_sales_p['sales'])}, {top_sales_p['margin_pct']:.1f}% margin), while "
                    f"<strong>{top_margin_p['product_name']}</strong> achieves peak profitability at "
                    f"{top_margin_p['margin_pct']:.1f}% margin."
                )
                render_takeaway(treemap_takeaway)

    # -------------------------------------------------------------------------
    # Section 2: Promotional Discount Elasticity & Erosion
    # -------------------------------------------------------------------------
    col3, col4 = st.columns([1.1, 1.3])

    with col3:
        with st.container(border=True):
            disc_df = discount_band_analysis(filtered_df)
            fig_disc = create_discount_band_chart(disc_df)
            st.plotly_chart(fig_disc, use_container_width=True)

            # Dynamic Takeaway for Discount Band
            if not disc_df.empty:
                zero_band = disc_df.loc[disc_df["discount_band"].astype(str) == "0%", "margin_pct"].values
                deep_band = disc_df.loc[disc_df["discount_band"].astype(str) == "30%+", "margin_pct"].values
                zero_m = zero_band[0] if len(zero_band) > 0 else 0.0
                deep_m = deep_band[0] if len(deep_band) > 0 else 0.0
                is_deep_neg = deep_m < 0
                disc_takeaway = (
                    f"Gross margin degrades precipitously from {zero_m:.1f}% on zero-discount orders down to "
                    f"{deep_m:.1f}% on deep promotions (30%+ discount), confirming severe margin sensitivity."
                )
                render_takeaway(disc_takeaway, is_alert=is_deep_neg)

    with col4:
        with st.container(border=True):
            fig_scatter = create_discount_scatter_chart(comp_df)
            st.plotly_chart(fig_scatter, use_container_width=True)

            # Dynamic Takeaway for Scatter
            corr = float(comp_df["discount_percent"].corr(comp_df["profit_margin_pct"]))
            neg_count = int((comp_df["profit_margin_pct"] < 0).sum())
            neg_share = (neg_count / len(comp_df) * 100.0) if len(comp_df) > 0 else 0.0
            scatter_takeaway = (
                f"Strong negative correlation (r = {corr:.2f}): {neg_count} completed orders "
                f"({neg_share:.1f}% of volume) suffered negative margins, heavily clustering above 20% discount."
            )
            render_takeaway(scatter_takeaway, is_alert=(neg_count > 0))

    # -------------------------------------------------------------------------
    # Section 3: Loss-Making & Lowest-Margin Products Table
    # -------------------------------------------------------------------------
    with st.container(border=True):
        st.markdown('<h4 class="card-title">Loss-Making & Lowest-Margin Products Watchlist</h4>', unsafe_allow_html=True)

        prod_summary = (
            comp_df.groupby(["product_name", "product_category"])
            .agg(
                sales=("sales_amount", "sum"),
                profit=("profit_amount", "sum"),
                units=("quantity_sold", "sum"),
                orders=("order_id", "nunique"),
                avg_discount=("discount_percent", "mean"),
            )
            .reset_index()
        )
        prod_summary["margin_pct"] = np.where(
            prod_summary["sales"] > 0,
            (prod_summary["profit"] / prod_summary["sales"] * 100.0).round(2),
            0.0,
        )

        # Filter for loss-making and lowest margin (sorted by profit_margin_pct ascending)
        loss_and_low = prod_summary.sort_values(by=["profit", "margin_pct"], ascending=[True, True]).head(12).copy()

        # Dynamic status classification
        def _status_badge(row: pd.Series) -> str:
            if row["profit"] < 0:
                return "🔴 Loss-Making"
            elif row["margin_pct"] < 10.0:
                return "🟡 Low Margin (<10%)"
            return "🟢 Thin Margin"

        loss_and_low["status"] = loss_and_low.apply(_status_badge, axis=1)

        # Format table columns
        display_tbl = loss_and_low[
            ["product_name", "product_category", "status", "units", "orders", "sales", "profit", "margin_pct", "avg_discount"]
        ].copy()

        display_tbl["sales"] = display_tbl["sales"].apply(format_inr)
        display_tbl["profit"] = display_tbl["profit"].apply(format_inr)
        display_tbl["margin_pct"] = display_tbl["margin_pct"].apply(lambda m: f"{m:.2f}%")
        display_tbl["avg_discount"] = display_tbl["avg_discount"].apply(lambda d: f"{d:.1f}%")

        display_tbl.columns = [
            "Product Name",
            "Category",
            "Risk Status",
            "Units Sold",
            "Orders",
            "Sales Revenue",
            "Gross Profit",
            "Profit Margin",
            "Avg Discount",
        ]

        st.dataframe(display_tbl, use_container_width=True, hide_index=True, height=330)

        # Dynamic Takeaway for Watchlist Table
        loss_skus = int((prod_summary["profit"] < 0).sum())
        total_sku_loss = float(abs(prod_summary[prod_summary["profit"] < 0]["profit"].sum())) if loss_skus > 0 else 0.0
        worst_sku = prod_summary.sort_values(by="profit").iloc[0]

        table_takeaway = (
            f"{loss_skus} distinct product(s) operated at a net loss (total gross loss of {format_inr(total_sku_loss)}), "
            f"led by <strong>{worst_sku['product_name']}</strong> with {format_inr(worst_sku['profit'])} profit "
            f"({worst_sku['margin_pct']:.1f}% margin, {worst_sku['avg_discount']:.1f}% avg discount)."
        )
        render_takeaway(table_takeaway, is_alert=(loss_skus > 0))


if __name__ == "__main__":
    main()
