"""
KPI calculations for Flux.
Provides resilient, well-defined business metrics guarded against division by zero and empty filters.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

def calculate_macro_kpis(
    sales_df: pd.DataFrame,
    cancellations_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    Calculates executive-level retail KPIs from filtered transactions.

    Definitions:
    - Gross Revenue: Sum of line_total for valid sales transactions.
    - Return Volume: Sum of return_amount for cancellation transactions (if provided).
    - Net Revenue: Gross Revenue - Return Volume.
    - Orders: Count of distinct valid invoice numbers.
    - Identified Customers: Count of distinct non-null customer IDs.
    - Unique Products: Count of distinct product stock codes.
    - Units Sold: Total quantity of items sold in valid transactions.
    - Average Order Value (AOV): Gross Revenue / Valid Orders.
    - Items Per Order: Units Sold / Valid Orders.
    - Repeat Customer Rate: Share of identified customers with 2 or more distinct orders.
    """
    if sales_df.empty:
        return {
            "gross_revenue": 0.0,
            "return_volume": 0.0,
            "net_revenue": 0.0,
            "total_orders": 0,
            "identified_customers": 0,
            "unique_products": 0,
            "units_sold": 0,
            "aov": 0.0,
            "items_per_order": 0.0,
            "repeat_customer_rate": 0.0,
            "repeat_customers_count": 0,
            "return_transactions_count": 0,
        }

    gross_revenue = float(sales_df["line_total"].sum())
    units_sold = int(sales_df["quantity"].sum())
    total_orders = int(sales_df["invoice_no"].nunique())
    unique_products = int(sales_df["stock_code"].nunique())

    # Customer metrics on non-null identified customers
    identified_cust_df = sales_df.dropna(subset=["customer_id"])
    identified_customers = int(identified_cust_df["customer_id"].nunique())

    if identified_customers > 0:
        cust_order_counts = identified_cust_df.groupby("customer_id")["invoice_no"].nunique()
        repeat_customers = int((cust_order_counts >= 2).sum())
        repeat_rate = float(repeat_customers / identified_customers)
    else:
        repeat_customers = 0
        repeat_rate = 0.0

    # AOV and items per order
    aov = float(gross_revenue / total_orders) if total_orders > 0 else 0.0
    items_per_order = float(units_sold / total_orders) if total_orders > 0 else 0.0

    # Returns calculation
    return_volume = 0.0
    return_tx_count = 0
    if cancellations_df is not None and not cancellations_df.empty:
        return_volume = float(cancellations_df["return_amount"].sum())
        return_tx_count = int(len(cancellations_df))

    net_revenue = gross_revenue - return_volume

    return {
        "gross_revenue": gross_revenue,
        "return_volume": return_volume,
        "net_revenue": net_revenue,
        "total_orders": total_orders,
        "identified_customers": identified_customers,
        "unique_products": unique_products,
        "units_sold": units_sold,
        "aov": aov,
        "items_per_order": items_per_order,
        "repeat_customer_rate": repeat_rate,
        "repeat_customers_count": repeat_customers,
        "return_transactions_count": return_tx_count,
    }
