"""
Data cleaning and transformation pipeline for Flux.
Provides transparent, auditable cleaning with exact reason tracking.
"""

from pathlib import Path
from typing import Tuple, Dict, Any
import json
import pandas as pd
import numpy as np

from src.config import (
    PROCESSED_DATA_DIR,
    CLEANED_DATA_PARQUET,
    CLEANED_DATA_CSV,
    CLEANING_AUDIT_JSON,
    DOCS_DIR,
)
from src.data.loader import load_raw_data
from src.data.validation import validate_cleaned_dataset

def clean_dataset(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Cleans raw transactions dataset and partitions valid sales and cancellations.

    Returns:
        valid_sales_df: Cleaned positive sales transactions.
        cancellations_df: Returns / cancelled transactions.
        audit_metrics: Dictionary tracking input count, dropped counts per rule, and output counts.
    """
    total_raw_rows = len(raw_df)
    df = raw_df.copy()

    # 1. Deduplication
    duplicate_count = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)

    # 2. Text Normalization
    df["stock_code"] = df["stock_code"].astype(str).str.strip()
    df["description"] = df["description"].astype(str).str.strip()
    df["country"] = df["country"].astype(str).str.strip()
    df["invoice_no"] = df["invoice_no"].astype(str).str.strip()

    # 3. Clean and Cast CustomerID
    # Store customer_id as clean nullable string (e.g., '17850')
    def format_cust_id(val):
        if pd.isnull(val):
            return None
        try:
            return str(int(float(val)))
        except (ValueError, TypeError):
            return None

    df["customer_id"] = df["customer_id"].apply(format_cust_id)
    missing_customer_count = int(df["customer_id"].isnull().sum())

    # 4. Safe Types and Dates
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0.0)

    # 5. Identify Cancellations / Returns vs. Valid Sales
    # Cancellation criteria: invoice starts with 'C' OR quantity < 0
    is_cancellation = df["invoice_no"].str.startswith("C", na=False) | (df["quantity"] < 0)
    cancellation_rows_count = int(is_cancellation.sum())

    # Separate cancellations
    cancellations_df = df[is_cancellation].copy()
    cancellations_df["return_quantity"] = cancellations_df["quantity"].abs()
    cancellations_df["return_amount"] = (cancellations_df["return_quantity"] * cancellations_df["unit_price"]).round(2)

    # Candidate valid sales
    sales_df = df[~is_cancellation].copy()

    # 6. Filter Invalid Non-Positive Prices & Zero Quantities
    zero_or_neg_price_mask = sales_df["unit_price"] <= 0
    zero_price_count = int(zero_or_neg_price_mask.sum())
    sales_df = sales_df[~zero_or_neg_price_mask].copy()

    zero_qty_mask = sales_df["quantity"] <= 0
    zero_qty_count = int(zero_qty_mask.sum())
    sales_df = sales_df[~zero_qty_mask].copy()

    # 7. Derived Features
    sales_df["line_total"] = (sales_df["quantity"] * sales_df["unit_price"]).round(2)
    sales_df["year_month"] = sales_df["invoice_date"].dt.to_period("M").astype(str)
    sales_df["invoice_date_only"] = sales_df["invoice_date"].dt.date
    sales_df["day_of_week"] = sales_df["invoice_date"].dt.day_name()
    sales_df["hour_of_day"] = sales_df["invoice_date"].dt.hour

    # Reset index
    sales_df = sales_df.reset_index(drop=True)
    cancellations_df = cancellations_df.reset_index(drop=True)

    # Validate output
    validate_cleaned_dataset(sales_df)

    audit_metrics = {
        "total_raw_rows": total_raw_rows,
        "exact_duplicates_removed": duplicate_count,
        "unique_raw_rows": total_raw_rows - duplicate_count,
        "cancellations_and_returns": cancellation_rows_count,
        "zero_or_negative_price_excluded": zero_price_count,
        "zero_quantity_excluded": zero_qty_count,
        "valid_completed_sales_rows": len(sales_df),
        "valid_sales_missing_customer_id": int(sales_df["customer_id"].isnull().sum()),
        "valid_sales_with_customer_id": int(sales_df["customer_id"].notnull().sum()),
        "unique_valid_invoices": int(sales_df["invoice_no"].nunique()),
        "unique_valid_products": int(sales_df["stock_code"].nunique()),
        "unique_valid_customers": int(sales_df["customer_id"].dropna().nunique()),
        "unique_countries": int(sales_df["country"].nunique()),
        "date_min": str(sales_df["invoice_date"].min()),
        "date_max": str(sales_df["invoice_date"].max()),
        "gross_sales_volume_gbp": float(round(sales_df["line_total"].sum(), 2)),
    }

    return sales_df, cancellations_df, audit_metrics

def run_cleaning_pipeline() -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    """
    Executes end-to-end cleaning, persists artifacts to data/processed/, and writes audit report.
    """
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    raw_df = load_raw_data()
    clean_sales, cancellations_df, audit = clean_dataset(raw_df)

    # Persist clean sales
    try:
        clean_sales.to_parquet(CLEANED_DATA_PARQUET, index=False)
    except Exception:
        pass
    clean_sales.to_csv(CLEANED_DATA_CSV, index=False)

    # Persist cancellations
    cancellations_parquet = PROCESSED_DATA_DIR / "online_retail_cancellations.parquet"
    cancellations_csv = PROCESSED_DATA_DIR / "online_retail_cancellations.csv"
    try:
        cancellations_df.to_parquet(cancellations_parquet, index=False)
    except Exception:
        pass
    cancellations_df.to_csv(cancellations_csv, index=False)

    # Persist audit JSON
    with open(CLEANING_AUDIT_JSON, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

    # Generate Markdown audit report
    report_md_path = DOCS_DIR / "cleaning-audit-report.md"
    report_content = f"""# Flux Data Cleaning & Audit Report

## 1. Summary of Pipeline Execution
- **Input Raw Rows:** {audit['total_raw_rows']:,}
- **Cleaned Valid Sales Rows:** {audit['valid_completed_sales_rows']:,}
- **Retained Cancellation/Return Rows:** {audit['cancellations_and_returns']:,}
- **Total Gross Revenue (£):** £{audit['gross_sales_volume_gbp']:,.2f}
- **Analysis Time Window:** {audit['date_min']} to {audit['date_max']}

## 2. Row Exclusion & Audit Breakdown

| Rule Applied | Count Affected | Rationale | Destination |
|---|---|---|---|
| **Exact Duplicates** | {audit['exact_duplicates_removed']:,} | Redundant identical records across all columns | Dropped |
| **Cancellations & Returns ('C' / Qty < 0)** | {audit['cancellations_and_returns']:,} | Negative quantities / return vouchers | Preserved in `online_retail_cancellations.parquet` |
| **Zero or Negative Unit Price** | {audit['zero_or_negative_price_excluded']:,} | Non-sale administrative / manual adjustments | Excluded from commercial transactions |
| **Zero Quantities** | {audit['zero_quantity_excluded']:,} | Non-order stock movements | Excluded from sales |

## 3. Customer Identification Status
- **Transactions with Customer ID:** {audit['valid_sales_with_customer_id']:,} (Available for RFM & Prediction)
- **Transactions with Missing Customer ID:** {audit['valid_sales_missing_customer_id']:,} (Retained for macro revenue & aggregate EDA, excluded from RFM/ML)
- **Distinct Identified Customers:** {audit['unique_valid_customers']:,}
- **Distinct Valid Invoices:** {audit['unique_valid_invoices']:,}
- **Distinct Valid Products:** {audit['unique_valid_products']:,}
- **Distinct Countries:** {audit['unique_countries']:,}
"""
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return clean_sales, cancellations_df, audit

if __name__ == "__main__":
    sales, cancels, audit = run_cleaning_pipeline()
    print("Cleaning pipeline complete!")
    print(f"Clean sales: {len(sales):,} rows")
    print(f"Cancellations: {len(cancels):,} rows")
    print(f"Audit: {audit}")
