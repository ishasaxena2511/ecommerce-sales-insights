"""Operations, Payments & Fulfillment Dynamics — E-Commerce Sales BI Platform.

Focuses on payment method distribution, UPI adoption trends, logistics delivery status,
shipping delays, regional fulfillment, category returns, and cancellation trends.
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
    page_title="Operations & Fulfillment | E-Commerce Sales BI",
    page_icon="🚚",
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
        create_cancellation_trend_chart,
        create_category_return_chart,
        create_delivery_status_donut,
        create_payment_method_bar,
        create_regional_delay_chart,
        create_shipping_delay_chart,
        create_upi_share_trend_chart,
        render_takeaway,
    )
    from utils.filters import render_sidebar_filters
except (ModuleNotFoundError, ImportError):
    from app.utils.charts import (
        THEME,
        create_cancellation_trend_chart,
        create_category_return_chart,
        create_delivery_status_donut,
        create_payment_method_bar,
        create_regional_delay_chart,
        create_shipping_delay_chart,
        create_upi_share_trend_chart,
        render_takeaway,
    )
    from app.utils.filters import render_sidebar_filters

from src.metrics import (
    completed_orders,
    delivery_summary,
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

    # Executive Banner
    st.markdown(
        """<div class="page-header">
<h1 class="page-header-title" style="color: #FFFFFF !important; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 6px 0;"><span style="color: #FFFFFF !important;">Operations, Payments &amp; Fulfillment Dynamics</span></h1>
<p class="page-header-subtitle" style="color: #CBD5E1 !important; margin: 0; font-size: 0.88rem;">Channel payment adoption, monthly UPI share trajectory, delivery fulfillment SLA reliability, shipping mode delays, and return/cancellation risk metrics.</p>
</div>""",
        unsafe_allow_html=True,
    )

    kpis = kpi_summary(filtered_df)
    total_orders = kpis["total_all_orders"]

    # Digital payments percentage (UPI, Credit Card, Debit Card, Net Banking, Wallet)
    digital_methods = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"]
    digital_orders = (filtered_df["payment_method"].isin(digital_methods)).sum()
    digital_share = (digital_orders / total_orders * 100.0) if total_orders > 0 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("On-Time Delivery SLA", f"{kpis['on_time_pct']:.1f}%", "Delivered vs Delayed")
    with k2:
        st.metric("Return Rate", f"{kpis['return_rate']:.1f}%", f"{(filtered_df['delivery_status'] == 'Returned').sum()} Returns", delta_color="inverse")
    with k3:
        st.metric("Cancellation Rate", f"{kpis['cancel_rate']:.1f}%", f"{(filtered_df['delivery_status'] == 'Cancelled').sum()} Cancelled", delta_color="inverse")
    with k4:
        st.metric("Digital Payment Share", f"{digital_share:.1f}%", f"{digital_orders} Prepaid/Digital Orders")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Section 1: Payment Method Volumes & UPI Trajectory
    # -------------------------------------------------------------------------
    col1, col2 = st.columns([1.1, 1.25])

    with col1:
        with st.container(border=True):
            pay_df = group_summary(filtered_df, by="payment_method")
            fig_pay = create_payment_method_bar(pay_df)
            st.plotly_chart(fig_pay, use_container_width=True)

            # Dynamic Takeaway for Payment Methods
            if not pay_df.empty:
                top_pay_s = pay_df.sort_values(by="sales", ascending=False).iloc[0]
                top_pay_o = pay_df.sort_values(by="orders", ascending=False).iloc[0]
                pay_takeaway = (
                    f"<strong>{top_pay_s['payment_method']}</strong> commands the highest realized revenue at "
                    f"{format_inr(top_pay_s['sales'])}, while <strong>{top_pay_o['payment_method']}</strong> leads in "
                    f"order volume with {top_pay_o['orders']} completed transactions ({top_pay_o['sales_contribution_pct']:.1f}% share)."
                )
                render_takeaway(pay_takeaway)

    with col2:
        with st.container(border=True):
            comp_df = completed_orders(filtered_df).copy()
            if not comp_df.empty:
                comp_df["year_month"] = comp_df["order_date"].dt.strftime("%Y-%m")
                m_grouped = (
                    comp_df.groupby("year_month")
                    .agg(
                        total_orders=("order_id", "nunique"),
                        upi_orders=("payment_method", lambda s: (s == "UPI").sum()),
                    )
                    .reset_index()
                )
                m_grouped["upi_order_share_pct"] = np.where(
                    m_grouped["total_orders"] > 0,
                    (m_grouped["upi_orders"] / m_grouped["total_orders"] * 100.0).round(2),
                    0.0,
                )
                fig_upi = create_upi_share_trend_chart(m_grouped)
                st.plotly_chart(fig_upi, use_container_width=True)

                # Dynamic Takeaway for Monthly UPI Share
                if not m_grouped.empty:
                    first_upi = m_grouped["upi_order_share_pct"].iloc[0]
                    last_upi = m_grouped["upi_order_share_pct"].iloc[-1]
                    avg_upi = m_grouped["upi_order_share_pct"].mean()
                    first_m = m_grouped["year_month"].iloc[0]
                    last_m = m_grouped["year_month"].iloc[-1]
                    upi_takeaway = (
                        f"UPI order share averaged {avg_upi:.1f}% across all months, trending from "
                        f"{first_upi:.1f}% in {first_m} to {last_upi:.1f}% in {last_m}, illustrating sustained digital payment adoption."
                    )
                    render_takeaway(upi_takeaway)
            else:
                st.info("No completed orders to evaluate UPI trend.")

    # -------------------------------------------------------------------------
    # Section 2: Fulfillment Reliability & Shipping Modes
    # -------------------------------------------------------------------------
    col3, col4 = st.columns([1.1, 1.1])

    with col3:
        with st.container(border=True):
            ship_deliv = delivery_summary(filtered_df, by="shipping_mode")
            ship_deliv["delay_rate"] = (100.0 - ship_deliv["on_time_pct"]).round(2)
            fig_ship = create_shipping_delay_chart(ship_deliv)
            st.plotly_chart(fig_ship, use_container_width=True)

            # Dynamic Takeaway for Shipping Mode
            if not ship_deliv.empty:
                worst_ship = ship_deliv.sort_values(by="delay_rate", ascending=False).iloc[0]
                best_ship = ship_deliv.sort_values(by="delay_rate", ascending=True).iloc[0]
                ship_takeaway = (
                    f"<strong>{worst_ship['shipping_mode']}</strong> shipping exhibits the highest delay rate at "
                    f"{worst_ship['delay_rate']:.1f}% ({worst_ship['delayed']} delayed orders), whereas "
                    f"<strong>{best_ship['shipping_mode']}</strong> is most reliable at {best_ship['delay_rate']:.1f}% delay."
                )
                render_takeaway(ship_takeaway, is_alert=(worst_ship["delay_rate"] >= 8.0))

    with col4:
        with st.container(border=True):
            status_counts = filtered_df["delivery_status"].value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            fig_donut = create_delivery_status_donut(status_counts)
            st.plotly_chart(fig_donut, use_container_width=True)

            # Dynamic Takeaway for Delivery Status Donut
            deliv_cnt = int((filtered_df["delivery_status"] == "Delivered").sum())
            delayed_cnt = int((filtered_df["delivery_status"] == "Delayed").sum())
            ret_cnt = int((filtered_df["delivery_status"] == "Returned").sum())
            canc_cnt = int((filtered_df["delivery_status"] == "Cancelled").sum())
            n_tot = len(filtered_df)
            deliv_takeaway = (
                f"Fulfillment breakdown: {deliv_cnt/n_tot*100:.1f}% delivered on-time, {delayed_cnt/n_tot*100:.1f}% delayed, "
                f"{ret_cnt/n_tot*100:.1f}% returned, and {canc_cnt/n_tot*100:.1f}% cancelled across {n_tot:,} total orders."
            )
            render_takeaway(deliv_takeaway)

    # -------------------------------------------------------------------------
    # Section 3: Regional Delays & Category Returns
    # -------------------------------------------------------------------------
    col5, col6 = st.columns([1.1, 1.1])

    with col5:
        with st.container(border=True):
            reg_deliv = delivery_summary(filtered_df, by="region")
            reg_deliv["delay_rate"] = (100.0 - reg_deliv["on_time_pct"]).round(2)
            fig_reg_delay = create_regional_delay_chart(reg_deliv)
            st.plotly_chart(fig_reg_delay, use_container_width=True)

            # Dynamic Takeaway for Regional Delay
            if not reg_deliv.empty:
                worst_reg = reg_deliv.sort_values(by="delay_rate", ascending=False).iloc[0]
                best_reg = reg_deliv.sort_values(by="delay_rate", ascending=True).iloc[0]
                reg_takeaway = (
                    f"<strong>{worst_reg['region']}</strong> experiences highest logistical friction with a "
                    f"{worst_reg['delay_rate']:.1f}% delay rate, while <strong>{best_reg['region']}</strong> maintains "
                    f"peak delivery speed at {best_reg['delay_rate']:.1f}% delay."
                )
                render_takeaway(reg_takeaway, is_alert=(worst_reg["delay_rate"] >= 10.0))

    with col6:
        with st.container(border=True):
            cat_deliv = delivery_summary(filtered_df, by="product_category")
            fig_cat_return = create_category_return_chart(cat_deliv)
            st.plotly_chart(fig_cat_return, use_container_width=True)

            # Dynamic Takeaway for Category Returns
            if not cat_deliv.empty:
                worst_cat = cat_deliv.sort_values(by="return_rate", ascending=False).iloc[0]
                best_cat = cat_deliv.sort_values(by="return_rate", ascending=True).iloc[0]
                ret_takeaway = (
                    f"<strong>{worst_cat['product_category']}</strong> recorded the highest return rate at "
                    f"{worst_cat['return_rate']:.1f}% ({worst_cat['returned']} returned orders), contrasting with "
                    f"<strong>{best_cat['product_category']}</strong> with lowest returns at {best_cat['return_rate']:.1f}%."
                )
                render_takeaway(ret_takeaway, is_alert=(worst_cat["return_rate"] >= 6.0))

    # -------------------------------------------------------------------------
    # Section 4: Cancellation Rate Trajectory Over Time
    # -------------------------------------------------------------------------
    with st.container(border=True):
        all_df = filtered_df.copy()
        all_df["year_month"] = all_df["order_date"].dt.strftime("%Y-%m")
        m_cancel = (
            all_df.groupby("year_month")
            .agg(
                total_orders=("order_id", "nunique"),
                cancelled=("delivery_status", lambda s: (s == "Cancelled").sum()),
            )
            .reset_index()
        )
        m_cancel["cancel_rate"] = np.where(
            m_cancel["total_orders"] > 0,
            (m_cancel["cancelled"] / m_cancel["total_orders"] * 100.0).round(2),
            0.0,
        )
        fig_cancel = create_cancellation_trend_chart(m_cancel)
        st.plotly_chart(fig_cancel, use_container_width=True)

        # Dynamic Takeaway for Cancellation Trend
        if not m_cancel.empty:
            avg_cancel = m_cancel["cancel_rate"].mean()
            peak_cancel = m_cancel.sort_values(by="cancel_rate", ascending=False).iloc[0]
            cancel_takeaway = (
                f"Monthly cancellation rate averaged {avg_cancel:.1f}% over the observation window, "
                f"reaching a peak of {peak_cancel['cancel_rate']:.1f}% in {peak_cancel['year_month']} "
                f"({peak_cancel['cancelled']} cancelled orders)."
            )
            render_takeaway(cancel_takeaway, is_alert=(peak_cancel["cancel_rate"] >= 5.0))

    # Dynamic Takeaway for Cancellation Trend
    if not m_cancel.empty:
        avg_cancel = m_cancel["cancel_rate"].mean()
        peak_cancel = m_cancel.sort_values(by="cancel_rate", ascending=False).iloc[0]
        cancel_takeaway = (
            f"Monthly cancellation rate averaged {avg_cancel:.1f}% over the observation window, "
            f"reaching a peak of {peak_cancel['cancel_rate']:.1f}% in {peak_cancel['year_month']} "
            f"({peak_cancel['cancelled']} cancelled orders)."
        )
        render_takeaway(cancel_takeaway, is_alert=(peak_cancel["cancel_rate"] >= 5.0))
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
