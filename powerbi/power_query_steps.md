# Power Query M Cleaning Steps & Data Transformation Pipeline

This document provides the exact **Power Query M** transformation code and step-by-step instructions to reproduce the production cleaning pipeline from [`src/clean_data.py`](/src/clean_data.py) inside **Power BI Desktop's Power Query Editor**.

---

## 1. Architecture Overview

In Power Query, the cleaning pipeline is implemented through modular M queries:
1. **`Raw_Sales`**: Staging query loading `data/raw/ecommerce_sales_raw.csv`.
2. **`Clean_Sales`**: Core transformation query performing schema standardization, deduplication, heterogeneous date parsing, categorical reconciliation, customer mode imputations, and financial recomputations.
3. **Star Schema Dimension & Fact Extracts**:
   - `Dim_Customer`
   - `Dim_Product`
   - `Dim_Geography`
   - `Dim_Date`
   - `Fact_Orders`

---

## 2. Complete Power Query M Script for `Clean_Sales`

Paste this script directly into **Home > Advanced Editor** in Power Query Editor:

```powerquery
let
    // -------------------------------------------------------------------------
    // Step 1: Ingest Raw Data Source
    // -------------------------------------------------------------------------
    Source = Csv.Document(
        File.Contents("<YOUR_PROJECT_PATH>\data\raw\ecommerce_sales_raw.csv"),
        [Delimiter=",", Columns=20, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    // -------------------------------------------------------------------------
    // Step 2: Trim Whitespace and Standardize Column Headers to snake_case
    // -------------------------------------------------------------------------
    TrimmedHeaders = Table.TransformColumnNames(PromotedHeaders, Text.Trim),
    RenamedColumns = Table.RenameColumns(TrimmedHeaders, {
        {"Order ID", "order_id"},
        {"Customer ID", "customer_id"},
        {"Customer Name", "customer_name"},
        {"Order Date", "raw_order_date"},
        {"Region", "region"},
        {"State", "state"},
        {"City", "city"},
        {"Product Category", "product_category"},
        {"Product Name", "product_name"},
        {"Quantity Sold", "quantity_sold"},
        {"Unit Price", "unit_price"},
        {"Discount %", "discount_percent"},
        {"Sales Amount", "sales_amount"},
        {"Cost Amount", "cost_amount"},
        {"Profit Amount", "profit_amount"},
        {"Profit Margin %", "profit_margin_pct"},
        {"Payment Method", "payment_method"},
        {"Shipping Mode", "shipping_mode"},
        {"Delivery Status", "delivery_status"},
        {"Customer Segment", "customer_segment"}
    }),

    // Trim whitespace on all text columns
    TrimmedTextColumns = Table.TransformColumns(RenamedColumns, {
        {"order_id", Text.Trim, type text},
        {"customer_id", Text.Trim, type text},
        {"customer_name", Text.Trim, type text},
        {"raw_order_date", Text.Trim, type text},
        {"region", Text.Trim, type text},
        {"state", Text.Trim, type text},
        {"city", Text.Trim, type text},
        {"product_category", Text.Trim, type text},
        {"product_name", Text.Trim, type text},
        {"payment_method", Text.Trim, type text},
        {"shipping_mode", Text.Trim, type text},
        {"delivery_status", Text.Trim, type text},
        {"customer_segment", Text.Trim, type text}
    }),

    // -------------------------------------------------------------------------
    // Step 3: Deduplication (Keep First Occurrence of Order ID)
    // -------------------------------------------------------------------------
    DeduplicatedOrders = Table.Distinct(TrimmedTextColumns, {"order_id"}),

    // -------------------------------------------------------------------------
    // Step 4: Parse Heterogeneous Dates (YYYY-MM-DD, DD/MM/YYYY, '15 Jul 2025')
    // -------------------------------------------------------------------------
    AddedOrderDate = Table.AddColumn(DeduplicatedOrders, "order_date", each
        let
            raw = [raw_order_date],
            parsed = try Date.FromText(raw, [Format="yyyy-MM-dd"]) otherwise
                     try Date.FromText(raw, [Format="dd/MM/yyyy"]) otherwise
                     try Date.FromText(raw, [Format="d/M/yyyy"]) otherwise
                     try Date.From(raw, "en-IN") otherwise
                     try Date.From(raw, "en-US") otherwise null
        in
            parsed,
        type date
    ),
    RemovedRawDate = Table.RemoveColumns(AddedOrderDate, {"raw_order_date"}),
    FilteredValidDates = Table.SelectRows(RemovedRawDate, each [order_date] <> null),

    // -------------------------------------------------------------------------
    // Step 5: Categorical Value Standardization (Title Case & Domain Validation)
    // -------------------------------------------------------------------------
    StandardizedCategoricals = Table.TransformColumns(FilteredValidDates, {
        {"region", each Text.Proper(Text.Trim(_)), type text},
        {"product_category", each Text.Proper(Text.Trim(_)), type text},
        {"customer_segment", each Text.Proper(Text.Trim(_)), type text},
        {"shipping_mode", each Text.Proper(Text.Trim(_)), type text},
        {"delivery_status", each Text.Proper(Text.Trim(_)), type text}
    }),

    // Standardize Payment Methods (handle UPI case and variants)
    StandardizedPayment = Table.TransformColumns(StandardizedCategoricals, {
        {"payment_method", each
            let
                val = Text.Upper(Text.Trim(_))
            in
                if val = "UPI" then "UPI"
                else if Text.Contains(val, "CREDIT") then "Credit Card"
                else if Text.Contains(val, "DEBIT") then "Debit Card"
                else if Text.Contains(val, "NET") or Text.Contains(val, "BANKING") then "Net Banking"
                else if val = "COD" or Text.Contains(val, "CASH") then "COD"
                else if Text.Contains(val, "WALLET") then "Wallet"
                else if _ = null or _ = "" or _ = "NAN" then "Unknown"
                else Text.Proper(_),
            type text
        }
    }),

    // -------------------------------------------------------------------------
    // Step 6: Convert Numeric Types for Downstream Calculations
    // -------------------------------------------------------------------------
    ConvertedTypes = Table.TransformColumnTypes(StandardizedPayment, {
        {"quantity_sold", Int64.Type},
        {"unit_price", type number},
        {"discount_percent", type number},
        {"cost_amount", type number}
    }),

    // -------------------------------------------------------------------------
    // Step 7: Impute Missing Discount % with Category Median
    // -------------------------------------------------------------------------
    // Group by category to find median discount
    CategoryMedians = Table.Group(
        Table.SelectRows(ConvertedTypes, each [discount_percent] <> null),
        {"product_category"},
        {{"median_discount", each List.Median([discount_percent]), type number}}
    ),
    MergedCategoryMedians = Table.NestedJoin(
        ConvertedTypes, {"product_category"},
        CategoryMedians, {"product_category"},
        "CatMed",
        JoinKind.LeftOuter
    ),
    ExpandedCategoryMedians = Table.ExpandTableColumn(MergedCategoryMedians, "CatMed", {"median_discount"}, {"cat_median_discount"}),
    ImputedDiscounts = Table.TransformColumns(ExpandedCategoryMedians, {
        {"discount_percent", each if _ = null then [cat_median_discount] else _, type number}
    }),
    ReplacedNullDiscountWithZero = Table.ReplaceValue(
        ImputedDiscounts,
        null,
        0.0,
        Replacer.ReplaceValue,
        {"discount_percent"}
    ),
    RemovedCatMedianCol = Table.RemoveColumns(ReplacedNullDiscountWithZero, {"cat_median_discount"}),

    // -------------------------------------------------------------------------
    // Step 8: Recompute Financial Metrics Dynamically (Formula Ground Truth)
    // -------------------------------------------------------------------------
    // Recompute Sales Amount: Quantity * Unit Price * (1 - Discount/100)
    RecomputedSales = Table.AddColumn(RemovedCatMedianCol, "clean_sales_amount", each
        Number.Round([quantity_sold] * [unit_price] * (1.0 - ([discount_percent] / 100.0)), 2),
        type number
    ),

    // Recompute Profit Amount: Sales Amount - Cost Amount
    RecomputedProfit = Table.AddColumn(RecomputedSales, "clean_profit_amount", each
        Number.Round([clean_sales_amount] - [cost_amount], 2),
        type number
    ),

    // Recompute Profit Margin %: (Profit / Sales) * 100
    RecomputedMargin = Table.AddColumn(RecomputedProfit, "clean_profit_margin_pct", each
        if [clean_sales_amount] > 0 then
            Number.Round(([clean_profit_amount] / [clean_sales_amount]) * 100.0, 2)
        else
            0.0,
        type number
    ),

    // Clean up original computed columns and rename new standardized fields
    RemovedOldCalculated = Table.RemoveColumns(RecomputedMargin, {"sales_amount", "profit_amount", "profit_margin_pct"}),
    RenamedCleanCalculated = Table.RenameColumns(RemovedOldCalculated, {
        {"clean_sales_amount", "sales_amount"},
        {"clean_profit_amount", "profit_amount"},
        {"clean_profit_margin_pct", "profit_margin_pct"}
    })
in
    RenamedCleanCalculated
```

---

## 3. Why Recomputing Profit Is Superior to Imputing an Average

In messy transactional data, missing values frequently occur in `Profit Amount` or `Profit Margin %`. In traditional naive data cleaning, practitioners often substitute the missing values with the column mean (`mean(profit)`) or category median (`median(profit)`). 

In this pipeline, **Profit is strictly recomputed from fundamental accounting equations**:

$$\text{Profit Amount} = \text{Sales Amount} - \text{Cost Amount}$$

$$\text{Sales Amount} = \text{Quantity Sold} \times \text{Unit Price} \times \left(1 - \frac{\text{Discount \%}}{100}\right)$$

### Key Rationale:

1. **Mathematical Identity Integrity**:
   - Profit is not an independent stochastic variable; it is a **deterministic derived identity**.
   - If an order with a ₹50,000 laptop and ₹46,000 cost has a missing profit field, substituting an overall company mean profit of ₹895 creates an irreconcilable financial contradiction (`Sales (50,000) - Cost (46,000) = 4,000 ≠ 895`).
2. **Elimination of Variance Distortion & Bias**:
   - Imputing an average dampens variance, distorts SKU-level margin spreads, and artificially masks loss-making orders (negative profit transactions).
3. **Auditing & Financial Compliance**:
   - Enterprise BI dashboards must withstand financial audits. Recomputing guarantees that row-level drill-through records sum up exactly to aggregate general ledger figures.

---

## 4. Star Schema Extraction in Power Query

From the `Clean_Sales` query, the dimensional model is constructed via **Reference Query**:

### `Dim_Customer`
```powerquery
let
    Source = Clean_Sales,
    Grouped = Table.Group(Source, {"customer_id"}, {
        {"customer_name", each List.First([customer_name]), type text},
        {"customer_segment", each List.First([customer_segment]), type text}
    }),
    Sorted = Table.Sort(Grouped, {{"customer_id", Order.Ascending}}),
    AddedKey = Table.AddIndexColumn(Sorted, "customer_key", 1, 1, Int64.Type),
    Reordered = Table.ReorderColumns(AddedKey, {"customer_key", "customer_id", "customer_name", "customer_segment"})
in
    Reordered
```

### `Dim_Product`
```powerquery
let
    Source = Clean_Sales,
    Grouped = Table.Group(Source, {"product_name"}, {
        {"product_category", each List.First([product_category]), type text}
    }),
    Sorted = Table.Sort(Grouped, {{"product_name", Order.Ascending}}),
    AddedKey = Table.AddIndexColumn(Sorted, "product_key", 1, 1, Int64.Type),
    Reordered = Table.ReorderColumns(AddedKey, {"product_key", "product_name", "product_category"})
in
    Reordered
```

### `Dim_Geography`
```powerquery
let
    Source = Clean_Sales,
    Grouped = Table.Group(Source, {"city", "state", "region"}, {}),
    Coords = Csv.Document(
        File.Contents("<YOUR_PROJECT_PATH>\data\raw\city_coordinates.csv"),
        [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    PromotedCoords = Table.PromoteHeaders(Coords, [PromoteAllScalars=true]),
    TypedCoords = Table.TransformColumnTypes(PromotedCoords, {
        {"Latitude", type number},
        {"Longitude", type number}
    }),
    Merged = Table.NestedJoin(Grouped, {"city"}, TypedCoords, {"City"}, "GeoCoords", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Merged, "GeoCoords", {"Latitude", "Longitude"}, {"latitude", "longitude"}),
    Sorted = Table.Sort(Expanded, {{"region", Order.Ascending}, {"state", Order.Ascending}, {"city", Order.Ascending}}),
    AddedKey = Table.AddIndexColumn(Sorted, "geography_key", 1, 1, Int64.Type),
    Reordered = Table.ReorderColumns(AddedKey, {"geography_key", "city", "state", "region", "latitude", "longitude"})
in
    Reordered
```

### `Fact_Orders`
```powerquery
let
    Source = Clean_Sales,
    MergeCust = Table.NestedJoin(Source, {"customer_id"}, Dim_Customer, {"customer_id"}, "Cust", JoinKind.Inner),
    ExpandCust = Table.ExpandTableColumn(MergeCust, "Cust", {"customer_key"}, {"customer_key"}),

    MergeProd = Table.NestedJoin(ExpandCust, {"product_name"}, Dim_Product, {"product_name"}, "Prod", JoinKind.Inner),
    ExpandProd = Table.ExpandTableColumn(MergeProd, "Prod", {"product_key"}, {"product_key"}),

    MergeGeo = Table.NestedJoin(ExpandProd, {"city", "state", "region"}, Dim_Geography, {"city", "state", "region"}, "Geo", JoinKind.Inner),
    ExpandGeo = Table.ExpandTableColumn(MergeGeo, "Geo", {"geography_key"}, {"geography_key"}),

    AddedDateKey = Table.AddColumn(ExpandGeo, "date_key", each
        Date.Year([order_date]) * 10000 + Date.Month([order_date]) * 100 + Date.Day([order_date]),
        Int64.Type
    ),
    AddedIsCompleted = Table.AddColumn(AddedDateKey, "is_completed", each
        if [delivery_status] = "Delivered" or [delivery_status] = "Delayed" then 1 else 0,
        Int64.Type
    ),
    Sorted = Table.Sort(AddedIsCompleted, {{"order_date", Order.Ascending}, {"order_id", Order.Ascending}}),
    AddedOrderKey = Table.AddIndexColumn(Sorted, "order_key", 1, 1, Int64.Type),
    SelectedColumns = Table.SelectColumns(AddedOrderKey, {
        "order_key", "order_id", "date_key", "customer_key", "product_key", "geography_key",
        "quantity_sold", "unit_price", "discount_percent", "sales_amount", "cost_amount",
        "profit_amount", "profit_margin_pct", "payment_method", "shipping_mode", "delivery_status",
        "is_completed"
    })
in
    SelectedColumns
```
