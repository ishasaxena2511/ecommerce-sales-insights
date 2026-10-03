# E-Commerce Sales Insights Dashboard — Project Context

## 1. Goal & Audience
- **Project Purpose**: Build an end-to-end, enterprise-grade sales business intelligence (BI) platform for an Indian e-commerce company.
- **Target Audience**: 
  - Executive Leadership (CEO, VP of Sales) seeking macro revenue trajectories, margins, and market health.
  - Functional Leads (Marketing, Inventory/Supply Chain) optimizing campaign ROI, regional fulfillment, shipping channels, and product categories.
  - Hiring Managers & Technical Recruiters assessing data modeling, Python engineering, statistical rigor, dashboard UX, and business acumen.

---

## 2. Technology Stack
- **Language**: Python 3.11
- **Data Engineering & Manipulation**: `pandas`, `numpy`
- **Visualization**: `plotly` (interactive web figures)
- **Application & UI**: `streamlit` (multi-page business intelligence app)
- **Testing & Verification**: `pytest`
- **Exploratory Analysis**: `jupyter`, `nbconvert`
- **Path Management & Portability**: Python standard library `pathlib.Path`

---

## 3. Data Schemas

### 3.1 Raw Schema (Exact Column Names)
The raw ingestion pipeline expects CSV data with the exact column headers:
1. `Order ID` (e.g., `ORD-100001`)
2. `Customer ID` (e.g., `CUST-0001`)
3. `Customer Name` (e.g., `Aarav Sharma`)
4. `Order Date` (mixed raw formats: `YYYY-MM-DD`, `DD/MM/YYYY`, text dates like `15 Jul 2025`)
5. `Region` (`North`, `South`, `East`, `West`, `Central`)
6. `State` (Indian states, e.g., `Maharashtra`, `Karnataka`, `Delhi`, etc.)
7. `City` (Indian cities, e.g., `Mumbai`, `Bengaluru`, `Delhi`, etc.)
8. `Product Category` (`Electronics`, `Fashion`, `Home & Kitchen`, `Beauty & Personal Care`, `Books & Stationery`, `Sports & Fitness`, `Grocery & Gourmet`)
9. `Product Name` (Specific product title)
10. `Quantity Sold` (Integer units ordered)
11. `Unit Price` (Base price per unit in INR ₹)
12. `Discount %` (Percentage discount applied: 0 to 40)
13. `Sales Amount` (Net revenue generated in INR ₹)
14. `Cost Amount` (Total cost of goods sold in INR ₹)
15. `Profit Amount` (Net profit in INR ₹)
16. `Profit Margin %` (Profit as a percentage of Sales Amount)
17. `Payment Method` (`UPI`, `Credit Card`, `Debit Card`, `Net Banking`, `COD`, `Wallet`)
18. `Shipping Mode` (`Same-Day`, `Express`, `Standard`, `Economy`)
19. `Delivery Status` (`Delivered`, `Delayed`, `Returned`, `Cancelled`)
20. `Customer Segment` (`Consumer`, `Corporate`, `Home Office`)

### 3.2 Processed Schema (1-to-1 snake_case Mapping)
Cleaned and validated analytical datasets convert raw column names into standardized `snake_case`:
- `Order ID` $\rightarrow$ `order_id`
- `Customer ID` $\rightarrow$ `customer_id`
- `Customer Name` $\rightarrow$ `customer_name`
- `Order Date` $\rightarrow$ `order_date` (`datetime64[ns]`)
- `Region` $\rightarrow$ `region`
- `State` $\rightarrow$ `state`
- `City` $\rightarrow$ `city`
- `Product Category` $\rightarrow$ `product_category`
- `Product Name` $\rightarrow$ `product_name`
- `Quantity Sold` $\rightarrow$ `quantity_sold`
- `Unit Price` $\rightarrow$ `unit_price`
- `Discount %` $\rightarrow$ `discount_percent`
- `Sales Amount` $\rightarrow$ `sales_amount`
- `Cost Amount` $\rightarrow$ `cost_amount`
- `Profit Amount` $\rightarrow$ `profit_amount`
- `Profit Margin %` $\rightarrow$ `profit_margin_pct`
- `Payment Method` $\rightarrow$ `payment_method`
- `Shipping Mode` $\rightarrow$ `shipping_mode`
- `Delivery Status` $\rightarrow$ `delivery_status`
- `Customer Segment` $\rightarrow$ `customer_segment`

---

## 4. Metric Definitions & Business Logic

### 4.1 Financial Metrics & Formulas
- **Sales Amount**:
  $$\text{Sales Amount} = \text{Quantity Sold} \times \text{Unit Price} \times \left(1 - \frac{\text{Discount \%}}{100}\right)$$
- **Profit Amount**:
  $$\text{Profit Amount} = \text{Sales Amount} - \text{Cost Amount}$$
- **Profit Margin %**:
  $$\text{Profit Margin \%} = \begin{cases} \left(\frac{\text{Profit Amount}}{\text{Sales Amount}}\right) \times 100, & \text{if Sales Amount} > 0 \\ 0.0, & \text{otherwise} \end{cases}$$
- **Rounding**: All financial amounts rounded to 2 decimal places.

### 4.2 Order Scoping & Pipeline Integrity
- **Completed Orders Scope**:
  $$\text{Completed Orders} \iff \text{Delivery Status} \in \{\text{Delivered}, \text{Delayed}\}$$
- **Revenue & Profit KPIs**: ALL top-line sales, revenue growth, gross margins, and profitability KPIs MUST strictly compute over **Completed orders only**.
- **Exception & Funnel Metrics**:
  - `Returned` and `Cancelled` orders are excluded from realized revenue and profit.
  - **Return Rate**:
    $$\text{Return Rate} = \frac{\text{Count of Orders with Delivery Status = 'Returned'}}{\text{Total Orders}} \times 100$$
  - **Cancellation Rate**:
    $$\text{Cancellation Rate} = \frac{\text{Count of Orders with Delivery Status = 'Cancelled'}}{\text{Total Orders}} \times 100$$

### 4.3 Operational & Analytical KPIs
- **Total Orders**: Distinct count of `Order ID` ($\text{nunique}(\text{order\_id})$).
- **Average Order Value (AOV)**:
  $$\text{AOV} = \frac{\text{Total Completed Sales Amount}}{\text{Total Completed Orders}}$$
- **Revenue Growth %**: Month-over-Month (MoM) and Year-over-Year (YoY) percentage changes:
  $$\text{Growth \%} = \frac{\text{Sales}_{t} - \text{Sales}_{t-1}}{\text{Sales}_{t-1}} \times 100$$
- **Entity Contribution % (Customer or Product)**:
  $$\text{Contribution \%} = \frac{\text{Entity Sales}}{\text{Total Category / Portfolio Sales}} \times 100$$
- **On-time Delivery %**:
  $$\text{On-time \%} = \frac{\text{Count}(\text{Delivery Status} = \text{'Delivered'})}{\text{Count}(\text{Delivery Status} \in \{\text{'Delivered'}, \text{'Delayed'}\})} \times 100$$

---

## 5. Engineering & Analytical Conventions
- **Reproducibility**: All pseudorandom generators seeded deterministically with `42` (`numpy.random.seed(42)`).
- **Execution Standard**: Every pipeline script must be executable from repository root:
  ```bash
  python src/<script_name>.py
  ```
- **Path Resolution**: Standardized `pathlib.Path` usage across all modules (`Path(__file__).resolve().parents[...]`).
- **Code Quality**: Full type hints (`typing`) and comprehensive docstrings on every function and class.
- **Dynamic Calculation**: NEVER hardcode insight figures, KPI values, or executive summaries. Always compute them dynamically from underlying data frames.
- **Indian Currency Representation**:
  - Currency symbol: `₹`
  - Compact number formatting using Indian terminology:
    - Thousands: `K` (e.g., `₹85.4K`)
    - Lakhs ($10^5$): `L` (e.g., `₹12.45L`)
    - Crores ($10^7$): `Cr` (e.g., `₹1.85Cr`)

---

## 6. Dashboard Theme & Visual Identity
- **Header Primary Navy**: `#0B2545`
- **Secondary Navy/Blue**: `#13315C`
- **Primary Accent / Teal**: `#1B998B`
- **Highlight / Amber**: `#F4A261`
- **Negative / Alert Red**: `#E63946`
- **Canvas / Page Background**: `#F5F7FA`
- **Card Surface Background**: `#FFFFFF` (with soft elevation shadow)
- **Typography**: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
