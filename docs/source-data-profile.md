# Source Data Profile Report: Online Retail

## 1. File & Workbook Identification
- **Source File:** `Online Retail.xlsx`
- **File Size:** ~23.7 MB (23,715,344 bytes)
- **Worksheet Name:** `Online Retail`
- **Total Rows:** 541,909
- **Total Columns:** 8

## 2. Schema & Inferred Data Types

| Column Name | Inferred Dtype | Canonical Field Mapping | Description |
|---|---|---|---|
| `InvoiceNo` | `object` | `invoice_no` | Invoice number. 6-digit integer or prefixed with 'C' for cancellations. |
| `StockCode` | `object` | `stock_code` | Product/item code (nominal alphanumeric, e.g. '85123A', 'POST'). |
| `Description`| `object` | `description` | Product name / text description. |
| `Quantity` | `int64` | `quantity` | Quantities per transaction line. Negative for returns/cancellations. |
| `InvoiceDate`| `datetime64[ns]` | `invoice_date` | Timestamp of invoice generation. |
| `UnitPrice` | `float64` | `unit_price` | Unit price in GBP (£) sterling. |
| `CustomerID` | `float64` | `customer_id` | 5-digit customer identifier. |
| `Country` | `object` | `country` | Country where customer resides. |

## 3. Data Quality & Missingness

| Metric | Count | % of Total | Notes |
|---|---|---|---|
| **Missing CustomerID** | 135,080 | 24.93% | Must be retained for macro sales aggregates, but excluded from customer RFM and repeat-purchase prediction. |
| **Missing Description** | 1,454 | 0.27% | Mostly internal stock adjustments or administrative lines. |
| **Duplicate Rows** | 5,268 | 0.97% | Exact duplicates across all columns; should be de-duplicated during cleaning. |
| **Cancelled Invoices ('C')** | 9,288 | 1.71% | Invoices starting with 'C' (indicating customer returns). |
| **Negative Quantities** | 10,624 | 1.96% | Correspond to cancellations or damaged inventory adjustments. |
| **Zero or Negative Prices** | 2,517 | 0.46% | Administrative adjustments, samples, bad debt, or Amazon fees. |

## 4. Key Distributions & Cardinality
- **Date Range:** `2010-12-01 08:26:00` to `2011-12-09 12:50:00` (~1 year + 9 days).
- **Unique Invoices:** 25,900
- **Unique Products (`StockCode`):** 4,070
- **Unique Customers (Identified):** 4,372
- **Unique Countries:** 38
- **Top 5 Countries by Volume:**
  1. United Kingdom: 495,478 rows (91.4%)
  2. Germany: 9,495 rows (1.75%)
  3. France: 8,557 rows (1.58%)
  4. EIRE: 8,196 rows (1.51%)
  5. Spain: 2,533 rows (0.47%)

## 5. Cleaning Rules Required
1. **Deduplication:** Remove 5,268 exact duplicate rows.
2. **Text Normalization:** Strip whitespace from `StockCode`, `Description`, `Country`.
3. **Cancellation & Return Partitioning:**
   - Mark cancellations where `InvoiceNo` starts with 'C' or `Quantity < 0`.
   - Separate valid completed sales from cancellation/returns so both can be accurately measured (Gross Sales vs Returns vs Net Sales).
4. **Invalid Prices & StockCodes:** Exclude non-product administrative records with `UnitPrice <= 0` or non-standard stock codes (e.g. 'D', 'DOT', 'AMAZONFEE', 'CR') from product affinity/basket analysis.
5. **Customer ID Casting:** Convert float customer IDs (e.g. 17850.0) into clean integer strings (`17850`), with explicit `None`/NaN representation.
6. **Line Total Derivation:** `line_total = quantity * unit_price`.
