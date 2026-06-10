import pandas as pd
import numpy as np


# =====================================================
# AUTO COLUMN DETECTION
# =====================================================
def detect_columns(df):

    cols = {c.lower(): c for c in df.columns}
    result = {}

    # DATE
    for key in ["date", "order_date", "transaction_date", "invoice_date"]:
        if key in cols:
            result["date"] = cols[key]
            break

    # SALES
    for key in ["sales", "revenue", "amount", "total", "price", "value"]:
        if key in cols:
            result["sales"] = cols[key]
            break

    # PRODUCT
    for key in ["product", "product_name", "item", "category", "sku"]:
        if key in cols:
            result["product"] = cols[key]
            break

    # CUSTOMER
    for key in ["customer", "customer_id", "client", "cust_id", "customer_name"]:
        if key in cols:
            result["customer"] = cols[key]
            break

    # QUANTITY
    for key in ["quantity", "qty", "units", "volume"]:
        if key in cols:
            result["quantity"] = cols[key]
            break

    # REGION
    for key in ["region", "state", "city", "area", "territory", "location"]:
        if key in cols:
            result["region"] = cols[key]
            break

    return result


# =====================================================
# SAFE CURRENCY FORMATTER
# =====================================================
def format_currency(val):

    try:
        val = float(val)
    except:
        return "₹0"

    if np.isnan(val):
        return "₹0"

    if val >= 1_000_000:
        return f"₹{val/1_000_000:.2f}M"

    elif val >= 1_000:
        return f"₹{val/1_000:.1f}K"

    return f"₹{val:.0f}"


# =====================================================
# SAFE DATE PARSER
# =====================================================
def safe_parse_dates(df, col):

    if col not in df.columns:
        return df

    df[col] = pd.to_datetime(
        df[col],
        errors="coerce",
        infer_datetime_format=True
    )

    return df