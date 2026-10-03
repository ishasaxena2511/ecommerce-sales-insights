"""Star Schema Generator for Power BI Desktop.

Transforms production clean dataset into a 3NF/Kimball star schema:
- fact_orders.csv
- dim_customer.csv
- dim_product.csv
- dim_date.csv (full continuous calendar with fiscal attributes)
- dim_geography.csv (with latitude / longitude)

Enforces integer surrogate keys and verifies 100% referential integrity with zero orphan keys.
"""

from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pandas as pd

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT: Path = Path(__file__).resolve().parent.parent
PROCESSED_DATA_PATH: Path = REPO_ROOT / "data" / "processed" / "ecommerce_sales_clean.csv"
COORDS_PATH: Path = REPO_ROOT / "data" / "raw" / "city_coordinates.csv"
POWERBI_DIR: Path = REPO_ROOT / "powerbi"
POWERBI_DIR.mkdir(parents=True, exist_ok=True)


def build_star_schema() -> None:
    print(f"Reading cleaned sales data from: {PROCESSED_DATA_PATH}")
    df = pd.read_csv(PROCESSED_DATA_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])

    coords = pd.read_csv(COORDS_PATH)

    # -------------------------------------------------------------------------
    # 1. Dimension: dim_customer
    # -------------------------------------------------------------------------
    print("\n1. Building dim_customer...")
    # Distinct customer profiles
    cust_df = (
        df.groupby("customer_id")
        .agg(
            customer_name=("customer_name", "first"),
            customer_segment=("customer_segment", "first"),
        )
        .reset_index()
        .sort_values(by="customer_id")
        .reset_index(drop=True)
    )
    cust_df.insert(0, "customer_key", range(1, len(cust_df) + 1))
    print(f"   dim_customer rows: {len(cust_df)}")

    # -------------------------------------------------------------------------
    # 2. Dimension: dim_product
    # -------------------------------------------------------------------------
    print("\n2. Building dim_product...")
    prod_df = (
        df.groupby("product_name")
        .agg(product_category=("product_category", "first"))
        .reset_index()
        .sort_values(by="product_name")
        .reset_index(drop=True)
    )
    prod_df.insert(0, "product_key", range(1, len(prod_df) + 1))
    print(f"   dim_product rows: {len(prod_df)}")

    # -------------------------------------------------------------------------
    # 3. Dimension: dim_geography
    # -------------------------------------------------------------------------
    print("\n3. Building dim_geography...")
    geo_df = (
        df.groupby(["city", "state", "region"])
        .size()
        .reset_index(name="order_count")
        .drop(columns=["order_count"])
        .sort_values(by=["region", "state", "city"])
        .reset_index(drop=True)
    )
    # Merge coordinates
    geo_df = geo_df.merge(
        coords[["City", "Latitude", "Longitude"]],
        left_on="city",
        right_on="City",
        how="left",
    ).drop(columns=["City"])
    geo_df.rename(columns={"Latitude": "latitude", "Longitude": "longitude"}, inplace=True)
    geo_df.insert(0, "geography_key", range(1, len(geo_df) + 1))
    print(f"   dim_geography rows: {len(geo_df)}")

    # -------------------------------------------------------------------------
    # 4. Dimension: dim_date
    # -------------------------------------------------------------------------
    print("\n4. Building dim_date (continuous calendar)...")
    # Span complete calendar years 2024-01-01 to 2026-12-31 for robust Time Intelligence
    date_range = pd.date_range(start="2024-01-01", end="2026-12-31", freq="D")
    date_rows = []
    for dt in date_range:
        date_key = int(dt.strftime("%Y%m%d"))
        year = dt.year
        month = dt.month
        day = dt.day
        day_of_week = dt.isoweekday() # 1=Mon, 7=Sun
        is_weekend = 1 if day_of_week in [6, 7] else 0
        quarter = f"Q{dt.quarter}"
        year_quarter = f"{year}-Q{dt.quarter}"
        year_month = dt.strftime("%Y-%m")
        month_name = dt.strftime("%B")
        month_short = dt.strftime("%b")
        day_name = dt.strftime("%A")

        # Indian Fiscal Year: April 1 to March 31
        if month >= 4:
            fy_start = year
            fy_end = year + 1
            f_quarter = f"FQ{((month - 4) // 3) + 1}"
            f_month_num = month - 3
        else:
            fy_start = year - 1
            fy_end = year
            f_quarter = "FQ4"
            f_month_num = month + 9
        fiscal_year = f"FY{fy_start}-{str(fy_end)[-2:]}"

        date_rows.append({
            "date_key": date_key,
            "date": dt.strftime("%Y-%m-%d"),
            "year": year,
            "month_number": month,
            "month_name": month_name,
            "month_short": month_short,
            "year_month": year_month,
            "quarter": quarter,
            "year_quarter": year_quarter,
            "day_of_month": day,
            "day_name": day_name,
            "day_of_week": day_of_week,
            "is_weekend": is_weekend,
            "fiscal_year": fiscal_year,
            "fiscal_quarter": f_quarter,
            "fiscal_month_number": f_month_num,
        })
    date_df = pd.DataFrame(date_rows)
    print(f"   dim_date rows: {len(date_df)} (from {date_df['date'].min()} to {date_df['date'].max()})")

    # -------------------------------------------------------------------------
    # 5. Fact Table: fact_orders
    # -------------------------------------------------------------------------
    print("\n5. Building fact_orders...")
    fact_df = df.copy()

    # Map surrogate keys
    # Customer
    fact_df = fact_df.merge(cust_df[["customer_key", "customer_id"]], on="customer_id", how="left")
    # Product
    fact_df = fact_df.merge(prod_df[["product_key", "product_name"]], on="product_name", how="left")
    # Geography
    fact_df = fact_df.merge(
        geo_df[["geography_key", "city", "state", "region"]],
        on=["city", "state", "region"],
        how="left",
    )
    # Date key
    fact_df["date_key"] = fact_df["order_date"].dt.strftime("%Y%m%d").astype(int)
    # Completed flag
    fact_df["is_completed"] = fact_df["delivery_status"].isin(["Delivered", "Delayed"]).astype(int)

    # Order key
    fact_df.sort_values(by=["order_date", "order_id"], inplace=True)
    fact_df.reset_index(drop=True, inplace=True)
    fact_df.insert(0, "order_key", range(1, len(fact_df) + 1))

    # Keep analytical fact columns
    fact_cols = [
        "order_key",
        "order_id",
        "date_key",
        "customer_key",
        "product_key",
        "geography_key",
        "quantity_sold",
        "unit_price",
        "discount_percent",
        "sales_amount",
        "cost_amount",
        "profit_amount",
        "profit_margin_pct",
        "payment_method",
        "shipping_mode",
        "delivery_status",
        "is_completed",
    ]
    fact_orders = fact_df[fact_cols]
    print(f"   fact_orders rows: {len(fact_orders)}")

    # -------------------------------------------------------------------------
    # 6. Referential Integrity Verification (Zero Orphan Keys)
    # -------------------------------------------------------------------------
    print("\n6. Running Referential Integrity Audits...")
    # Check null FKs
    for fk_col in ["date_key", "customer_key", "product_key", "geography_key"]:
        null_count = fact_orders[fk_col].isna().sum()
        assert null_count == 0, f"Found {null_count} nulls in {fk_col}!"

    # Check orphan customer keys
    orphan_cust = set(fact_orders["customer_key"]) - set(cust_df["customer_key"])
    assert len(orphan_cust) == 0, f"Orphan customer keys found: {orphan_cust}"

    # Check orphan product keys
    orphan_prod = set(fact_orders["product_key"]) - set(prod_df["product_key"])
    assert len(orphan_prod) == 0, f"Orphan product keys found: {orphan_prod}"

    # Check orphan geography keys
    orphan_geo = set(fact_orders["geography_key"]) - set(geo_df["geography_key"])
    assert len(orphan_geo) == 0, f"Orphan geography keys found: {orphan_geo}"

    # Check orphan date keys
    orphan_dates = set(fact_orders["date_key"]) - set(date_df["date_key"])
    assert len(orphan_dates) == 0, f"Orphan date keys found: {orphan_dates}"

    print("   ✅ ZERO orphan keys: all fact foreign keys resolve to dimension surrogate keys.")

    # Rejoin & verify metric parity
    rejoined = (
        fact_orders.merge(cust_df, on="customer_key")
        .merge(prod_df, on="product_key")
        .merge(geo_df, on="geography_key")
        .merge(date_df, on="date_key")
    )
    assert len(rejoined) == len(df), f"Row count mismatch on rejoin: {len(rejoined)} vs {len(df)}"

    comp_orig = df[df["delivery_status"].isin(["Delivered", "Delayed"])]
    comp_rejoined = rejoined[rejoined["is_completed"] == 1]

    sales_diff = abs(comp_orig["sales_amount"].sum() - comp_rejoined["sales_amount"].sum())
    profit_diff = abs(comp_orig["profit_amount"].sum() - comp_rejoined["profit_amount"].sum())
    assert sales_diff < 1e-4, f"Sales mismatch: {sales_diff}"
    assert profit_diff < 1e-4, f"Profit mismatch: {profit_diff}"
    print(f"   ✅ Metric parity check: Rejoined Sales diff = {sales_diff:.4f}, Profit diff = {profit_diff:.4f}")

    # -------------------------------------------------------------------------
    # 7. Write Star Schema CSVs to powerbi/
    # -------------------------------------------------------------------------
    print(f"\n7. Writing Star Schema CSVs to: {POWERBI_DIR}")
    fact_orders.to_csv(POWERBI_DIR / "fact_orders.csv", index=False)
    cust_df.to_csv(POWERBI_DIR / "dim_customer.csv", index=False)
    prod_df.to_csv(POWERBI_DIR / "dim_product.csv", index=False)
    geo_df.to_csv(POWERBI_DIR / "dim_geography.csv", index=False)
    date_df.to_csv(POWERBI_DIR / "dim_date.csv", index=False)

    print("   Successfully generated:")
    print(f"   - {POWERBI_DIR / 'fact_orders.csv'} ({len(fact_orders):,} rows)")
    print(f"   - {POWERBI_DIR / 'dim_customer.csv'} ({len(cust_df):,} rows)")
    print(f"   - {POWERBI_DIR / 'dim_product.csv'} ({len(prod_df):,} rows)")
    print(f"   - {POWERBI_DIR / 'dim_geography.csv'} ({len(geo_df):,} rows)")
    print(f"   - {POWERBI_DIR / 'dim_date.csv'} ({len(date_df):,} rows)")


if __name__ == "__main__":
    build_star_schema()
