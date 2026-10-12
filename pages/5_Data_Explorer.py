"""
Flux — Data Explorer & Audit Ledger
Module 5: Transparent Schema Audit, Data Quality Reconciliation & Filterable Record Browser
"""

import streamlit as st
import pandas as pd
import json

from src.data.loader import load_cached_clean_data
from src.config import (
    CLEANING_AUDIT_JSON,
    PROCESSED_DATA_DIR,
    WORKBOOK_PATH,
    WORKSHEET_NAME,
)
from src.utils.ui import (
    apply_editorial_theme,
    render_header,
    render_card,
)

st.set_page_config(
    page_title="Data Explorer — Flux",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_editorial_theme()

render_header(
    title="Data Explorer & Audit Ledger",
    subtitle="Full provenance inspection, transparent cleaning audit rules, cancellation records, and interactive filtering.",
    tag="DATA GOVERNANCE & PROVENANCE"
)

# Load Audit JSON
audit_data = {}
if CLEANING_AUDIT_JSON.exists():
    try:
        with open(CLEANING_AUDIT_JSON, "r", encoding="utf-8") as f:
            audit_data = json.load(f)
    except Exception:
        pass

# Load Clean Sales
try:
    df_sales = load_cached_clean_data()
except Exception as e:
    st.error(f"Error loading clean dataset: {e}")
    st.stop()

# Load Cancellations Ledger
cancels_parquet = PROCESSED_DATA_DIR / "online_retail_cancellations.parquet"
cancels_csv = PROCESSED_DATA_DIR / "online_retail_cancellations.csv"
if cancels_parquet.exists():
    df_cancels = pd.read_parquet(cancels_parquet)
elif cancels_csv.exists():
    df_cancels = pd.read_csv(cancels_csv)
else:
    df_cancels = pd.DataFrame()

# Audit Overview Cards
if audit_data:
    st.markdown('<div class="ui-label" style="margin-bottom: 0.75rem;">PIPELINE AUDIT METRICS</div>', unsafe_allow_html=True)
    a1, a2, a3, a4, a5 = st.columns(5)
    with a1:
        st.metric("Raw Rows Ingested", f"{audit_data.get('total_raw_rows', 0):,}")
    with a2:
        st.metric("Duplicates Removed", f"{audit_data.get('exact_duplicates_removed', 0):,}")
    with a3:
        st.metric("Returns Partitioned", f"{audit_data.get('cancellations_and_returns', 0):,}")
    with a4:
        st.metric("Valid Clean Sales", f"{audit_data.get('valid_completed_sales_rows', 0):,}")
    with a5:
        st.metric("Identified Customers", f"{audit_data.get('unique_valid_customers', 0):,}")

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# Tabs: Valid Sales Ledger vs Cancellations Ledger vs Schema Specification
tab_sales, tab_cancels, tab_schema = st.tabs([
    "Valid Commercial Sales",
    "Cancellation & Returns Ledger",
    "Schema & Type Mappings"
])

with tab_sales:
    st.markdown('<div class="ui-label" style="margin-bottom: 0.5rem;">FILTERABLE TRANSACTIONS</div>', unsafe_allow_html=True)
    
    f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
    with f_col1:
        search_query = st.text_input("Search Item / Description", placeholder="e.g. HEART, BAG, T-LIGHT")
    with f_col2:
        cust_filter = st.text_input("Customer ID", placeholder="e.g. 17850")
    with f_col3:
        country_filter = st.selectbox(
            "Filter Country",
            ["All"] + sorted(df_sales["country"].unique().tolist()),
            index=0,
        )

    # Apply filters
    filtered_view = df_sales
    if search_query:
        filtered_view = filtered_view[filtered_view["description"].str.contains(search_query, case=False, na=False)]
    if cust_filter:
        filtered_view = filtered_view[filtered_view["customer_id"] == cust_filter]
    if country_filter != "All":
        filtered_view = filtered_view[filtered_view["country"] == country_filter]

    st.markdown(
        f"<div style='font-size: 0.82rem; color: #78716C; margin: 0.5rem 0;'>Showing <b>{min(len(filtered_view), 500):,}</b> of <b>{len(filtered_view):,}</b> matching records</div>",
        unsafe_allow_html=True,
    )
    
    display_cols = ["invoice_no", "invoice_date", "stock_code", "description", "quantity", "unit_price", "line_total", "customer_id", "country"]
    st.dataframe(
        filtered_view[display_cols].head(500),
        use_container_width=True,
        hide_index=True,
    )
    
    # Download Button
    csv_bytes = filtered_view.head(2000).to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered Results (Up to 2,000 Rows CSV)",
        data=csv_bytes,
        file_name="flux_transactions_export.csv",
        mime="text/csv",
    )

with tab_cancels:
    st.markdown('<div class="ui-label" style="margin-bottom: 0.5rem;">CANCELLATION & RETURN RECORDS</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size: 0.85rem; color: #78716C; margin-bottom: 1rem;">
            Invoices beginning with 'C' or containing negative quantities are preserved in this ledger 
            to ensure return volumes can be audited without distorting positive sales metrics.
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not df_cancels.empty:
        st.dataframe(
            df_cancels[["invoice_no", "invoice_date", "stock_code", "description", "quantity", "unit_price", "return_quantity", "return_amount", "customer_id", "country"]].head(500),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No cancellation records located in processed directory.")

with tab_schema:
    st.markdown('<div class="ui-label" style="margin-bottom: 0.5rem;">SCHEMA SPECIFICATION</div>', unsafe_allow_html=True)
    
    schema_df = pd.DataFrame([
        {"Raw Column": "InvoiceNo", "Canonical Field": "invoice_no", "Storage Type": "string", "Description": "Invoice identifier (numeric or 'C' prefix)"},
        {"Raw Column": "StockCode", "Canonical Field": "stock_code", "Storage Type": "string", "Description": "Nominal product SKU code"},
        {"Raw Column": "Description", "Canonical Field": "description", "Storage Type": "string", "Description": "Product title (whitespace stripped)"},
        {"Raw Column": "Quantity", "Canonical Field": "quantity", "Storage Type": "int64", "Description": "Units per line (>0 in clean sales)"},
        {"Raw Column": "InvoiceDate", "Canonical Field": "invoice_date", "Storage Type": "datetime64", "Description": "Timestamp of order generation"},
        {"Raw Column": "UnitPrice", "Canonical Field": "unit_price", "Storage Type": "float64", "Description": "Unit selling price in GBP (£)"},
        {"Raw Column": "CustomerID", "Canonical Field": "customer_id", "Storage Type": "string (nullable)", "Description": "5-digit customer identifier"},
        {"Raw Column": "Country", "Canonical Field": "country", "Storage Type": "string", "Description": "Customer residency country"},
        {"Derived", "line_total", "float64", "Quantity × UnitPrice", "Total transaction revenue"},
        {"Derived", "year_month", "string", "YYYY-MM", "Monthly period bucket"},
    ])
    st.dataframe(schema_df, use_container_width=True, hide_index=True)
