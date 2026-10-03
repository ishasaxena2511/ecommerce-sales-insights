# Power BI Desktop Implementation & Architecture Guide

This comprehensive guide outlines the end-to-end instructions for assembling the enterprise **E-Commerce Sales Insights Dashboard** inside **Power BI Desktop**, matching the layout, metrics, color palette, and business logic of the Streamlit application.

---

## 1. Dimensional Star Schema & Relationship Architecture

The data model follows a Kimball-style Star Schema, strictly decoupled from transactional noise, with high-performance integer surrogate keys:

```
                      +-------------------+
                      |     dim_date      |
                      |-------------------|
                      | PK date_key (Int) |
                      |    date (Date)    |
                      |    fiscal fields  |
                      +---------+---------+
                                | 1
                                |
                                | *
+--------------------+ 1        |        1 +--------------------+
|    dim_customer    +----------+----------+    dim_product     |
|--------------------|          |          |--------------------|
| PK customer_key    |          |          | PK product_key     |
|    customer_id     |          |          |    product_name    |
|    customer_name   |    +-----+-----+    |    product_category|
|    customer_segment|    |fact_orders|    +--------------------+
+--------------------+    |-----------|
                          |order_key  |
+--------------------+    |FK date_key|    1 +------------------+
|   dim_geography    +----+FK cust_key+------+  (Measures Table)|
|--------------------|  * |FK prod_key|      |------------------|
| PK geography_key   |    |FK geo_key |      | [Total Sales]    |
|    city, state     |    |measures...|      | [Total Profit]   |
|    latitude/long   |    +-----------+      | [Profit Margin %]|
+--------------------+                       +------------------+
```

### 1.1 Relationship Configuration Table

In the **Model View** of Power BI Desktop, establish the following **1-to-Many (`1:*`)** relationships with **Single** cross-filter direction:

| From Table (Dimension) | Primary Key (`1`) | To Table (Fact) | Foreign Key (`*`) | Cardinality | Cross-Filter Direction | Active |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **`dim_date`** | `date_key` | **`fact_orders`** | `date_key` | 1 to Many (`1:*`) | Single | Yes |
| **`dim_customer`** | `customer_key` | **`fact_orders`** | `customer_key` | 1 to Many (`1:*`) | Single | Yes |
| **`dim_product`** | `product_key` | **`fact_orders`** | `product_key` | 1 to Many (`1:*`) | Single | Yes |
| **`dim_geography`** | `geography_key` | **`fact_orders`** | `geography_key` | 1 to Many (`1:*`) | Single | Yes |

> [!IMPORTANT]
> **Mark as Date Table**:
> Right-click `dim_date` in the Fields list -> **Mark as date table** -> Select `date` column. This enables Power BI's native Time Intelligence engine (`DATEADD`, `SAMEPERIODLASTYEAR`).

### 1.2 Referential Integrity Verification (Zero Orphan Keys)
- Every record in `fact_orders.csv` joins back to all four dimension tables with **100% key match**.
- Verified zero nulls across all surrogate foreign keys (`date_key`, `customer_key`, `product_key`, `geography_key`).
- Star schema CSV files are located in [`powerbi/`](./):
  - `fact_orders.csv` (1,495 rows)
  - `dim_customer.csv` (299 rows)
  - `dim_product.csv` (52 rows)
  - `dim_geography.csv` (56 rows)
  - `dim_date.csv` (1,096 rows)

---

## 2. Canvas Grid Layout System (1280 x 720 Standard)

All visuals are aligned to a responsive 1280x720 canvas grid.

```
+---------------------------------------------------------------------------------------------------+
| [1280 x 720 Canvas Grid Blueprint]                                                               |
+------------+--------------------------------------------------------------------------------------+
| LEFT       | TOP BANNER: Title & Executive Subtitle (X=234, Y=12, W=1034, H=48)                   |
| SLICERS    +--------------------------------------------------------------------------------------+
| PANEL      | 5 TOP KPI CARDS STRIP (Y=68, H=72, Gap=10px)                                         |
|            | [Sales: W=198] [Profit: W=198] [Orders: W=198] [AOV: W=198] [Margin %: W=202]        |
| X=12       +--------------------------------------------------------------------------------------+
| Y=12       | MIDDLE SECTION: Analytical Trajectories & Distributions (Y=150, H=270)               |
| W=210      | [Monthly Sales & Profit Line/Bar: W=430] [Category Bar: W=330] [Region Donut: W=254]|
| H=696      +--------------------------------------------------------------------------------------+
|            | BOTTOM SECTION: Entity Concentration & Portfolios (Y=430, H=278)                     |
|            | [Top 10 VIP Customers Table: W=540]            [Top 10 Products by Revenue: W=484]   |
+------------+--------------------------------------------------------------------------------------+
```

### Exact Coordinates & Sizing Matrix (1280 x 720)

| Visual Element | Visual Type | X (px) | Y (px) | Width (px) | Height (px) | Primary Measure / Field |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Sidebar Slicers Container** | Shape / Container | 12 | 12 | 210 | 696 | White card (`#FFFFFF`), border `#E2E8F0` |
| ├ Slicer: Date Range | Date Slicer (Between) | 20 | 80 | 194 | 85 | `dim_date[date]` |
| ├ Slicer: Region | Slicer (Dropdown) | 20 | 175 | 194 | 65 | `dim_geography[region]` |
| ├ Slicer: Product Category | Slicer (Dropdown) | 20 | 250 | 194 | 65 | `dim_product[product_category]` |
| ├ Slicer: Customer Segment | Slicer (Dropdown) | 20 | 325 | 194 | 65 | `dim_customer[customer_segment]` |
| ├ Slicer: Payment Method | Slicer (Dropdown) | 20 | 400 | 194 | 65 | `fact_orders[payment_method]` |
| └ Clear Filters Button | Button (Bookmark) | 20 | 640 | 194 | 36 | Action: Reset Filters Bookmark |
| **Executive Header Banner** | Text Box / Header | 234 | 12 | 1034 | 48 | Gradient Navy `#0B2545` to `#13315C` |
| **KPI Card 1: Total Sales** | Card (new) | 234 | 68 | 198 | 72 | `[Total Sales]`, delta `[Sales MoM Growth %]` |
| **KPI Card 2: Total Profit** | Card (new) | 442 | 68 | 198 | 72 | `[Total Profit]`, border teal `#1B998B` |
| **KPI Card 3: Completed Orders**| Card (new) | 650 | 68 | 198 | 72 | `[Total Orders]` |
| **KPI Card 4: AOV** | Card (new) | 858 | 68 | 198 | 72 | `[AOV]` |
| **KPI Card 5: Profit Margin %** | Card (new) | 1066 | 68 | 202 | 72 | `[Profit Margin %]` (Goal > 15%) |
| **Middle Visual 1: Trend** | Line and Clustered Bar | 234 | 150 | 430 | 270 | X: `dim_date[year_month]`, Bar: `[Total Sales]`, Line: `[Total Profit]` |
| **Middle Visual 2: Category** | Clustered Bar Chart | 674 | 150 | 330 | 270 | Y: `dim_product[product_category]`, X: `[Total Profit]`, Tooltip: `[Profit Margin %]` |
| **Middle Visual 3: Regional** | Donut Chart | 1014 | 150 | 254 | 270 | Legend: `dim_geography[region]`, Values: `[Total Sales]` |
| **Bottom Visual 1: Customers** | Table Visual | 234 | 430 | 540 | 278 | Columns: `customer_name`, `customer_segment`, `[Total Sales]`, `[Customer Contribution %]` |
| **Bottom Visual 2: Products** | Horizontal Bar Chart | 784 | 430 | 484 | 278 | Y: `dim_product[product_name]` (Top 10), X: `[Total Sales]` |

---

## 3. Page Construction Blueprint

### Page 1: Sales Overview (Executive BI)
- **Goal**: Macro revenue health, trajectory, monthly growth, and customer/product concentration.
- **Top KPIs**: `[Total Sales]`, `[Total Profit]`, `[Total Orders]`, `[AOV]`, `[Profit Margin %]`.
- **Trend Visual**: Line & Clustered Column:
  - Column values: `[Total Sales]` (Teal `#1B998B`)
  - Line values: `[Total Profit]` (Navy `#0B2545`)
- **VIP Customer Table**:
  - Add conditional formatting: Data bars on `[Total Sales]` (fill `#1B998B`).
  - Top 10 filter using Top N visual-level filter on `[Total Sales]`.

### Page 2: Profit Insights & Loss Prevention
- **Goal**: Margin architecture, discount sensitivity, and loss-making SKU management.
- **Top KPIs**: `[Total Profit]`, `[Profit Margin %]`, `[Loss Making Orders Count]`, `[Total Realized Loss Amount]`.
- **Visuals**:
  1. **Category Profit Bar Chart** (X: `[Total Profit]`, Y: `product_category`):
     - Conditional color rule: Positive = `#1B998B`, Negative = `#E63946`.
  2. **Treemap Visual** (Category -> Product):
     - Group: `product_category`, Details: `product_name`
     - Values: `[Total Sales]`, Color saturation: `[Profit Margin %]`
  3. **Discount Band Analysis** (Line and Clustered Bar):
     - X: Custom Discount Bands (`0%`, `1-10%`, `11-20%`, `21-30%`, `30%+`)
     - Column: `[Total Sales]`, Line: `[Profit Margin %]`
  4. **Loss-Making Products Watchlist** (Table):
     - Filter: `fact_orders[profit_amount] < 0`
     - Columns: `product_name`, `product_category`, `quantity_sold`, `sales_amount`, `profit_amount`, `discount_percent`.

### Page 3: Regional View (Geo-Spatial Intelligence)
- **Goal**: Territory performance, city-tier penetration, and state gross margins.
- **Top KPIs**: `Active City Hubs` (56), `Active States` (20), `Top Region Share`, `South Region Margin` (18.0%).
- **Visuals**:
  1. **India Geo Bubble Map** (Map / Azure Map visual):
     - Latitude: `dim_geography[latitude]`
     - Longitude: `dim_geography[longitude]`
     - Bubble Size: `[Total Sales]`
     - Bubble Color: Diverging scale based on `[Profit Margin %]` (Min `#E63946`, Mid `#F4A261`, Max `#1B998B`).
  2. **State Sales & Profit Comparison** (Grouped Bar Chart):
     - Y: `dim_geography[state]` (Top 12)
     - X: `[Total Sales]` and `[Total Profit]`
  3. **Region × Category Heatmap** (Matrix Visual):
     - Rows: `dim_geography[region]`
     - Columns: `dim_product[product_category]`
     - Values: `[Profit Margin %]`
     - Conditional Formatting: Background color scale (`#FCA5A5` to `#34D399`).

---

## 4. Advanced Interactivity Setup

### 4.1 Product Deep-Dive Drill-Through Page
1. Create a new page named `Product_Detail_Drillthrough`.
2. Under Visualizations -> **Drill-through fields**, drag `dim_product[product_name]`.
3. Set **Keep all filters** = `On`.
4. Layout visuals:
   - Header card showing selected product name.
   - 3 KPI cards: Product Sales, Product Profit, Units Sold.
   - Order-level detail table: `fact_orders[order_id]`, `dim_date[date]`, `dim_customer[customer_name]`, `quantity_sold`, `discount_percent`, `sales_amount`, `profit_amount`, `delivery_status`.
5. Enable the native Power BI **Back button** at the top left.

### 4.2 Report Page Tooltips
1. Create a page named `Category_Tooltip_Card`.
2. In Page Information -> Set **Page type** = `Tooltip` (Size: 320x240 px).
3. Insert visual:
   - Mini monthly sales sparkline line chart (`dim_date[year_month]` vs `[Total Sales]`).
   - 3 KPI labels: AOV, Profit Margin %, Return Rate.
4. On the main page Category Bar chart -> Format -> Tooltips -> Type: `Report page`, Page: `Category_Tooltip_Card`.

### 4.3 Bookmark: "Reset All Filters"
1. Configure all slicers to their default full unselected state.
2. Open View -> **Bookmarks** -> Click **Add** -> Name: `Reset_Filters`.
3. Set Bookmark Options: Uncheck **Data** if preserving user visuals, or leave **Data** checked to revert filter selections.
4. Select the sidebar "Reset Filters" button -> Format -> Action -> Type: `Bookmark` -> Bookmark: `Reset_Filters`.

---

## 5. Deployment & Power BI Service Publication

1. **Theme Ingestion**:
   - In Power BI Desktop: **View** tab -> **Themes** dropdown -> **Browse for themes** -> Select [`powerbi/theme.json`](.//powerbi/theme.json).
2. **Save & Publish**:
   - Save the project file as `ecommerce_sales_insights.pbix`.
   - Click **Home > Publish** -> Select Target Workspace (e.g. `Executive BI - Commercial Analytics`).
3. **Scheduled Refresh**:
   - In Power BI Service -> Datasets -> Settings -> **Gateway connection** (or Personal Cloud Gateway for local CSVs).
   - Set **Scheduled refresh**: Daily at 06:00 AM IST.
4. **Row-Level Security (RLS) Configuration**:
   - In Modeling -> **Manage Roles** -> Create Role: `Regional_Manager_North`.
   - Table Filter: `dim_geography[region] == "North"`.
   - Test in Service via **Security > Test as role**.
