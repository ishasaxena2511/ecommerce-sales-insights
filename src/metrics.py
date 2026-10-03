"""Core Business Metrics & Analytical Calculations for Indian E-Commerce BI Platform.

This module provides pure, deterministic, and fully-typed business intelligence metrics
over the cleaned e-commerce sales dataset.

Conventions & Governance (PROJECT_CONTEXT.md):
- No UI / Streamlit dependencies (pure pandas/numpy domain logic).
- Completed Orders Scope: Delivery Status in ('Delivered', 'Delayed').
  All revenue, profit, gross margin, AOV, and growth metrics compute strictly on completed orders.
- Exception & Funnel Scope: Returned and Cancelled orders are analyzed separately via
  return rates and cancellation rates.
- Currency Formatting: Indian numbering conventions (₹ with K / L / Cr suffixes).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

# Standard column aliases for flexible dimension grouping
DIMENSION_ALIASES: Dict[str, str] = {
    "category": "product_category",
    "product_category": "product_category",
    "product": "product_name",
    "product_name": "product_name",
    "region": "region",
    "state": "state",
    "city": "city",
    "segment": "customer_segment",
    "customer_segment": "customer_segment",
    "payment": "payment_method",
    "payment_method": "payment_method",
    "shipping": "shipping_mode",
    "shipping_mode": "shipping_mode",
    "delivery": "delivery_status",
    "delivery_status": "delivery_status",
    "order_value_band": "order_value_band",
}


def _resolve_dimension(by: str) -> str:
    """Resolves dimension name or alias to canonical column header."""
    canonical = DIMENSION_ALIASES.get(by.strip().lower(), by.strip())
    return canonical


# -----------------------------------------------------------------------------
# 1. Scoping: Completed Orders
# -----------------------------------------------------------------------------
def completed_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Filters a sales DataFrame to completed orders only.

    According to PROJECT_CONTEXT.md:
        Completed Orders <=> Delivery Status in ('Delivered', 'Delayed').
    Returned and Cancelled orders are excluded from realized revenue and gross profit.

    Args:
        df: Input e-commerce sales DataFrame.

    Returns:
        Filtered DataFrame containing only delivered and delayed orders.
    """
    if "is_completed" in df.columns:
        return df[df["is_completed"]].copy()
    if "delivery_status" in df.columns:
        return df[df["delivery_status"].isin(["Delivered", "Delayed"])].copy()
    return df.copy()


# -----------------------------------------------------------------------------
# 2. Executive KPI Summary
# -----------------------------------------------------------------------------
def kpi_summary(df: pd.DataFrame) -> Dict[str, float]:
    """Computes executive top-line KPIs across financial and operational dimensions.

    Financial metrics (Sales, Profit, Margin, AOV) strictly evaluate Completed orders.
    Operational funnel metrics (Return Rate, Cancel Rate, On-Time %) evaluate total volume.

    Args:
        df: Input e-commerce sales DataFrame.

    Returns:
        Dictionary containing:
            - total_sales: Total realized completed revenue (INR).
            - total_profit: Total realized completed profit (INR).
            - margin_pct: Gross profit margin percentage (%).
            - total_orders: Count of distinct completed order IDs.
            - total_all_orders: Total distinct order IDs across all delivery statuses.
            - aov: Average Order Value (total_sales / total_orders).
            - return_rate: Returned orders / total orders (%).
            - cancel_rate: Cancelled orders / total orders (%).
            - on_time_pct: Delivered orders / (Delivered + Delayed) (%).
    """
    if df.empty:
        return {
            "total_sales": 0.0,
            "total_profit": 0.0,
            "margin_pct": 0.0,
            "total_orders": 0,
            "total_all_orders": 0,
            "aov": 0.0,
            "return_rate": 0.0,
            "cancel_rate": 0.0,
            "on_time_pct": 0.0,
        }

    total_all_orders = int(df["order_id"].nunique())

    # Completed orders for financial KPIs
    comp_df = completed_orders(df)
    comp_orders = int(comp_df["order_id"].nunique())
    total_sales = float(comp_df["sales_amount"].sum())
    total_profit = float(comp_df["profit_amount"].sum())
    margin_pct = (total_profit / total_sales * 100.0) if total_sales > 0 else 0.0
    aov = (total_sales / comp_orders) if comp_orders > 0 else 0.0

    # Operational fulfillment rates across entire order universe
    status_counts = df["delivery_status"].value_counts().to_dict()
    returned_cnt = status_counts.get("Returned", 0)
    cancelled_cnt = status_counts.get("Cancelled", 0)
    delivered_cnt = status_counts.get("Delivered", 0)
    delayed_cnt = status_counts.get("Delayed", 0)

    return_rate = (returned_cnt / total_all_orders * 100.0) if total_all_orders > 0 else 0.0
    cancel_rate = (cancelled_cnt / total_all_orders * 100.0) if total_all_orders > 0 else 0.0

    completed_cnt = delivered_cnt + delayed_cnt
    on_time_pct = (delivered_cnt / completed_cnt * 100.0) if completed_cnt > 0 else 0.0

    return {
        "total_sales": round(total_sales, 2),
        "total_profit": round(total_profit, 2),
        "margin_pct": round(margin_pct, 2),
        "total_orders": comp_orders,
        "total_all_orders": total_all_orders,
        "aov": round(aov, 2),
        "return_rate": round(return_rate, 2),
        "cancel_rate": round(cancel_rate, 2),
        "on_time_pct": round(on_time_pct, 2),
    }


# -----------------------------------------------------------------------------
# 3. Monthly Trend & Growth Dynamics
# -----------------------------------------------------------------------------
def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Computes monthly financial trajectories with MoM and YoY revenue growth rates.

    Evaluates realized completed orders. Calculates:
        - mom_growth_pct: Month-over-Month % change (first month is NaN).
        - yoy_growth_pct: Year-over-Year % change (first 12 months are NaN).

    Args:
        df: Input e-commerce sales DataFrame.

    Returns:
        DataFrame indexed/sorted by year_month with sales, profit, margin_pct,
        orders, units, mom_growth_pct, and yoy_growth_pct.
    """
    comp_df = completed_orders(df).copy()
    if comp_df.empty:
        return pd.DataFrame(
            columns=[
                "year_month",
                "sales",
                "profit",
                "margin_pct",
                "orders",
                "units",
                "mom_growth_pct",
                "yoy_growth_pct",
            ]
        )

    if "year_month" not in comp_df.columns:
        comp_df["year_month"] = comp_df["order_date"].dt.strftime("%Y-%m")

    grouped = (
        comp_df.groupby("year_month")
        .agg(
            sales=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
            orders=("order_id", "nunique"),
            units=("quantity_sold", "sum"),
        )
        .reset_index()
    )

    grouped = grouped.sort_values(by="year_month").reset_index(drop=True)
    grouped["sales"] = grouped["sales"].round(2)
    grouped["profit"] = grouped["profit"].round(2)
    grouped["margin_pct"] = np.where(
        grouped["sales"] > 0,
        ((grouped["profit"] / grouped["sales"]) * 100.0).round(2),
        0.0,
    )

    # MoM and YoY percentage changes
    grouped["mom_growth_pct"] = (grouped["sales"].pct_change(1) * 100.0).round(2)
    grouped["yoy_growth_pct"] = (grouped["sales"].pct_change(12) * 100.0).round(2)

    return grouped


# -----------------------------------------------------------------------------
# 4. Group Summary
# -----------------------------------------------------------------------------
def group_summary(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Aggregates sales, profits, orders, units, and portfolio contribution across any dimension.

    Supports canonical dimensions and aliases: category, product, region, state, city,
    segment, payment method, shipping mode. Computes realized completed orders.

    Args:
        df: Input sales DataFrame.
        by: Grouping column name or alias.

    Returns:
        Aggregated DataFrame sorted by sales descending, with sales_contribution_pct
        summing to 100.0%.
    """
    col = _resolve_dimension(by)
    if col not in df.columns:
        raise KeyError(f"Column '{by}' (resolved to '{col}') not found in DataFrame.")

    comp_df = completed_orders(df)
    if comp_df.empty:
        return pd.DataFrame(
            columns=[col, "sales", "profit", "margin_pct", "orders", "units", "sales_contribution_pct"]
        )

    total_portfolio_sales = comp_df["sales_amount"].sum()

    grouped = (
        comp_df.groupby(col)
        .agg(
            sales=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
            orders=("order_id", "nunique"),
            units=("quantity_sold", "sum"),
        )
        .reset_index()
    )

    grouped["sales"] = grouped["sales"].round(2)
    grouped["profit"] = grouped["profit"].round(2)
    grouped["margin_pct"] = np.where(
        grouped["sales"] > 0,
        ((grouped["profit"] / grouped["sales"]) * 100.0).round(2),
        0.0,
    )

    if total_portfolio_sales > 0:
        grouped["sales_contribution_pct"] = (
            (grouped["sales"] / total_portfolio_sales) * 100.0
        ).round(2)
    else:
        grouped["sales_contribution_pct"] = 0.0

    grouped = grouped.sort_values(by="sales", ascending=False).reset_index(drop=True)
    return grouped


# -----------------------------------------------------------------------------
# 5. Top N Ranking Wrapper
# -----------------------------------------------------------------------------
def top_n(df: pd.DataFrame, by: str, metric: str = "sales", n: int = 10) -> pd.DataFrame:
    """Extracts top N entities ranked by a specified KPI (e.g., sales, profit, orders, units).

    Args:
        df: Input sales DataFrame.
        by: Dimension to rank (e.g. 'product_name', 'city').
        metric: KPI name to rank by ('sales', 'profit', 'orders', 'units').
        n: Number of top records to return.

    Returns:
        Top N DataFrame slice.
    """
    summary = group_summary(df, by)
    if metric not in summary.columns:
        raise KeyError(f"Metric '{metric}' not found in group summary columns: {list(summary.columns)}")
    return summary.sort_values(by=metric, ascending=False).head(n).reset_index(drop=True)


# -----------------------------------------------------------------------------
# 6. Customer Summary & Stratification
# -----------------------------------------------------------------------------
def customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates customer lifetime spend, order frequency, recency, and spend tier.

    Tier segmentation by spend percentile rank:
        - Platinum: >= 85th percentile (top 15% VIP customers)
        - Gold: 60th to 85th percentile (upper-middle high value)
        - Silver: 30th to 60th percentile (core consistent buyers)
        - Bronze: < 30th percentile (occasional / entry buyers)

    Args:
        df: Input sales DataFrame.

    Returns:
        DataFrame with customer_id, customer_name, total_spend, orders, aov,
        first_order_date, last_order_date, contribution_pct, cumulative_pct, and tier.
    """
    comp_df = completed_orders(df)
    if comp_df.empty:
        return pd.DataFrame(
            columns=[
                "customer_id",
                "customer_name",
                "total_spend",
                "orders",
                "aov",
                "first_order_date",
                "last_order_date",
                "contribution_pct",
                "cumulative_pct",
                "tier",
            ]
        )

    grouped = (
        comp_df.groupby(["customer_id", "customer_name"])
        .agg(
            total_spend=("sales_amount", "sum"),
            orders=("order_id", "nunique"),
            first_order_date=("order_date", "min"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )

    grouped["total_spend"] = grouped["total_spend"].round(2)
    grouped["aov"] = np.where(
        grouped["orders"] > 0,
        (grouped["total_spend"] / grouped["orders"]).round(2),
        0.0,
    )

    # Sort descending by spend to calculate contribution & cumulative pareto
    grouped = grouped.sort_values(by="total_spend", ascending=False).reset_index(drop=True)
    total_sales = grouped["total_spend"].sum()

    if total_sales > 0:
        grouped["contribution_pct"] = ((grouped["total_spend"] / total_sales) * 100.0).round(2)
        grouped["cumulative_pct"] = grouped["contribution_pct"].cumsum().round(2)
    else:
        grouped["contribution_pct"] = 0.0
        grouped["cumulative_pct"] = 0.0

    # Percentile-based Tier Assignment
    # rank(pct=True) computes relative percentile rank from 0.0 to 1.0
    pct_rank = grouped["total_spend"].rank(pct=True, method="min")
    tier_conditions = [
        pct_rank >= 0.85,
        pct_rank >= 0.60,
        pct_rank >= 0.30,
    ]
    tier_labels = ["Platinum", "Gold", "Silver"]
    grouped["tier"] = np.select(tier_conditions, tier_labels, default="Bronze")

    return grouped


# -----------------------------------------------------------------------------
# 7. Discount Band Analysis
# -----------------------------------------------------------------------------
def discount_band_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyzes volume and profitability across discrete promotional discount bands.

    Bands:
        - '0%': Full price / zero discount
        - '1-10%': Low incentive discount
        - '11-20%': Standard seasonal discount
        - '21-30%': High clearance discount
        - '30%+': Deep promotion (sharp margin erosion)

    Args:
        df: Input sales DataFrame.

    Returns:
        DataFrame with discount_band, sales, profit, margin_pct, orders, units, avg_discount.
    """
    comp_df = completed_orders(df).copy()
    if comp_df.empty:
        return pd.DataFrame(
            columns=["discount_band", "sales", "profit", "margin_pct", "orders", "units", "avg_discount"]
        )

    # Binning definition
    conditions = [
        comp_df["discount_percent"] == 0.0,
        (comp_df["discount_percent"] > 0.0) & (comp_df["discount_percent"] <= 10.0),
        (comp_df["discount_percent"] > 10.0) & (comp_df["discount_percent"] <= 20.0),
        (comp_df["discount_percent"] > 20.0) & (comp_df["discount_percent"] <= 30.0),
        comp_df["discount_percent"] > 30.0,
    ]
    labels = ["0%", "1-10%", "11-20%", "21-30%", "30%+"]
    comp_df["discount_band"] = np.select(conditions, labels, default="0%")

    # Ensure fixed ordering
    comp_df["discount_band"] = pd.Categorical(comp_df["discount_band"], categories=labels, ordered=True)

    grouped = (
        comp_df.groupby("discount_band", observed=False)
        .agg(
            sales=("sales_amount", "sum"),
            profit=("profit_amount", "sum"),
            orders=("order_id", "nunique"),
            units=("quantity_sold", "sum"),
            avg_discount=("discount_percent", "mean"),
        )
        .reset_index()
    )

    grouped["sales"] = grouped["sales"].round(2)
    grouped["profit"] = grouped["profit"].round(2)
    grouped["avg_discount"] = grouped["avg_discount"].round(2)
    grouped["margin_pct"] = np.where(
        grouped["sales"] > 0,
        ((grouped["profit"] / grouped["sales"]) * 100.0).round(2),
        0.0,
    )

    return grouped


# -----------------------------------------------------------------------------
# 8. Delivery & Fulfillment Summary
# -----------------------------------------------------------------------------
def delivery_summary(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Computes fulfillment reliability, return rate, and cancellation rate across any dimension.

    Evaluated across ALL orders regardless of delivery status.

    Args:
        df: Input sales DataFrame.
        by: Grouping column (e.g. 'shipping_mode', 'region', 'product_category').

    Returns:
        DataFrame with total_orders, delivered, delayed, returned, cancelled,
        on_time_pct, return_rate, cancel_rate.
    """
    col = _resolve_dimension(by)
    if col not in df.columns:
        raise KeyError(f"Column '{by}' (resolved to '{col}') not found in DataFrame.")

    if df.empty:
        return pd.DataFrame(
            columns=[
                col,
                "total_orders",
                "delivered",
                "delayed",
                "returned",
                "cancelled",
                "on_time_pct",
                "return_rate",
                "cancel_rate",
            ]
        )

    # Pivot order counts by delivery status
    status_pivot = (
        df.groupby([col, "delivery_status"])["order_id"]
        .nunique()
        .unstack(fill_value=0)
        .reset_index()
    )

    # Ensure all 4 delivery statuses exist in columns
    for st in ["Delivered", "Delayed", "Returned", "Cancelled"]:
        if st not in status_pivot.columns:
            status_pivot[st] = 0

    status_pivot = status_pivot.rename(
        columns={
            "Delivered": "delivered",
            "Delayed": "delayed",
            "Returned": "returned",
            "Cancelled": "cancelled",
        }
    )

    status_pivot["total_orders"] = (
        status_pivot["delivered"]
        + status_pivot["delayed"]
        + status_pivot["returned"]
        + status_pivot["cancelled"]
    )

    completed_orders_cnt = status_pivot["delivered"] + status_pivot["delayed"]
    status_pivot["on_time_pct"] = np.where(
        completed_orders_cnt > 0,
        ((status_pivot["delivered"] / completed_orders_cnt) * 100.0).round(2),
        0.0,
    )
    status_pivot["return_rate"] = np.where(
        status_pivot["total_orders"] > 0,
        ((status_pivot["returned"] / status_pivot["total_orders"]) * 100.0).round(2),
        0.0,
    )
    status_pivot["cancel_rate"] = np.where(
        status_pivot["total_orders"] > 0,
        ((status_pivot["cancelled"] / status_pivot["total_orders"]) * 100.0).round(2),
        0.0,
    )

    status_pivot = status_pivot.sort_values(by="total_orders", ascending=False).reset_index(drop=True)
    return status_pivot


# -----------------------------------------------------------------------------
# 9. Period Comparison (Current vs. Previous Equal Period)
# -----------------------------------------------------------------------------
def period_comparison(
    df: pd.DataFrame,
    start: Union[str, datetime, pd.Timestamp],
    end: Union[str, datetime, pd.Timestamp],
) -> Dict[str, Any]:
    """Compares financial and operational KPIs between a target date range and the preceding equal period.

    For example, if start = 2025-01-01 and end = 2025-03-31 (90 days),
    the previous baseline period is 2024-10-03 to 2024-12-31 (preceding 90 days).

    Args:
        df: Input sales DataFrame.
        start: Start date of current evaluation window (inclusive).
        end: End date of current evaluation window (inclusive).

    Returns:
        Dictionary containing current period KPIs, previous period KPIs,
        and absolute/percentage deltas.
    """
    ts_start = pd.to_datetime(start)
    ts_end = pd.to_datetime(end)

    if ts_start > ts_end:
        raise ValueError(f"Start date ({ts_start}) cannot be after end date ({ts_end}).")

    duration = ts_end - ts_start
    # Previous period of equal length immediately preceding start date
    prev_end = ts_start - timedelta(days=1)
    prev_start = prev_end - duration

    # Filter periods
    curr_df = df[(df["order_date"] >= ts_start) & (df["order_date"] <= ts_end)]
    prev_df = df[(df["order_date"] >= prev_start) & (df["order_date"] <= prev_end)]

    curr_kpi = kpi_summary(curr_df)
    prev_kpi = kpi_summary(prev_df)

    def _calc_growth(curr: float, prev: float) -> Optional[float]:
        if prev > 0:
            return round(((curr - prev) / prev) * 100.0, 2)
        return None

    deltas = {
        "sales_delta": round(curr_kpi["total_sales"] - prev_kpi["total_sales"], 2),
        "sales_growth_pct": _calc_growth(curr_kpi["total_sales"], prev_kpi["total_sales"]),
        "profit_delta": round(curr_kpi["total_profit"] - prev_kpi["total_profit"], 2),
        "profit_growth_pct": _calc_growth(curr_kpi["total_profit"], prev_kpi["total_profit"]),
        "margin_delta_pct": round(curr_kpi["margin_pct"] - prev_kpi["margin_pct"], 2),
        "orders_delta": int(curr_kpi["total_orders"] - prev_kpi["total_orders"]),
        "orders_growth_pct": _calc_growth(curr_kpi["total_orders"], prev_kpi["total_orders"]),
        "aov_delta": round(curr_kpi["aov"] - prev_kpi["aov"], 2),
        "aov_growth_pct": _calc_growth(curr_kpi["aov"], prev_kpi["aov"]),
    }

    return {
        "current_period": {
            "start": str(ts_start.date()),
            "end": str(ts_end.date()),
            "kpis": curr_kpi,
        },
        "previous_period": {
            "start": str(prev_start.date()),
            "end": str(prev_end.date()),
            "kpis": prev_kpi,
        },
        "deltas": deltas,
    }


# -----------------------------------------------------------------------------
# 10. Indian Currency Formatter (₹ with K / L / Cr formatting)
# -----------------------------------------------------------------------------
def format_inr(value: Optional[Union[float, int]], precision: int = 2) -> str:
    """Formats numeric amounts into standard Indian currency strings (₹ with K / L / Cr).

    Formatting Rules:
        - >= 10,000,000 (1 Crore): '₹X.XX Cr'
        - >= 100,000 (1 Lakh): '₹X.XX L'
        - >= 1,000 (1 Thousand): '₹X.XX K'
        - < 1,000: '₹X.XX'

    Args:
        value: Numeric currency amount in INR.
        precision: Decimal points for abbreviated units (default 2).

    Returns:
        Formatted string (e.g., '₹1.25 Cr', '₹45.3 L', '₹12.5 K', '₹850.00').
    """
    if value is None or pd.isna(value):
        return "₹0.00"

    num = float(value)
    sign = "-" if num < 0 else ""
    abs_num = abs(num)

    if abs_num >= 10_000_000:  # 1 Crore = 10 Million
        scaled = abs_num / 10_000_000
        formatted = f"{scaled:.{precision}f}".rstrip("0").rstrip(".") if precision > 0 else f"{scaled:.0f}"
        return f"{sign}₹{formatted} Cr"
    elif abs_num >= 100_000:  # 1 Lakh = 100 Thousand
        scaled = abs_num / 100_000
        formatted = f"{scaled:.{precision}f}".rstrip("0").rstrip(".") if precision > 0 else f"{scaled:.0f}"
        return f"{sign}₹{formatted} L"
    elif abs_num >= 1_000:  # 1 Thousand
        scaled = abs_num / 1_000
        formatted = f"{scaled:.{precision}f}".rstrip("0").rstrip(".") if precision > 0 else f"{scaled:.0f}"
        return f"{sign}₹{formatted} K"
    else:
        return f"{sign}₹{abs_num:,.{precision}f}"
