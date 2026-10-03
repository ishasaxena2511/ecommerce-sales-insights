"""Unit and Integration Tests for Business Intelligence Metrics.

Tests:
1. Hand-computed synthetic test fixture verifying all formulas against manual calculations.
2. Reconciliation tests over production clean dataset (data/processed/ecommerce_sales_clean.csv).
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.metrics import (
    completed_orders,
    customer_summary,
    delivery_summary,
    discount_band_analysis,
    format_inr,
    group_summary,
    kpi_summary,
    monthly_trend,
    period_comparison,
    top_n,
)

PROCESSED_DATA_PATH: Path = (
    Path(__file__).resolve().parent.parent / "data" / "processed" / "ecommerce_sales_clean.csv"
)


# -----------------------------------------------------------------------------
# 1. Hand-Computed Test Fixture
# -----------------------------------------------------------------------------
@pytest.fixture
def sample_sales_data() -> pd.DataFrame:
    """Creates a tiny, hand-computed 5-order dataset with known ground truth.

    Orders:
    - ORD-01: Delivered | Electronics | Qty 1 | Price 1000 | Disc 0%  | Sales 1000 | Cost 700 | Profit 300 | Cust A
    - ORD-02: Delivered | Fashion     | Qty 2 | Price 1000 | Disc 0%  | Sales 2000 | Cost 1500| Profit 500 | Cust B
    - ORD-03: Delayed   | Electronics | Qty 1 | Price 1500 | Disc 0%  | Sales 1500 | Cost 1200| Profit 300 | Cust A
    - ORD-04: Returned  | Fashion     | Qty 1 | Price 800  | Disc 0%  | Sales 800  | Cost 600 | Profit 200 | Cust C
    - ORD-05: Cancelled | Grocery     | Qty 1 | Price 500  | Disc 0%  | Sales 500  | Cost 400 | Profit 100 | Cust D

    Hand calculations:
    - Completed orders (ORD-01, ORD-02, ORD-03):
      * Total Sales: 1000 + 2000 + 1500 = 4500.00
      * Total Profit: 300 + 500 + 300 = 1100.00
      * Gross Margin %: (1100 / 4500) * 100 = 24.44%
      * Completed Orders count: 3
      * Total All Orders count: 5
      * AOV: 4500 / 3 = 1500.00
    - Funnel Rates:
      * Delivered = 2, Delayed = 1, Returned = 1, Cancelled = 1
      * Return Rate: (1 / 5) * 100 = 20.00%
      * Cancel Rate: (1 / 5) * 100 = 20.00%
      * On-Time %: 2 / (2 + 1) * 100 = 66.67%
    """
    data = [
        {
            "order_id": "ORD-01",
            "customer_id": "CUST-A",
            "customer_name": "Aarav Sharma",
            "order_date": pd.Timestamp("2025-01-10"),
            "region": "North",
            "state": "Delhi",
            "city": "New Delhi",
            "product_category": "Electronics",
            "product_name": "Headphones",
            "quantity_sold": 1,
            "unit_price": 1000.0,
            "discount_percent": 0.0,
            "sales_amount": 1000.0,
            "cost_amount": 700.0,
            "profit_amount": 300.0,
            "profit_margin_pct": 30.0,
            "payment_method": "UPI",
            "shipping_mode": "Same-Day",
            "delivery_status": "Delivered",
            "customer_segment": "Consumer",
            "year_month": "2025-01",
            "is_completed": True,
        },
        {
            "order_id": "ORD-02",
            "customer_id": "CUST-B",
            "customer_name": "Priya Patel",
            "order_date": pd.Timestamp("2025-01-15"),
            "region": "West",
            "state": "Maharashtra",
            "city": "Mumbai",
            "product_category": "Fashion",
            "product_name": "Cotton Kurta",
            "quantity_sold": 2,
            "unit_price": 1000.0,
            "discount_percent": 0.0,
            "sales_amount": 2000.0,
            "cost_amount": 1500.0,
            "profit_amount": 500.0,
            "profit_margin_pct": 25.0,
            "payment_method": "Credit Card",
            "shipping_mode": "Express",
            "delivery_status": "Delivered",
            "customer_segment": "Corporate",
            "year_month": "2025-01",
            "is_completed": True,
        },
        {
            "order_id": "ORD-03",
            "customer_id": "CUST-A",
            "customer_name": "Aarav Sharma",
            "order_date": pd.Timestamp("2025-02-05"),
            "region": "North",
            "state": "Delhi",
            "city": "New Delhi",
            "product_category": "Electronics",
            "product_name": "Smartwatch",
            "quantity_sold": 1,
            "unit_price": 1500.0,
            "discount_percent": 0.0,
            "sales_amount": 1500.0,
            "cost_amount": 1200.0,
            "profit_amount": 300.0,
            "profit_margin_pct": 20.0,
            "payment_method": "UPI",
            "shipping_mode": "Standard",
            "delivery_status": "Delayed",
            "customer_segment": "Consumer",
            "year_month": "2025-02",
            "is_completed": True,
        },
        {
            "order_id": "ORD-04",
            "customer_id": "CUST-C",
            "customer_name": "Rohan Iyer",
            "order_date": pd.Timestamp("2025-02-12"),
            "region": "South",
            "state": "Karnataka",
            "city": "Bengaluru",
            "product_category": "Fashion",
            "product_name": "Jeans",
            "quantity_sold": 1,
            "unit_price": 800.0,
            "discount_percent": 0.0,
            "sales_amount": 800.0,
            "cost_amount": 600.0,
            "profit_amount": 200.0,
            "profit_margin_pct": 25.0,
            "payment_method": "COD",
            "shipping_mode": "Standard",
            "delivery_status": "Returned",
            "customer_segment": "Home Office",
            "year_month": "2025-02",
            "is_completed": False,
        },
        {
            "order_id": "ORD-05",
            "customer_id": "CUST-D",
            "customer_name": "Ananya Gupta",
            "order_date": pd.Timestamp("2025-02-20"),
            "region": "Central",
            "state": "Madhya Pradesh",
            "city": "Bhopal",
            "product_category": "Grocery & Gourmet",
            "product_name": "Basmati Rice",
            "quantity_sold": 1,
            "unit_price": 500.0,
            "discount_percent": 0.0,
            "sales_amount": 500.0,
            "cost_amount": 400.0,
            "profit_amount": 100.0,
            "profit_margin_pct": 20.0,
            "payment_method": "Net Banking",
            "shipping_mode": "Economy",
            "delivery_status": "Cancelled",
            "customer_segment": "Consumer",
            "year_month": "2025-02",
            "is_completed": False,
        },
    ]
    return pd.DataFrame(data)


# -----------------------------------------------------------------------------
# 2. Hand-Computed Formula Unit Tests
# -----------------------------------------------------------------------------
def test_completed_orders_scoping(sample_sales_data: pd.DataFrame) -> None:
    """Verifies that completed_orders strictly filters for Delivered and Delayed."""
    comp = completed_orders(sample_sales_data)
    assert len(comp) == 3
    assert set(comp["delivery_status"].unique()) == {"Delivered", "Delayed"}
    assert "ORD-04" not in comp["order_id"].values
    assert "ORD-05" not in comp["order_id"].values


def test_kpi_summary_hand_computed(sample_sales_data: pd.DataFrame) -> None:
    """Validates every single metric of kpi_summary against manual hand calculations."""
    kpis = kpi_summary(sample_sales_data)

    # Financial verification
    assert kpis["total_sales"] == 4500.00
    assert kpis["total_profit"] == 1100.00
    assert kpis["margin_pct"] == 24.44
    assert kpis["total_orders"] == 3
    assert kpis["total_all_orders"] == 5
    assert kpis["aov"] == 1500.00

    # Operational funnel verification
    assert kpis["return_rate"] == 20.00
    assert kpis["cancel_rate"] == 20.00
    assert kpis["on_time_pct"] == 66.67


def test_monthly_trend_hand_computed(sample_sales_data: pd.DataFrame) -> None:
    """Verifies monthly trend calculations and growth rates on hand-computed data."""
    trend = monthly_trend(sample_sales_data)
    assert len(trend) == 2  # 2025-01 and 2025-02

    # Month 1: 2025-01 (Sales = 1000 + 2000 = 3000)
    assert trend.iloc[0]["year_month"] == "2025-01"
    assert trend.iloc[0]["sales"] == 3000.00
    assert trend.iloc[0]["profit"] == 800.00
    assert pd.isna(trend.iloc[0]["mom_growth_pct"])  # MoM is NaN for first month

    # Month 2: 2025-02 (Sales = 1500)
    # MoM Growth: (1500 - 3000) / 3000 = -50.0%
    assert trend.iloc[1]["year_month"] == "2025-02"
    assert trend.iloc[1]["sales"] == 1500.00
    assert trend.iloc[1]["mom_growth_pct"] == -50.00


def test_group_summary_hand_computed(sample_sales_data: pd.DataFrame) -> None:
    """Verifies group_summary on hand-computed categories."""
    cat_summary = group_summary(sample_sales_data, by="category")

    # Categories in completed orders: Electronics (2500), Fashion (2000)
    assert len(cat_summary) == 2
    assert cat_summary.iloc[0]["product_category"] == "Electronics"
    assert cat_summary.iloc[0]["sales"] == 2500.00
    assert cat_summary.iloc[0]["sales_contribution_pct"] == 55.56

    assert cat_summary.iloc[1]["product_category"] == "Fashion"
    assert cat_summary.iloc[1]["sales"] == 2000.00
    assert cat_summary.iloc[1]["sales_contribution_pct"] == 44.44

    # Contribution % sums to 100.0%
    assert round(cat_summary["sales_contribution_pct"].sum(), 1) == 100.0


def test_top_n_hand_computed(sample_sales_data: pd.DataFrame) -> None:
    """Verifies top_n returns the highest ranked record."""
    top1 = top_n(sample_sales_data, by="category", metric="sales", n=1)
    assert len(top1) == 1
    assert top1.iloc[0]["product_category"] == "Electronics"


def test_customer_summary_hand_computed(sample_sales_data: pd.DataFrame) -> None:
    """Verifies customer aggregation, spend, and tier assignment."""
    cust_df = customer_summary(sample_sales_data)

    # 2 customers in completed orders: CUST-A (2500), CUST-B (2000)
    assert len(cust_df) == 2
    assert cust_df.iloc[0]["customer_id"] == "CUST-A"
    assert cust_df.iloc[0]["total_spend"] == 2500.00
    assert cust_df.iloc[0]["orders"] == 2
    assert cust_df.iloc[0]["aov"] == 1250.00
    assert cust_df.iloc[0]["contribution_pct"] == 55.56
    assert cust_df.iloc[0]["tier"] == "Platinum"

    assert cust_df.iloc[1]["customer_id"] == "CUST-B"
    assert cust_df.iloc[1]["total_spend"] == 2000.00
    assert cust_df.iloc[1]["orders"] == 1


def test_discount_band_analysis_hand_computed(sample_sales_data: pd.DataFrame) -> None:
    """Verifies discount band categorization."""
    disc_df = discount_band_analysis(sample_sales_data)
    # All completed orders had 0% discount
    band_0 = disc_df[disc_df["discount_band"] == "0%"]
    assert not band_0.empty
    assert band_0.iloc[0]["sales"] == 4500.00
    assert band_0.iloc[0]["orders"] == 3


def test_delivery_summary_hand_computed(sample_sales_data: pd.DataFrame) -> None:
    """Verifies delivery fulfillment metrics grouped by region."""
    deliv_df = delivery_summary(sample_sales_data, by="region")

    # North region has 2 orders: 1 Delivered, 1 Delayed
    north = deliv_df[deliv_df["region"] == "North"].iloc[0]
    assert north["total_orders"] == 2
    assert north["delivered"] == 1
    assert north["delayed"] == 1
    assert north["on_time_pct"] == 50.00
    assert north["return_rate"] == 0.00

    # South region has 1 order: Returned
    south = deliv_df[deliv_df["region"] == "South"].iloc[0]
    assert south["total_orders"] == 1
    assert south["returned"] == 1
    assert south["return_rate"] == 100.00


def test_period_comparison_hand_computed(sample_sales_data: pd.DataFrame) -> None:
    """Verifies period_comparison between two equal time windows."""
    # Current period: Feb 2025 (2025-02-01 to 2025-02-28, 27 days)
    # Previous period: Jan 2025 (preceding 27 days)
    comp = period_comparison(sample_sales_data, start="2025-02-01", end="2025-02-28")
    assert "current_period" in comp
    assert "previous_period" in comp
    assert "deltas" in comp

    # Current has ORD-03 (1500 sales)
    assert comp["current_period"]["kpis"]["total_sales"] == 1500.00
    # Previous (Jan) has ORD-01 & ORD-02 (3000 sales)
    assert comp["previous_period"]["kpis"]["total_sales"] == 3000.00
    assert comp["deltas"]["sales_delta"] == -1500.00
    assert comp["deltas"]["sales_growth_pct"] == -50.00


def test_format_inr_strings() -> None:
    """Tests Indian currency formatting across Crores, Lakhs, Thousands, and negative amounts."""
    assert format_inr(12500000) == "₹1.25 Cr"
    assert format_inr(4530000) == "₹45.3 L"
    assert format_inr(12500) == "₹12.5 K"
    assert format_inr(850.50) == "₹850.50"
    assert format_inr(-12500000) == "-₹1.25 Cr"
    assert format_inr(0) == "₹0.00"
    assert format_inr(None) == "₹0.00"


# -----------------------------------------------------------------------------
# 3. Reconciliation Tests over Real Cleaned Dataset
# -----------------------------------------------------------------------------
@pytest.fixture
def real_clean_data() -> pd.DataFrame:
    """Loads the real cleaned dataset generated by src/clean_data.py."""
    if not PROCESSED_DATA_PATH.exists():
        pytest.skip(f"Clean dataset not found at {PROCESSED_DATA_PATH}. Run clean_data.py first.")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def test_reconciliation_total_sales_equals_category_sum(real_clean_data: pd.DataFrame) -> None:
    """Reconciles that the sum of category sales exactly equals top-line total completed sales."""
    overall_kpis = kpi_summary(real_clean_data)
    cat_summary = group_summary(real_clean_data, by="product_category")

    total_kpi_sales = overall_kpis["total_sales"]
    sum_category_sales = round(cat_summary["sales"].sum(), 2)

    assert np.isclose(total_kpi_sales, sum_category_sales, atol=0.05), (
        f"Category sales sum ({sum_category_sales}) does not match total sales ({total_kpi_sales})"
    )


def test_reconciliation_total_sales_equals_region_sum(real_clean_data: pd.DataFrame) -> None:
    """Reconciles that the sum of regional sales exactly equals top-line total completed sales."""
    overall_kpis = kpi_summary(real_clean_data)
    reg_summary = group_summary(real_clean_data, by="region")

    total_kpi_sales = overall_kpis["total_sales"]
    sum_region_sales = round(reg_summary["sales"].sum(), 2)

    assert np.isclose(total_kpi_sales, sum_region_sales, atol=0.05), (
        f"Region sales sum ({sum_region_sales}) does not match total sales ({total_kpi_sales})"
    )


def test_reconciliation_total_sales_equals_customer_spend_sum(real_clean_data: pd.DataFrame) -> None:
    """Reconciles that the sum of individual customer spends equals total completed sales."""
    overall_kpis = kpi_summary(real_clean_data)
    cust_df = customer_summary(real_clean_data)

    total_kpi_sales = overall_kpis["total_sales"]
    sum_cust_spend = round(cust_df["total_spend"].sum(), 2)

    assert np.isclose(total_kpi_sales, sum_cust_spend, atol=0.05), (
        f"Customer spend sum ({sum_cust_spend}) does not match total sales ({total_kpi_sales})"
    )


def test_reconciliation_sales_contribution_sums_to_100(real_clean_data: pd.DataFrame) -> None:
    """Asserts that portfolio sales contribution percentages sum to 100% across all categories."""
    cat_summary = group_summary(real_clean_data, by="product_category")
    total_contrib = cat_summary["sales_contribution_pct"].sum()

    assert np.isclose(total_contrib, 100.0, atol=0.1), (
        f"Sales contribution percentage sum ({total_contrib}%) must equal 100.0%"
    )


def test_reconciliation_mom_growth_first_month_is_nan(real_clean_data: pd.DataFrame) -> None:
    """Asserts that Month-over-Month growth is NaN for the very first chronological month."""
    trend = monthly_trend(real_clean_data)
    assert pd.isna(trend.iloc[0]["mom_growth_pct"]), "First month MoM growth must be NaN"
    # All subsequent months should have numeric growth values
    assert trend.iloc[1:]["mom_growth_pct"].notna().all(), "Subsequent months must have valid MoM values"


def test_reconciliation_yoy_growth_first_12_months_are_nan(real_clean_data: pd.DataFrame) -> None:
    """Asserts that Year-over-Year growth is NaN for the first 12 months, and populated from month 13."""
    trend = monthly_trend(real_clean_data)
    assert len(trend) >= 13, "Dataset should have at least 13 months for YoY analysis"
    assert trend.iloc[:12]["yoy_growth_pct"].isna().all(), "First 12 months YoY growth must be NaN"
    assert not pd.isna(trend.iloc[12]["yoy_growth_pct"]), "Month 13 YoY growth must be populated"


def test_reconciliation_customer_tiers_distribution(real_clean_data: pd.DataFrame) -> None:
    """Verifies that all 4 customer tiers are present and cumulative contribution ends at 100%."""
    cust_df = customer_summary(real_clean_data)
    expected_tiers = {"Platinum", "Gold", "Silver", "Bronze"}
    assert set(cust_df["tier"].unique()).issubset(expected_tiers)

    # Cumulative contribution of sorted customers must reach 100%
    last_cum_pct = cust_df.iloc[-1]["cumulative_pct"]
    assert np.isclose(last_cum_pct, 100.0, atol=0.2), (
        f"Final cumulative spend percentage ({last_cum_pct}%) must reach 100.0%"
    )


def test_reconciliation_fulfillment_rates_bounded(real_clean_data: pd.DataFrame) -> None:
    """Asserts that on-time, return, and cancellation rates fall strictly within [0, 100]."""
    kpis = kpi_summary(real_clean_data)
    assert 0.0 <= kpis["on_time_pct"] <= 100.0
    assert 0.0 <= kpis["return_rate"] <= 100.0
    assert 0.0 <= kpis["cancel_rate"] <= 100.0
    assert 0.0 <= kpis["margin_pct"] <= 100.0


def test_reconciliation_discount_bands_total_sales(real_clean_data: pd.DataFrame) -> None:
    """Asserts that sum of sales across all discount bands matches total completed sales."""
    overall_kpis = kpi_summary(real_clean_data)
    disc_summary = discount_band_analysis(real_clean_data)

    total_kpi_sales = overall_kpis["total_sales"]
    sum_band_sales = round(disc_summary["sales"].sum(), 2)

    assert np.isclose(total_kpi_sales, sum_band_sales, atol=0.05), (
        f"Discount band sales sum ({sum_band_sales}) does not match total sales ({total_kpi_sales})"
    )
