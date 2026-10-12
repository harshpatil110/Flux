# Flux Data Cleaning & Audit Report

## 1. Summary of Pipeline Execution
- **Input Raw Rows:** 541,909
- **Cleaned Valid Sales Rows:** 524,878
- **Retained Cancellation/Return Rows:** 10,587
- **Total Gross Revenue (£):** £10,642,110.80
- **Analysis Time Window:** 2010-12-01 08:26:00 to 2011-12-09 12:50:00

## 2. Row Exclusion & Audit Breakdown

| Rule Applied | Count Affected | Rationale | Destination |
|---|---|---|---|
| **Exact Duplicates** | 5,268 | Redundant identical records across all columns | Dropped |
| **Cancellations & Returns ('C' / Qty < 0)** | 10,587 | Negative quantities / return vouchers | Preserved in `online_retail_cancellations.parquet` |
| **Zero or Negative Unit Price** | 1,176 | Non-sale administrative / manual adjustments | Excluded from commercial transactions |
| **Zero Quantities** | 0 | Non-order stock movements | Excluded from sales |

## 3. Customer Identification Status
- **Transactions with Customer ID:** 392,692 (Available for RFM & Prediction)
- **Transactions with Missing Customer ID:** 132,186 (Retained for macro revenue & aggregate EDA, excluded from RFM/ML)
- **Distinct Identified Customers:** 4,338
- **Distinct Valid Invoices:** 19,960
- **Distinct Valid Products:** 3,922
- **Distinct Countries:** 38
