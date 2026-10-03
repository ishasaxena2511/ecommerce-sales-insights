"""Synthetic E-Commerce Data Generator for Indian E-Commerce BI Platform.

Generates:
1. `data/raw/city_coordinates.csv`: Reference geographical coordinates.
2. `data/raw/_ground_truth_clean.csv`: 1,500 pristine orders (01-Oct-2024 to 30-Sep-2026).
3. `data/raw/ecommerce_sales_raw.csv`: Deliberately corrupted real-world raw file with
   duplicates, missing values, mixed date formats, casing/spacing issues, and outliers.

Execution:
    python src/generate_data.py
"""

from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

# Ensure UTF-8 output encoding across Windows terminals
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Global reproducibility seed
SEED: int = 42
np.random.seed(SEED)
random.seed(SEED)

# Project directory resolution
REPO_ROOT: Path = Path(__file__).resolve().parent.parent
DATA_RAW_DIR: Path = REPO_ROOT / "data" / "raw"

# -----------------------------------------------------------------------------
# 1. Geographic Reference Data
# -----------------------------------------------------------------------------
# Format: (City, State, Region, Latitude, Longitude, is_metro)
GEOGRAPHY_DATA: List[Tuple[str, str, str, float, float, bool]] = [
    # North
    ("New Delhi", "Delhi", "North", 28.6139, 77.2090, True),
    ("Delhi", "Delhi", "North", 28.7041, 77.1025, True),
    ("Noida", "Uttar Pradesh", "North", 28.5355, 77.3910, True),
    ("Lucknow", "Uttar Pradesh", "North", 26.8467, 80.9462, False),
    ("Kanpur", "Uttar Pradesh", "North", 26.4499, 80.3319, False),
    ("Jaipur", "Rajasthan", "North", 26.9124, 75.7873, False),
    ("Jodhpur", "Rajasthan", "North", 26.2389, 73.0243, False),
    ("Udaipur", "Rajasthan", "North", 24.5854, 73.7125, False),
    ("Chandigarh", "Punjab", "North", 30.7333, 76.7794, False),
    ("Ludhiana", "Punjab", "North", 30.9010, 75.8573, False),
    ("Amritsar", "Punjab", "North", 31.6340, 74.8723, False),
    ("Gurugram", "Haryana", "North", 28.4595, 77.0266, True),
    ("Faridabad", "Haryana", "North", 28.4089, 77.3178, False),

    # South
    ("Bengaluru", "Karnataka", "South", 12.9716, 77.5946, True),
    ("Mysuru", "Karnataka", "South", 12.2958, 76.6394, False),
    ("Mangaluru", "Karnataka", "South", 12.9141, 74.8560, False),
    ("Chennai", "Tamil Nadu", "South", 13.0827, 80.2707, True),
    ("Coimbatore", "Tamil Nadu", "South", 11.0168, 76.9558, False),
    ("Madurai", "Tamil Nadu", "South", 9.9252, 78.1198, False),
    ("Hyderabad", "Telangana", "South", 17.3850, 78.4867, True),
    ("Warangal", "Telangana", "South", 17.9689, 79.5941, False),
    ("Kochi", "Kerala", "South", 9.9312, 76.2673, False),
    ("Thiruvananthapuram", "Kerala", "South", 8.5241, 76.9366, False),
    ("Kozhikode", "Kerala", "South", 11.2588, 75.7804, False),
    ("Visakhapatnam", "Andhra Pradesh", "South", 17.6868, 83.2185, False),
    ("Vijayawada", "Andhra Pradesh", "South", 16.5062, 80.6480, False),

    # East
    ("Kolkata", "West Bengal", "East", 22.5726, 88.3639, True),
    ("Howrah", "West Bengal", "East", 22.5958, 88.2636, False),
    ("Siliguri", "West Bengal", "East", 26.7271, 88.3953, False),
    ("Bhubaneswar", "Odisha", "East", 20.2961, 85.8245, False),
    ("Cuttack", "Odisha", "East", 20.4625, 85.8828, False),
    ("Rourkela", "Odisha", "East", 22.2604, 84.8536, False),
    ("Patna", "Bihar", "East", 25.5941, 85.1376, False),
    ("Gaya", "Bihar", "East", 24.7914, 85.0002, False),
    ("Muzaffarpur", "Bihar", "East", 26.1209, 85.3647, False),
    ("Guwahati", "Assam", "East", 26.1445, 91.7362, False),
    ("Silchar", "Assam", "East", 24.8333, 92.7789, False),
    ("Ranchi", "Jharkhand", "East", 23.3441, 85.3096, False),
    ("Jamshedpur", "Jharkhand", "East", 22.8046, 86.2029, False),

    # West
    ("Mumbai", "Maharashtra", "West", 19.0760, 72.8777, True),
    ("Pune", "Maharashtra", "West", 18.5204, 73.8567, True),
    ("Nagpur", "Maharashtra", "West", 21.1458, 79.0882, False),
    ("Nashik", "Maharashtra", "West", 19.9975, 73.7898, False),
    ("Ahmedabad", "Gujarat", "West", 23.0225, 72.5714, True),
    ("Surat", "Gujarat", "West", 21.1702, 72.8311, False),
    ("Vadodara", "Gujarat", "West", 22.3072, 73.1812, False),
    ("Rajkot", "Gujarat", "West", 22.3039, 70.8022, False),
    ("Panaji", "Goa", "West", 15.4909, 73.8278, False),
    ("Margao", "Goa", "West", 15.2832, 73.9862, False),

    # Central
    ("Bhopal", "Madhya Pradesh", "Central", 23.2599, 77.4126, False),
    ("Indore", "Madhya Pradesh", "Central", 22.7196, 75.8577, False),
    ("Gwalior", "Madhya Pradesh", "Central", 26.2183, 78.1828, False),
    ("Jabalpur", "Madhya Pradesh", "Central", 23.1815, 79.9864, False),
    ("Raipur", "Chhattisgarh", "Central", 21.2514, 81.6296, False),
    ("Bilaspur", "Chhattisgarh", "Central", 22.0797, 82.1409, False),
    ("Durg", "Chhattisgarh", "Central", 21.1904, 81.2849, False),
]

CITY_MAP: Dict[str, Dict[str, Any]] = {
    row[0]: {
        "state": row[1],
        "region": row[2],
        "lat": row[3],
        "lon": row[4],
        "is_metro": row[5],
    }
    for row in GEOGRAPHY_DATA
}

# -----------------------------------------------------------------------------
# 2. Product Catalog & Margins
# -----------------------------------------------------------------------------
# Category-specific cost ratios aligned with business benchmarks:
# - Electronics: realized margin ~10-15% (cost ratio ~0.77 - 0.80; erodes sharply into negative above 25% discount)
# - Fashion: realized margin ~35-45% (cost ratio ~0.46 - 0.52)
# - Beauty & Personal Care: realized margin ~35-45% (cost ratio ~0.47 - 0.53)
# - Home & Kitchen: realized margin ~22-28% (cost ratio ~0.62 - 0.66)
# - Sports & Fitness: realized margin ~22-28% (cost ratio ~0.62 - 0.66)
# - Books & Stationery: realized margin ~20-26% (cost ratio ~0.64 - 0.68)
# - Grocery & Gourmet: realized margin ~18-22% (cost ratio ~0.68 - 0.72)
PRODUCTS: Dict[str, List[Tuple[str, float, float]]] = {
    "Electronics": [
        ("OnePlus Nord CE 5G (128GB)", 19999.0, 0.79),
        ("Boat Rockerz 550 Wireless Headphones", 1799.0, 0.77),
        ("Noise ColorFit Pulse 2 Max Smartwatch", 2299.0, 0.78),
        ("Samsung 43-inch Crystal 4K Neo TV", 31990.0, 0.80),
        ("Realme 20000mAh Power Bank (18W)", 1899.0, 0.77),
        ("HP 15s Ryzen 5 16GB/512GB SSD Laptop", 52990.0, 0.80),
        ("Mi Smart Air Purifier 4", 13999.0, 0.78),
        ("SanDisk Ultra 128GB MicroSD Card", 899.0, 0.76),
    ],
    "Fashion": [
        ("FabIndia Men Handloom Cotton Kurta", 1890.0, 0.48),
        ("Biba Women Printed Anarkali Suit Set", 3499.0, 0.46),
        ("Levi's Men 511 Slim Fit Jeans", 2999.0, 0.50),
        ("W for Woman Floral Rayon Kurti", 1399.0, 0.45),
        ("Allen Solly Men Classic Slim Shirt", 1699.0, 0.50),
        ("Zaveri Pearls Gold-Plated Choker Set", 899.0, 0.44),
        ("Puma Smashic Unisex White Sneakers", 3299.0, 0.51),
        ("Manyavar Silk Blend Nehru Jacket", 3199.0, 0.48),
    ],
    "Beauty & Personal Care": [
        ("Mamaearth Onion Hair Fall Control Oil 250ml", 499.0, 0.49),
        ("mCaffeine Naked & Raw Coffee Body Scrub", 399.0, 0.47),
        ("Minimalist 10% Niacinamide Face Serum", 599.0, 0.50),
        ("Forest Essentials Soundarya Radiance Cream", 2575.0, 0.46),
        ("Plum Green Tea Pore Cleansing Face Wash", 345.0, 0.48),
        ("WOW Skin Science Apple Cider Vinegar Shampoo", 449.0, 0.49),
        ("The Derma Co 1% Hyaluronic Sunscreen Aqua Gel", 499.0, 0.50),
        ("Biotique Morning Nectar Flawless Skin Lotion", 299.0, 0.48),
    ],
    "Home & Kitchen": [
        ("Prestige Iris 750W Mixer Grinder (3 Jars)", 3299.0, 0.64),
        ("Hawkins Contura Hard Anodised Pressure Cooker 3L", 1850.0, 0.63),
        ("Pigeon Non-Stick Kitchen Induction Cookware Set", 1699.0, 0.62),
        ("Wakefit Memory Foam Sleeping Pillow (Pack of 2)", 999.0, 0.65),
        ("Milton Thermosteel Flip Lid Hot/Cold Flask 1L", 949.0, 0.63),
        ("Solimo Microfibre Double Comforter Blanket", 1599.0, 0.64),
        ("Bajaj New Shakti Neo 15L Storage Water Geyser", 5899.0, 0.66),
    ],
    "Books & Stationery": [
        ("Atomic Habits by James Clear", 499.0, 0.66),
        ("The Psychology of Money by Morgan Housel", 380.0, 0.65),
        ("Classmate Pulse 6-Subject Spiral Notebooks (Pack of 4)", 299.0, 0.66),
        ("Parker Vector Standard CT Rollerball Pen", 420.0, 0.63),
        ("Ikigai: Japanese Secret to Long and Happy Life", 399.0, 0.65),
        ("Camlin Artist 24 Water Colour Tubes", 330.0, 0.64),
        ("Indian Polity 6th Edition by M. Laxmikanth", 760.0, 0.68),
    ],
    "Sports & Fitness": [
        ("Strauss TPE Anti-Skid Yoga Mat 6mm with Bag", 899.0, 0.63),
        ("Nivia Storm Football Size 5 Rubber", 499.0, 0.62),
        ("Cosco Light Tennis Cricket Ball (Pack of 6)", 420.0, 0.63),
        ("Boldfit Adjustable PVC Dumbbell Set 10kg", 1899.0, 0.64),
        ("Yonex Nanoray 7000I G4 Graphite Badminton Racquet", 1999.0, 0.64),
        ("Decathlon Domyos Training Resistance Band 15kg", 499.0, 0.61),
        ("Cultsport Smart Magnetic Spin Exercise Bike", 12999.0, 0.67),
    ],
    "Grocery & Gourmet": [
        ("Tata Tea Gold Premium Black Tea 1kg", 540.0, 0.70),
        ("Fortune Sunlite Refined Sunflower Oil 5L Can", 760.0, 0.72),
        ("India Gate Super Basmati Rice Aged 5kg", 720.0, 0.71),
        ("Disano Extra Virgin Cold Pressed Olive Oil 1L", 999.0, 0.69),
        ("Nutraj Special California Raw Whole Almonds 500g", 480.0, 0.70),
        ("Organic India Tulsi Green Tea Bags (Pack of 100)", 260.0, 0.69),
        ("Cadbury Celebrations Assorted Rich Chocolate Box", 380.0, 0.71),
    ],
}

# Category sample weights (Electronics has highest revenue driver, followed by Fashion, Home, Beauty)
CATEGORY_WEIGHTS: Dict[str, float] = {
    "Electronics": 0.22,
    "Fashion": 0.20,
    "Home & Kitchen": 0.16,
    "Beauty & Personal Care": 0.15,
    "Grocery & Gourmet": 0.12,
    "Sports & Fitness": 0.08,
    "Books & Stationery": 0.07,
}

DISCOUNT_CHOICES: List[float] = [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0]
DISCOUNT_WEIGHTS: List[float] = [0.24, 0.16, 0.20, 0.15, 0.11, 0.08, 0.04, 0.02]

# -----------------------------------------------------------------------------
# 3. Customer Generation (300 Customers with Skewed Repeat Distribution)
# -----------------------------------------------------------------------------
INDIAN_FIRST_NAMES: List[str] = [
    "Aarav", "Priya", "Rohan", "Ananya", "Vikram", "Neha", "Rahul", "Pooja",
    "Arjun", "Sneha", "Aditya", "Divya", "Kabir", "Ishita", "Siddharth", "Meera",
    "Kunal", "Shreya", "Amit", "Ritu", "Sanjay", "Swati", "Gaurav", "Tanvi",
    "Varun", "Riya", "Karthik", "Deepa", "Rajesh", "Kavita", "Nikhil", "Simran",
    "Alok", "Sunita", "Harsh", "Prerna", "Manish", "Pallavi", "Vivek", "Bhavna",
    "Akash", "Komal", "Mayank", "Nisha", "Tushar", "Preeti", "Abhishek", "Jyoti",
]

INDIAN_LAST_NAMES: List[str] = [
    "Sharma", "Patel", "Iyer", "Gupta", "Verma", "Singh", "Nair", "Chatterjee",
    "Reddy", "Joshi", "Mehta", "Kumar", "Das", "Bhat", "Rao", "Kulkarni",
    "Mukherjee", "Sen", "Pillai", "Agarwal", "Kapoor", "Malhotra", "Deshmukh",
    "Nambiar", "Choudhury", "Bose", "Saxena", "Menon", "Trivedi", "Banerjee",
]


def generate_customer_pool(num_customers: int = 300) -> List[Dict[str, Any]]:
    """Creates a deterministic pool of 300 unique Indian customers with fixed profiles."""
    cities_list = list(CITY_MAP.keys())
    # Customer segment distribution: Consumer 60%, Corporate 25%, Home Office 15%
    segments = ["Consumer", "Corporate", "Home Office"]
    segment_weights = [0.60, 0.25, 0.15]

    customers: List[Dict[str, Any]] = []
    used_names = set()

    for idx in range(1, num_customers + 1):
        cust_id = f"CUST-{idx:04d}"

        # Generate unique full name
        while True:
            first = random.choice(INDIAN_FIRST_NAMES)
            last = random.choice(INDIAN_LAST_NAMES)
            name = f"{first} {last}"
            if name not in used_names or len(used_names) >= (len(INDIAN_FIRST_NAMES) * len(INDIAN_LAST_NAMES)):
                used_names.add(name)
                break

        segment = np.random.choice(segments, p=segment_weights)
        home_city = random.choice(cities_list)
        geo_info = CITY_MAP[home_city]

        customers.append({
            "customer_id": cust_id,
            "customer_name": name,
            "customer_segment": segment,
            "city": home_city,
            "state": geo_info["state"],
            "region": geo_info["region"],
            "is_metro": geo_info["is_metro"],
        })

    return customers


# -----------------------------------------------------------------------------
# 4. Temporal Distribution & Seasonality (730 Days: Oct 1, 2024 to Sep 30, 2026)
# -----------------------------------------------------------------------------
def compute_daily_order_weights(start_date: datetime, total_days: int) -> np.ndarray:
    """Calculates realistic retail seasonality with festive spikes, summer dips, and YoY growth."""
    weights = np.zeros(total_days)

    for d in range(total_days):
        current_date = start_date + timedelta(days=d)
        month = current_date.month
        day = current_date.day

        # Base baseline weight
        w = 1.0

        # ~15% YoY secular growth trend across the 2-year timeline
        growth_multiplier = 1.0 + (0.15 * (d / 365.25))
        w *= growth_multiplier

        # Festive spike in Oct-Nov (Diwali / Dussehra / Dhanteras mega sales)
        if month == 10:
            w *= 1.85 if day >= 10 else 1.45
        elif month == 11:
            w *= 1.70 if day <= 20 else 1.25
        # January Republic Day sale bump
        elif month == 1:
            w *= 1.40 if 15 <= day <= 26 else 1.15
        # Summer dip in May-June
        elif month in (5, 6):
            w *= 0.78
        # August Independence Day & Raksha Bandhan bump
        elif month == 8 and 10 <= day <= 18:
            w *= 1.30

        # Weekend shopping lift (Friday-Sunday)
        if current_date.weekday() in (4, 5, 6):
            w *= 1.18

        weights[d] = w

    return weights / weights.sum()


# -----------------------------------------------------------------------------
# 5. Core Order Generation
# -----------------------------------------------------------------------------
def generate_clean_orders(
    num_orders: int = 1500,
    start_date: datetime = datetime(2024, 10, 1),
    total_days: int = 730,
) -> pd.DataFrame:
    """Generates 1,500 realistic, clean e-commerce orders following business constraints."""
    customers = generate_customer_pool(300)

    # Skewed repeat customer distribution (Pareto-like):
    # Ensure all 300 unique customers make at least 1 purchase, while top customers buy repeatedly
    pareto_weights = np.random.pareto(a=1.45, size=len(customers))
    pareto_probs = pareto_weights / pareto_weights.sum()

    # Assign initial 300 orders to each customer, then sample remaining 1200 via Pareto
    repeat_customers = list(np.random.choice(customers, size=num_orders - len(customers), p=pareto_probs))
    all_customer_assignments = list(customers) + repeat_customers
    np.random.shuffle(all_customer_assignments)

    daily_probs = compute_daily_order_weights(start_date, total_days)
    selected_day_offsets = np.random.choice(total_days, size=num_orders, p=daily_probs)
    # Ensure exact date range bounds 01-Oct-2024 (0) to 30-Sep-2026 (total_days - 1)
    selected_day_offsets[0] = 0
    selected_day_offsets[-1] = total_days - 1
    selected_day_offsets.sort()

    categories = list(CATEGORY_WEIGHTS.keys())
    cat_weights = [CATEGORY_WEIGHTS[c] for c in categories]

    orders: List[Dict[str, Any]] = []

    for i in range(num_orders):
        order_id = f"ORD-{100001 + i}"
        day_offset = int(selected_day_offsets[i])
        order_dt = start_date + timedelta(days=day_offset)

        # Select customer
        cust = all_customer_assignments[i]
        is_metro = cust["is_metro"]

        # Category and Product
        category = np.random.choice(categories, p=cat_weights)
        prod_tuple = random.choice(PRODUCTS[category])
        prod_name, base_price, cost_ratio = prod_tuple

        # Quantity logic: Grocery/Books often have multi-pack buys, others mostly 1-3
        if category in ("Grocery & Gourmet", "Books & Stationery"):
            quantity = int(np.random.choice([1, 2, 3, 4, 5], p=[0.45, 0.28, 0.15, 0.08, 0.04]))
        elif category == "Electronics":
            quantity = int(np.random.choice([1, 2, 3], p=[0.82, 0.14, 0.04]))
        else:
            quantity = int(np.random.choice([1, 2, 3, 4], p=[0.65, 0.22, 0.09, 0.04]))

        # Unit Price with minor realistic pricing noise (+/- 2%)
        unit_price = round(base_price * np.random.uniform(0.98, 1.02), 2)

        # Discount %
        discount_pct = float(np.random.choice(DISCOUNT_CHOICES, p=DISCOUNT_WEIGHTS))

        # Financial Calculations according to PROJECT_CONTEXT.md
        # Sales Amount = Quantity Sold * Unit Price * (1 - Discount % / 100)
        sales_amount = round(quantity * unit_price * (1.0 - discount_pct / 100.0), 2)

        # Cost calculation based on cost ratio with sharp margin erosion on heavy discounts (>25%)
        # Base unit cost is fixed, so high discounts compress profit margins significantly
        unit_cost = round(base_price * cost_ratio, 2)
        cost_amount = round(quantity * unit_cost, 2)

        profit_amount = round(sales_amount - cost_amount, 2)
        profit_margin_pct = round((profit_amount / sales_amount) * 100.0, 2) if sales_amount > 0 else 0.0

        # Payment Method:
        # Dynamic UPI adoption: climbs from ~36% in Q4 2024 to ~56% in Q3 2026
        upi_base_share = 0.36 + (0.20 * (day_offset / total_days))
        # COD is significantly higher in smaller / tier 2-3 non-metro cities
        if is_metro:
            cod_share = 0.12
            cc_share = 0.26
            nb_share = 0.10
            dc_share = 0.10
            wallet_share = max(0.02, 1.0 - (upi_base_share + cod_share + cc_share + nb_share + dc_share))
        else:
            cod_share = 0.32
            cc_share = 0.12
            nb_share = 0.08
            dc_share = 0.10
            wallet_share = max(0.02, 1.0 - (upi_base_share + cod_share + cc_share + nb_share + dc_share))

        pay_options = ["UPI", "Credit Card", "Debit Card", "Net Banking", "COD", "Wallet"]
        pay_weights = np.array([upi_base_share, cc_share, dc_share, nb_share, cod_share, wallet_share], dtype=float)
        pay_weights /= pay_weights.sum()
        payment_method = str(np.random.choice(pay_options, p=pay_weights))

        # Shipping Mode: Same-Day only in metro cities
        if is_metro:
            ship_options = ["Same-Day", "Express", "Standard", "Economy"]
            ship_weights = [0.18, 0.32, 0.36, 0.14]
        else:
            ship_options = ["Express", "Standard", "Economy"]
            ship_weights = [0.25, 0.52, 0.23]
        shipping_mode = str(np.random.choice(ship_options, p=ship_weights))

        # Delivery Status target: Delivered ~84%, Delayed ~8%, Returned ~5%, Cancelled ~3%
        # - Cancellations happen pre-dispatch ~3%
        # - Returns: Fashion has highest return rate (~10%), Beauty/Electronics ~3-4%
        # - Delays: more likely on Economy/Standard shipping and East/Central regions
        is_delayed_risk = (shipping_mode in ("Economy", "Standard")) and (cust["region"] in ("East", "Central"))

        rand_val = np.random.uniform(0.0, 1.0)
        if rand_val < 0.03:
            delivery_status = "Cancelled"
        elif category == "Fashion" and rand_val < 0.13:
            delivery_status = "Returned"
        elif category != "Fashion" and rand_val < 0.07:
            delivery_status = "Returned"
        elif is_delayed_risk and rand_val < 0.20:
            delivery_status = "Delayed"
        elif (not is_delayed_risk) and rand_val < 0.13:
            delivery_status = "Delayed"
        else:
            delivery_status = "Delivered"

        orders.append({
            "Order ID": order_id,
            "Customer ID": cust["customer_id"],
            "Customer Name": cust["customer_name"],
            "Order Date": order_dt.strftime("%Y-%m-%d"),
            "Region": cust["region"],
            "State": cust["state"],
            "City": cust["city"],
            "Product Category": category,
            "Product Name": prod_name,
            "Quantity Sold": quantity,
            "Unit Price": unit_price,
            "Discount %": discount_pct,
            "Sales Amount": sales_amount,
            "Cost Amount": cost_amount,
            "Profit Amount": profit_amount,
            "Profit Margin %": profit_margin_pct,
            "Payment Method": payment_method,
            "Shipping Mode": shipping_mode,
            "Delivery Status": delivery_status,
            "Customer Segment": cust["customer_segment"],
        })

    df = pd.DataFrame(orders)

    # Fine-tune delivery status distribution to align with ~84%, ~8%, ~5%, ~3%
    # Adjust non-cancelled/non-returned to ensure exact target realism
    cur_counts = df["Delivery Status"].value_counts()
    target_delivered = int(0.84 * num_orders)
    target_delayed = int(0.08 * num_orders)
    target_returned = int(0.05 * num_orders)
    target_cancelled = num_orders - (target_delivered + target_delayed + target_returned)

    # Rebalance precisely while respecting category return tendencies
    status_arr = df["Delivery Status"].values.copy()
    categories_arr = df["Product Category"].values

    # Assign cancelled (exactly target_cancelled)
    cand_idx = list(range(num_orders))
    np.random.shuffle(cand_idx)
    cancelled_idx = cand_idx[:target_cancelled]
    for idx in cancelled_idx:
        status_arr[idx] = "Cancelled"

    remaining = [i for i in cand_idx if i not in set(cancelled_idx)]

    # Returns: heavily biased to Fashion
    fashion_indices = [i for i in remaining if categories_arr[i] == "Fashion"]
    non_fashion_indices = [i for i in remaining if categories_arr[i] != "Fashion"]
    np.random.shuffle(fashion_indices)
    np.random.shuffle(non_fashion_indices)

    num_fashion_returns = min(len(fashion_indices), int(target_returned * 0.60))
    num_other_returns = target_returned - num_fashion_returns
    returned_idx = fashion_indices[:num_fashion_returns] + non_fashion_indices[:num_other_returns]
    for idx in returned_idx:
        status_arr[idx] = "Returned"

    remaining = [i for i in remaining if i not in set(returned_idx)]

    # Delays: biased to Economy/Standard in East/Central
    delay_cand = [
        i for i in remaining
        if df.at[i, "Shipping Mode"] in ("Economy", "Standard") and df.at[i, "Region"] in ("East", "Central")
    ]
    other_cand = [i for i in remaining if i not in set(delay_cand)]
    np.random.shuffle(delay_cand)
    np.random.shuffle(other_cand)

    num_delay_from_risk = min(len(delay_cand), int(target_delayed * 0.65))
    num_delay_other = target_delayed - num_delay_from_risk
    delayed_idx = delay_cand[:num_delay_from_risk] + other_cand[:num_delay_other]
    for idx in delayed_idx:
        status_arr[idx] = "Delayed"

    # All remaining are Delivered
    for i in remaining:
        if i not in set(delayed_idx):
            status_arr[i] = "Delivered"

    df["Delivery Status"] = status_arr
    return df


# -----------------------------------------------------------------------------
# 6. Raw Data Corruption Pipeline (Deliberate Messiness)
# -----------------------------------------------------------------------------
def corrupt_dataset(df_clean: pd.DataFrame) -> pd.DataFrame:
    """Injects realistic data quality issues into a copy of the clean dataset:

    - ~3% duplicate rows (~45 duplicates)
    - ~2% missing values each in Discount %, Profit Amount, City, Payment Method
    - Mixed date formats (YYYY-MM-DD, DD/MM/YYYY, "15 Jul 2025")
    - Inconsistent casing and trailing spaces in Product Category and Region
    - ~10 outliers (Quantity 50+ or Unit Price * 20)
    - ~5 rows with negative quantity
    """
    df_raw = df_clean.copy()
    n_rows = len(df_raw)

    # 1. Mixed Date Formats
    date_series = pd.to_datetime(df_raw["Order Date"])
    formatted_dates: List[str] = []
    for dt in date_series:
        p = np.random.uniform(0.0, 1.0)
        if p < 0.60:
            formatted_dates.append(dt.strftime("%Y-%m-%d"))
        elif p < 0.85:
            formatted_dates.append(dt.strftime("%d/%m/%Y"))
        else:
            # e.g., "15 Jul 2025"
            formatted_dates.append(dt.strftime("%d %b %Y"))
    df_raw["Order Date"] = formatted_dates

    # 2. Inconsistent Casing and Trailing Spaces in Product Category & Region
    corrupted_cats: List[str] = []
    for cat in df_raw["Product Category"]:
        rand_p = np.random.uniform(0.0, 1.0)
        if rand_p < 0.05:
            corrupted_cats.append(cat.lower() + " ")
        elif rand_p < 0.10:
            corrupted_cats.append(cat.upper())
        elif rand_p < 0.15:
            corrupted_cats.append(f"  {cat} ")
        else:
            corrupted_cats.append(cat)
    df_raw["Product Category"] = corrupted_cats

    corrupted_regions: List[str] = []
    for reg in df_raw["Region"]:
        rand_p = np.random.uniform(0.0, 1.0)
        if rand_p < 0.06:
            corrupted_regions.append(reg.upper())
        elif rand_p < 0.12:
            corrupted_regions.append(reg.lower() + " ")
        elif rand_p < 0.16:
            corrupted_regions.append(f" {reg}")
        else:
            corrupted_regions.append(reg)
    df_raw["Region"] = corrupted_regions

    # 3. Missing values (~2% missing each in Discount %, Profit Amount, City, Payment Method)
    # 2% of 1500 is 30 rows
    for col in ["Discount %", "Profit Amount", "City", "Payment Method"]:
        missing_indices = np.random.choice(n_rows, size=int(0.02 * n_rows), replace=False)
        df_raw.loc[missing_indices, col] = np.nan

    # 4. Outliers (~10 outliers: extreme quantity 50+ or price * 20)
    outlier_indices = np.random.choice(n_rows, size=10, replace=False)
    # 5 extreme quantity outliers
    qty_outliers = outlier_indices[:5]
    for q_idx in qty_outliers:
        extreme_q = int(np.random.choice([55, 60, 75, 88, 110]))
        df_raw.at[q_idx, "Quantity Sold"] = extreme_q
        # Recalculate sales amount to preserve mathematical link or create high volume spike
        p = df_raw.at[q_idx, "Unit Price"]
        d = 10.0 if pd.isna(df_raw.at[q_idx, "Discount %"]) else df_raw.at[q_idx, "Discount %"]
        df_raw.at[q_idx, "Sales Amount"] = round(extreme_q * p * (1 - d / 100.0), 2)

    # 5 extreme price * 20 outliers
    price_outliers = outlier_indices[5:]
    for p_idx in price_outliers:
        original_price = df_raw.at[p_idx, "Unit Price"]
        inflated_price = round(original_price * 20.0, 2)
        df_raw.at[p_idx, "Unit Price"] = inflated_price
        q = df_raw.at[p_idx, "Quantity Sold"]
        d = 15.0 if pd.isna(df_raw.at[p_idx, "Discount %"]) else df_raw.at[p_idx, "Discount %"]
        df_raw.at[p_idx, "Sales Amount"] = round(q * inflated_price * (1 - d / 100.0), 2)

    # 5. Negative quantities (~5 rows)
    neg_indices = np.random.choice(
        [i for i in range(n_rows) if i not in set(outlier_indices)],
        size=5,
        replace=False,
    )
    for n_idx in neg_indices:
        df_raw.at[n_idx, "Quantity Sold"] = -int(np.random.choice([1, 2, 3]))

    # 6. Duplicates (~3% duplicate rows, approx 45 rows)
    dup_count = int(0.03 * n_rows)
    dup_indices = np.random.choice(n_rows, size=dup_count, replace=False)
    duplicate_rows = df_raw.iloc[dup_indices].copy()

    # Append duplicates and shuffle rows
    df_corrupted = pd.concat([df_raw, duplicate_rows], ignore_index=True)
    df_corrupted = df_corrupted.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

    return df_corrupted


# -----------------------------------------------------------------------------
# 7. Main Execution Routine
# -----------------------------------------------------------------------------
def main() -> None:
    """Orchestrates generation of city coordinates, clean data, and corrupted raw data."""
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate & Save city_coordinates.csv
    city_df = pd.DataFrame(
        [
            {
                "City": city,
                "State": info["state"],
                "Region": info["region"],
                "Latitude": info["lat"],
                "Longitude": info["lon"],
            }
            for city, info in CITY_MAP.items()
        ]
    )
    city_coords_path = DATA_RAW_DIR / "city_coordinates.csv"
    city_df.to_csv(city_coords_path, index=False)
    print(f"[OK] Saved city coordinates: {city_coords_path} ({len(city_df)} cities)")

    # 2. Generate Clean Ground Truth (1,500 rows)
    clean_df = generate_clean_orders(num_orders=1500)
    clean_path = DATA_RAW_DIR / "_ground_truth_clean.csv"
    clean_df.to_csv(clean_path, index=False)
    print(f"[OK] Saved ground truth clean data: {clean_path} ({len(clean_df)} rows)")

    # 3. Generate & Save Deliberately Corrupted Raw Data
    raw_df = corrupt_dataset(clean_df)
    raw_path = DATA_RAW_DIR / "ecommerce_sales_raw.csv"
    raw_df.to_csv(raw_path, index=False)
    print(f"[OK] Saved corrupted raw dataset: {raw_path} ({len(raw_df)} rows)")

    # -------------------------------------------------------------------------
    # 8. Print Executive Summary
    # -------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("DATA GENERATION SUMMARY")
    print("=" * 60)
    print(f"Clean Rows: {len(clean_df):,}")
    print(f"Raw Rows (with ~3% duplicates): {len(raw_df):,}")
    print(f"Date Range (Clean): {clean_df['Order Date'].min()} to {clean_df['Order Date'].max()}")
    print(f"Unique Customers: {clean_df['Customer ID'].nunique():,}")
    def fmt_inr(val: float) -> str:
        try:
            return f"₹{val:,.2f}"
        except UnicodeEncodeError:
            return f"INR {val:,.2f}"

    def safe_p(msg: str) -> None:
        try:
            print(msg)
        except UnicodeEncodeError:
            print(msg.replace("₹", "INR "))

    safe_p(f"Total Sales (Clean Ground Truth): {fmt_inr(clean_df['Sales Amount'].sum())}")
    safe_p(f"Total Profit (Clean Ground Truth): {fmt_inr(clean_df['Profit Amount'].sum())}")
    overall_margin = (clean_df['Profit Amount'].sum() / clean_df['Sales Amount'].sum()) * 100
    safe_p(f"Overall Gross Margin %: {overall_margin:.2f}%")

    safe_p("\n[Sales by Product Category (Clean Ground Truth)]")
    cat_summary = (
        clean_df.groupby("Product Category")
        .agg(
            Orders=("Order ID", "count"),
            Total_Sales_INR=("Sales Amount", "sum"),
            Total_Profit_INR=("Profit Amount", "sum"),
            Avg_Margin_Pct=("Profit Margin %", "mean"),
        )
        .sort_values(by="Total_Sales_INR", ascending=False)
    )
    for cat, row in cat_summary.iterrows():
        sales_str = fmt_inr(row['Total_Sales_INR'])
        profit_str = fmt_inr(row['Total_Profit_INR'])
        safe_p(
            f"  - {cat:24s}: {sales_str:>14s} | "
            f"Orders: {int(row['Orders']):>4d} | "
            f"Profit: {profit_str:>12s} | "
            f"Avg Margin: {row['Avg_Margin_Pct']:>5.1f}%"
        )

    print("\n[Delivery Status Distribution (Clean)]")
    status_summary = clean_df["Delivery Status"].value_counts(normalize=True) * 100
    for status, pct in status_summary.items():
        count = (clean_df["Delivery Status"] == status).sum()
        print(f"  - {status:12s}: {count:>4d} orders ({pct:.1f}%)")

    print("\n[Raw Dataset Imperfection Checks]")
    print(f"  - Missing 'Discount %': {raw_df['Discount %'].isna().sum()} rows")
    print(f"  - Missing 'Profit Amount': {raw_df['Profit Amount'].isna().sum()} rows")
    print(f"  - Missing 'City': {raw_df['City'].isna().sum()} rows")
    print(f"  - Missing 'Payment Method': {raw_df['Payment Method'].isna().sum()} rows")
    print(f"  - Exact Duplicate Rows: {raw_df.duplicated().sum()} rows")
    print(f"  - Negative Quantity Rows: {(raw_df['Quantity Sold'] < 0).sum()} rows")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
