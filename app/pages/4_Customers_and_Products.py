"""Customer Intelligence & Product Portfolio — E-Commerce Sales BI Platform.

Focuses on customer segments, 80/20 Pareto spend curve, top VIP clients,
best-selling products by volume/value, low-performing categories,
and interactive product order drill-through with CSV download.
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
    page_title="Customers & Products | E-Commerce Sales BI",
    page_icon="🛍️",
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
        create_bestselling_products_chart,
        create_customer_pareto_chart,
        create_product_contribution_chart,
        create_segment_analysis_chart,
        render_takeaway,
    )
    from utils.filters import render_sidebar_filters
except (ModuleNotFoundError, ImportError):
    from app.utils.charts import (
        THEME,
        create_bestselling_products_chart,
        create_customer_pareto_chart,
        create_product_contribution_chart,
        create_segment_analysis_chart,
        render_takeaway,
    )
    from app.utils.filters import render_sidebar_filters

from src.metrics import (
    completed_orders,
    customer_summary,
    format_inr,
    group_summary,
    top_n,
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
<h1 class="page-header-title" style="color: #FFFFFF !important; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 6px 0;"><span style="color: #FFFFFF !important;">Customer Intelligence &amp; Product Portfolio</span></h1>
<p class="page-header-subtitle" style="color: #CBD5E1 !important; margin: 0; font-size: 0.88rem;">Segment economics, 80/20 Pareto revenue concentration, top VIP accounts, bestseller volume vs revenue, underperforming lines, and order-level drill-through.</p>
</div>""",
        unsafe_allow_html=True,
    )

    if comp_df.empty:
        st.warning("⚠️ No completed orders match current filter criteria to evaluate customers and products.")
        st.stop()

    # Customer Summary metrics
    cust_df = customer_summary(filtered_df)
    total_cust = len(cust_df)
    repeat_cust_cnt = int((cust_df["orders"] > 1).sum())
    repeat_rate = (repeat_cust_cnt / total_cust * 100.0) if total_cust > 0 else 0.0
    total_revenue = comp_df["sales_amount"].sum()
    avg_cust_spend = (total_revenue / total_cust) if total_cust > 0 else 0.0

    # Top 20% customer revenue share
    top_20_count = max(1, int(np.ceil(0.20 * total_cust)))
    top_20_share = cust_df.head(top_20_count)["contribution_pct"].sum()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Active Customer Accounts", f"{total_cust:,}")
    with k2:
        st.metric("Avg Spend per Customer", format_inr(avg_cust_spend))
    with k3:
        st.metric("Repeat Purchase Rate", f"{repeat_rate:.1f}%", f"{repeat_cust_cnt} Repeat Buyers")
    with k4:
        st.metric("Top 20% Customer Share", f"{top_20_share:.1f}%", "Pareto concentration")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Section 1: Customer Segments & Pareto 80/20 Curve
    # -------------------------------------------------------------------------
    col1, col2 = st.columns([1.1, 1.3])

    with col1:
        with st.container(border=True):
            seg_df = group_summary(filtered_df, by="customer_segment")
            # Add AOV to segment df
            seg_df["aov"] = np.where(seg_df["orders"] > 0, (seg_df["sales"] / seg_df["orders"]).round(2), 0.0)

            fig_seg = create_segment_analysis_chart(seg_df)
            st.plotly_chart(fig_seg, use_container_width=True)

            # Dynamic Takeaway for Segments
            if not seg_df.empty:
                top_sales_seg = seg_df.sort_values(by="sales", ascending=False).iloc[0]
                top_aov_seg = seg_df.sort_values(by="aov", ascending=False).iloc[0]
                seg_takeaway = (
                    f"<strong>{top_sales_seg['customer_segment']}</strong> drives the largest sales volume at "
                    f"{format_inr(top_sales_seg['sales'])} ({top_sales_seg['sales_contribution_pct']:.1f}% share), while "
                    f"<strong>{top_aov_seg['customer_segment']}</strong> commands the highest average order size at "
                    f"{format_inr(top_aov_seg['aov'])} AOV."
                )
                render_takeaway(seg_takeaway)

    with col2:
        with st.container(border=True):
            fig_pareto = create_customer_pareto_chart(cust_df)
            st.plotly_chart(fig_pareto, use_container_width=True)

            # Dynamic Takeaway for Pareto Curve
            if not cust_df.empty:
                p_row = cust_df[cust_df["cumulative_pct"] >= 80.0].head(1)
                pct_at_80 = ((p_row.index[0] + 1) / total_cust * 100.0) if not p_row.empty else 20.0
                n_vip = (p_row.index[0] + 1) if not p_row.empty else int(0.2 * total_cust)
                pareto_takeaway = (
                    f"Top {pct_at_80:.1f}% of customer accounts ({n_vip} buyers) account for 80% of total realized sales, "
                    f"evidencing significant revenue concentration in high-value VIP tiers."
                )
                render_takeaway(pareto_takeaway)

    # -------------------------------------------------------------------------
    # Section 2: Top Customer Stratification Table
    # -------------------------------------------------------------------------
    with st.container(border=True):
        st.markdown('<h4 class="card-title">Top 10 High-Value Customers (Tiers & Revenue Contribution)</h4>', unsafe_allow_html=True)

        top_cust_df = cust_df.head(10).copy()
        if not top_cust_df.empty:
            disp_cust = top_cust_df[
                ["customer_id", "customer_name", "tier", "total_spend", "orders", "aov", "contribution_pct", "cumulative_pct"]
            ].copy()

            disp_cust["total_spend"] = display_cust_spend = disp_cust["total_spend"].apply(format_inr)
            disp_cust["aov"] = disp_cust["aov"].apply(lambda v: f"₹{v:,.2f}")
            disp_cust["contribution_pct"] = disp_cust["contribution_pct"].apply(lambda p: f"{p:.2f}%")
            disp_cust["cumulative_pct"] = disp_cust["cumulative_pct"].apply(lambda p: f"{p:.2f}%")

            disp_cust.columns = [
                "Customer ID",
                "Customer Name",
                "Tier",
                "Lifetime Spend",
                "Orders",
                "AOV",
                "Revenue Share %",
                "Cumulative Share %",
            ]
            st.dataframe(disp_cust, use_container_width=True, hide_index=True, height=330)

            # Dynamic Takeaway for Top Customers
            top_1 = cust_df.iloc[0]
            plat_spend = cust_df[cust_df["tier"] == "Platinum"]["total_spend"].sum()
            plat_share = (plat_spend / total_revenue * 100.0) if total_revenue > 0 else 0.0
            top_c_takeaway = (
                f"Top customer <strong>{top_1['customer_name']}</strong> ({top_1['customer_id']}) contributed "
                f"{format_inr(top_1['total_spend'])} across {top_1['orders']} orders; Platinum-tier accounts "
                f"collectively represent {plat_share:.1f}% of total business revenue."
            )
            render_takeaway(top_c_takeaway)

    # -------------------------------------------------------------------------
    # Section 3: Product Portfolio Bestsellers & Underperformers
    # -------------------------------------------------------------------------
    col3, col4 = st.columns([1.2, 1.2])

    with col3:
        with st.container(border=True):
            metric_choice = st.radio("Rank Bestsellers by:", ["Units Sold", "Sales Revenue"], horizontal=True, label_visibility="collapsed")
            rank_metric = "units" if metric_choice == "Units Sold" else "sales"
            prod_ranked = top_n(filtered_df, by="product_name", metric=rank_metric, n=10)

            fig_bestsellers = create_bestselling_products_chart(prod_ranked, metric=rank_metric)
            st.plotly_chart(fig_bestsellers, use_container_width=True)

            # Dynamic Takeaway for Bestsellers
            top_unit_p = top_n(filtered_df, by="product_name", metric="units", n=1).iloc[0]
            top_sales_p = top_n(filtered_df, by="product_name", metric="sales", n=1).iloc[0]
            bs_takeaway = (
                f"<strong>{top_unit_p['product_name']}</strong> is the top volume mover ({top_unit_p['units']:,} units), "
                f"whereas <strong>{top_sales_p['product_name']}</strong> generates highest cash revenue at "
                f"{format_inr(top_sales_p['sales'])}."
            )
            render_takeaway(bs_takeaway)

    with col4:
        with st.container(border=True):
            top_prods_sales = top_n(filtered_df, by="product_name", metric="sales", n=10)
            fig_contrib = create_product_contribution_chart(top_prods_sales)
            st.plotly_chart(fig_contrib, use_container_width=True)

            # Dynamic Takeaway for Product Contribution
            top5_share = top_prods_sales.head(5)["sales_contribution_pct"].sum() if not top_prods_sales.empty else 0.0
            contrib_takeaway = (
                f"The top 5 revenue-generating products account for {top5_share:.1f}% of entire merchandise sales, "
                f"underpinning inventory procurement priorities."
            )
            render_takeaway(contrib_takeaway)

    # Low-Performing Categories Section
    with st.container(border=True):
        st.markdown('<h4 class="card-title">Low-Performing Categories (Underperformer Diagnostics)</h4>', unsafe_allow_html=True)
        cat_df = group_summary(filtered_df, by="product_category")
        low_cats = cat_df.sort_values(by="sales", ascending=True).head(3).copy()

        low_disp = low_cats[["product_category", "sales", "profit", "margin_pct", "orders", "units", "sales_contribution_pct"]].copy()
        low_disp["sales"] = low_disp["sales"].apply(format_inr)
        low_disp["profit"] = low_disp["profit"].apply(format_inr)
        low_disp["margin_pct"] = low_disp["margin_pct"].apply(lambda m: f"{m:.2f}%")
        low_disp["sales_contribution_pct"] = low_disp["sales_contribution_pct"].apply(lambda p: f"{p:.2f}%")

        low_disp.columns = [
            "Category",
            "Sales Revenue",
            "Gross Profit",
            "Profit Margin",
            "Orders",
            "Units Sold",
            "Revenue Share",
        ]
        st.dataframe(low_disp, use_container_width=True, hide_index=True)

        # Dynamic Takeaway for Low-Performing Categories
        lowest_cat = low_cats.iloc[0]
        low_cat_takeaway = (
            f"<strong>{lowest_cat['product_category']}</strong> represents the lowest-scale category generating only "
            f"{lowest_cat['sales']} ({lowest_cat['sales_contribution_pct']} of total revenue) with a margin of "
            f"{lowest_cat['margin_pct']}, signaling need for assortment review."
        )
        render_takeaway(low_cat_takeaway, is_alert=True)

    # -------------------------------------------------------------------------
    # Section 4: Product Drill-Through & Order-Level Export
    # -------------------------------------------------------------------------
    with st.container(border=True):
        st.markdown('<h4 class="card-title">Product Drill-Through Explorer (Order-Level Transactions)</h4>', unsafe_allow_html=True)

        all_prods = sorted(filtered_df["product_name"].dropna().unique().tolist())
        selected_prod = st.selectbox("Select Product to Inspect Detailed Order History:", options=all_prods, index=0)

        prod_orders = filtered_df[filtered_df["product_name"] == selected_prod].sort_values(by="order_date", ascending=False).copy()

        # Product mini metrics
        p_comp = completed_orders(prod_orders)
        p_sales = p_comp["sales_amount"].sum()
        p_profit = p_comp["profit_amount"].sum()
        p_margin = (p_profit / p_sales * 100.0) if p_sales > 0 else 0.0
        p_orders = len(prod_orders)
        p_units = prod_orders["quantity_sold"].sum()

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Total Orders", f"{p_orders:,}")
        with m2:
            st.metric("Units Ordered", f"{p_units:,}")
        with m3:
            st.metric("Realized Sales", format_inr(p_sales))
        with m4:
            st.metric("Gross Profit", format_inr(p_profit))
        with m5:
            st.metric("Realized Margin", f"{p_margin:.1f}%")

        # Order details table
        display_orders = prod_orders[
            ["order_id", "order_date", "customer_name", "city", "state", "quantity_sold", "discount_percent", "sales_amount", "profit_amount", "delivery_status"]
        ].copy()

        display_orders["order_date"] = display_orders["order_date"].dt.strftime("%Y-%m-%d")
        display_orders["discount_percent"] = display_orders["discount_percent"].apply(lambda d: f"{d:.1f}%")
        display_orders["sales_amount"] = display_orders["sales_amount"].apply(lambda v: f"₹{v:,.2f}")
        display_orders["profit_amount"] = display_orders["profit_amount"].apply(lambda v: f"₹{v:,.2f}")

        display_orders.columns = [
            "Order ID",
            "Order Date",
            "Customer Name",
            "City",
            "State",
            "Qty",
            "Discount",
            "Sales",
            "Profit",
            "Delivery Status",
        ]

        st.dataframe(display_orders, use_container_width=True, hide_index=True, height=280)

        # CSV Download Button
        csv_bytes = prod_orders.to_csv(index=False).encode("utf-8")
        clean_filename = selected_prod.replace(" ", "_").lower()
        st.download_button(
            label=f"📥 Download '{selected_prod}' Order Details (CSV)",
            data=csv_bytes,
            file_name=f"{clean_filename}_orders.csv",
            mime="text/csv",
            type="primary",
        )

        # Dynamic Takeaway for Selected Product
        avg_disc = prod_orders["discount_percent"].mean() if not prod_orders.empty else 0.0
        cities_count = prod_orders["city"].nunique()
        on_time_count = (prod_orders["delivery_status"] == "Delivered").sum()
        on_time_pct = (on_time_count / len(prod_orders) * 100.0) if len(prod_orders) > 0 else 0.0

        prod_takeaway = (
            f"<strong>{selected_prod}</strong>: Recorded {p_orders} total orders across {cities_count} cities with an "
            f"average promotional discount of {avg_disc:.1f}%, realizing {format_inr(p_sales)} in net revenue "
            f"at {p_margin:.1f}% margin and {on_time_pct:.1f}% on-time fulfillment."
        )
        render_takeaway(prod_takeaway)


if __name__ == "__main__":
    main()
