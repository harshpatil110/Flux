"""
RFM (Recency, Frequency, Monetary) feature extraction service for Flux.
"""

from typing import Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np

def calculate_rfm(
    sales_df: pd.DataFrame,
    reference_date: Optional[datetime] = None,
) -> pd.DataFrame:
    """
    Computes customer-level RFM metrics from valid sales transactions.

    Rules:
    - Only identified customers (non-null customer_id) are included.
    - Recency: Days from reference_date to customer's latest purchase.
    - Frequency: Count of distinct valid order IDs (invoice_no), not line items.
    - Monetary: Total spend across all valid orders.
    - Reference date defaults to max(invoice_date) + 1 day to ensure non-negative recency.
    """
    # Filter to identified customer records only
    cust_df = sales_df.dropna(subset=["customer_id"]).copy()
    if cust_df.empty:
        return pd.DataFrame(columns=["customer_id", "recency", "frequency", "monetary", "country"])

    cust_df["customer_id"] = cust_df["customer_id"].astype(str)

    # Reference Date calculation
    if reference_date is None:
        max_tx_date = cust_df["invoice_date"].max()
        ref_date = max_tx_date + pd.Timedelta(days=1)
    else:
        ref_date = pd.to_datetime(reference_date)

    # Group by customer
    rfm = cust_df.groupby("customer_id").agg(
        recency=("invoice_date", lambda d: int((ref_date - d.max()).days)),
        frequency=("invoice_no", "nunique"),
        monetary=("line_total", "sum"),
        first_purchase=("invoice_date", "min"),
        last_purchase=("invoice_date", "max"),
        country=("country", "first"),
    ).reset_index()

    rfm["monetary"] = rfm["monetary"].round(2)
    rfm["aov"] = (rfm["monetary"] / rfm["frequency"]).round(2)
    rfm["tenure_days"] = (ref_date - rfm["first_purchase"]).dt.days

    return rfm
