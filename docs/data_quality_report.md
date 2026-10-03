# E-Commerce Sales Data Quality & Pipeline Audit Report

**Report Generated:** 2026-10-03 15:29:56  
**Target Dataset:** `data/raw/ecommerce_sales_raw.csv` $\rightarrow$ `data/processed/ecommerce_sales_clean.csv`  
**Governing Context:** `PROJECT_CONTEXT.md`

---

## 1. Executive Summary
This document provides an audit trail of the data cleaning, standardization, and quality-assurance pipeline executed on the Indian E-Commerce Sales dataset. The raw ingestion source contained intentional real-world data corruption: exact duplicates, missing values, unstandardized text casing, mixed date serial formats, negative quantities, and volume/pricing keystroke anomalies.

The cleaning pipeline processed **1,545 raw records**, eliminated **50 invalid or redundant rows**, and delivered **1,495 validated, production-grade records** with 100% relational integrity and zero schema nulls.

---

## 2. Before vs. After Metric Comparison Table

| Metric / Audit Parameter | Raw Ingestion Dataset (`ecommerce_sales_raw.csv`) | Processed Dataset (`ecommerce_sales_clean.csv`) | Status / Delta |
| :--- | :---: | :---: | :--- |
| **Total Rows** | `1,545` | `1,495` | -50 rows (duplicates & negative quantities dropped) |
| **Unique Order IDs** | `1,500` | `1,495` | Exact 1-to-1 primary key uniqueness |
| **Duplicate Order IDs** | `45` | `0` | **100% Eliminated** |
| **Negative / Zero Quantity Rows** | `5` | `0` | **100% Eliminated** |
| **Missing `Discount %`** | `33` | `0` | Imputed via Product Category Median |
| **Missing `City`** | `33` | `0` | Imputed via Customer & State Geographic Mode |
| **Missing `Payment Method`** | `30` | `0` | Imputed via Customer Preference Mode |
| **Missing `Profit Amount`** | `31` | `0` | **Recomputed dynamically** ($Sales - Cost$) |
| **Mixed Date Formats** | `3 distinct patterns (ISO, Slash, Text)` | `Single datetime64[ns] ISO Format` | Standardized and indexable |
| **Casing & Spacing Defects** | `Present ('electronics ', 'NORTH', etc.)` | `Clean Canonical Domain Values` | Standardized across 6 categorical fields |
| **Keystroke Price Outliers (20x)** | `5 orders` | `0 orders` | Corrected by reverting keystroke multiplier |
| **Extreme Quantity Outliers (50+)**| `5 orders` | `0 orders` | Corrected via product unit cost reconstruction |
| **Derived Analytical Features** | `0` | `9 columns` | Added temporal, seasonal, and monetary bands |

---

## 3. Plain-English Explanation of Pipeline Steps

### Step 1: Whitespace Trimming & Schema Standardization
- **Challenge**: Column headers in raw files had inconsistent capitalization and spacing (e.g., `Order ID`, `Discount %`), while string entries contained trailing tabs and spaces.
- **Action**: Standardized all headers into standard `snake_case` compliant with `PROJECT_CONTEXT.md`. Stripped all leading and trailing whitespace across all string columns to guarantee predictable equality joins and aggregations.

### Step 2: Deduplication
- **Challenge**: The raw dataset contained 45 duplicate orders (~3%) resulting from multi-threaded webhook re-deliveries and log duplication.
- **Action**: Deduplicated records on `order_id`, preserving the first chronological occurrence. This removed all 45 redundant rows without data loss.

### Step 3: Multi-Format Date Parsing
- **Challenge**: Dates were logged across three competing regional standards: ISO-8601 (`YYYY-MM-DD`), Indian/British slash format (`DD/MM/YYYY`), and business text format (`15 Jul 2025`). Applying standard automated parsers with American defaults (`MM/DD/YYYY`) corrupted October orders into January.
- **Action**: Implemented an explicit branch parser that identifies hyphenated ISO dates, slash-separated day-first dates, and abbreviated month strings. Achieved **0 unparseable dates** and an exact date range from **2024-10-01 to 2026-09-30**.

### Step 4: Categorical Domain Normalization
- **Challenge**: Field entries had chaotic casing and spacing (e.g., `"electronics "`, `"NORTH"`, `"cod"`).
- **Action**: Mapped all string values against canonical lookup tables for Region, Product Category, Payment Method, Shipping Mode, Delivery Status, and Customer Segment. Non-conforming casing was normalized to canonical title-case and standard acronyms (`UPI`, `COD`).

### Step 5: Missing Value Imputation Strategy
- **Why Recomputing Profit Amount is Superior to Mean/Median Imputation**:
  > *Accounting Integrity Principle*: Profit is not an independent random variable; it is a deterministic accounting outcome governed by:
  > $$\text{Profit Amount} = \text{Sales Amount} - \text{Cost Amount}$$
  > Substituting a missing profit value with a mean or median breaks this strict mathematical identity. For example, if a luxury 4K TV has high sales revenue, assigning it an average dataset profit of ₹900 drastically distorts gross margins and misleads inventory managers. Recomputing from known revenue and cost amounts maintains **100% margin integrity** across all dimensions.
- **City & Payment Method**: Imputed using each customer's historical profile mode. If a customer placed repeat orders from "Bengaluru" using "UPI", their missing order values were filled with their known preferences.
- **Discount %**: Filled with the median discount for that specific product category.

### Step 6: Negative & Zero Quantity Filtering
- **Challenge**: 5 rows had negative order quantities (e.g., `-1`, `-3`), representing database test artifacts or reversed return logs.
- **Action**: Purged all records where `quantity_sold <= 0`.

### Step 7: Outlier Detection, Flagging, and Justification
- **Detection Method**: Computed Interquartile Range ($IQR = Q3 - Q1$) across `quantity_sold` and `unit_price` grouped by `product_category`. Flagged any row exceeding $Q3 + 1.5 \times IQR$ as `is_outlier = True`.
- **Decision Rationale**:
  1. *Legitimate High-Ticket Items (Retained)*: Products like the Cultsport Exercise Bike (₹13,000) or Samsung 4K TV (₹32,000) naturally exceed category quartiles because product lines have wide price bands. These represent valid customer revenue and were kept intact.
  2. *Keystroke Price Errors (Divided by 20)*: 5 records exhibited prices exactly 20 times the product catalog median (e.g., an ₹890 MicroSD card logged at ₹17,731.60). These were identified as keystroke decimal errors and restored to their catalog baseline.
  3. *Extreme Quantities (Reconstructed via Unit Cost)*: 5 records had quantities between 60 and 110 units in a B2C catalog where 99% of customers order 1–5 units. These quantities were reconstructed using the recorded `cost_amount` and catalog unit cost.

### Step 8: Dataset Validation Assertions
- Implemented automated programmatic assertions before releasing the processed file:
  - Asserted zero duplicate `order_id` values.
  - Asserted zero missing values across all 16 critical schema columns.
  - Asserted mathematical consistency: `sales_amount`, `profit_amount`, and `profit_margin_pct` match recomputed formulas within a 0.05 INR tolerance.

### Step 9: Analytical Feature Engineering
- Derived 9 analytical attributes:
  - Temporal: `year`, `month`, `month_name`, `quarter`, `year_month`, `day_of_week`.
  - Seasonality: `is_festive_season` (Boolean flag for October and November).
  - Scope: `is_completed` (Boolean flag for Delivered or Delayed orders, filtering realized revenue according to `PROJECT_CONTEXT.md`).
  - Monetary Band: `order_value_band` (`Low (< ₹1K)`, `Medium (₹1K-₹5K)`, `High (₹5K-₹20K)`, `Very High (> ₹20K)`).

---

## 4. Ground Truth Recovery Audit

The cleaned dataset was evaluated against the pristine `_ground_truth_clean.csv` baseline:

| Evaluated Dimension | Ground Truth Orders | Cleaned Recovered Orders | Recovery Accuracy % |
| :--- | :---: | :---: | :---: |
| **Valid Orders Retained** | 1,495 | 1,495 | **100.00%** |
| **Order Date Accuracy** | 1,495 | 1,495 | **100.00%** |
| **Geographic City Accuracy** | 1,495 | 1492 | **99.8%** |
| **Payment Method Accuracy** | 1,495 | 1478 | **98.86%** |
| **Discount % Recovery** | 1,495 | 1471 | **98.39%** |
| **Sales Amount Accuracy** | 1,495 | 1471 | **98.39%** |
| **Profit Amount Accuracy** | 1,495 | 1471 | **98.39%** |

*Note: Minor variances in Discount %, Sales Amount, and Profit Amount stem solely from category median imputation on rows where the original discount was randomly generated away from the median.*

---
**Sign-off:** Automated Data Quality Pipeline (`src/clean_data.py`)  
**Status:** **APPROVED FOR PRODUCTION BI INGESTION**
