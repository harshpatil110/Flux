# Flux Project Validation & Handover Report

## 1. Executive Summary
The **Flux** Customer Purchase Behaviour Analysis platform has been designed, implemented, and fully validated across all eight tasks outlined in `task.md`. The application runs cleanly on Streamlit, strictly complies with the **Warm Editorial Minimalism** design system (`design (1).md`), and processes the supplied `Online Retail.xlsx` workbook with full transparency, zero hallucinated data, and no data leakage.

## 2. Validation Checklist Status

| Task | Scope | Deliverables | Verification Status |
|---|---|---|---|
| **Task 1** | Workspace, Design & Workbook Audit | `docs/design-implementation-notes.md`, `docs/source-data-profile.md`, foundation `src/config.py`, starter `app.py`, `.gitignore` | **PASS (100%)** |
| **Task 2** | Ingestion, Validation & Cleaning Pipeline | `src/data/loader.py`, `src/data/validation.py`, `src/data/cleaning.py`, `docs/cleaning-audit-report.md`, parquet cache | **PASS (100%)** |
| **Task 3** | Exploratory Data Analysis & Business KPIs | `src/analytics/kpis.py`, `src/analytics/eda.py`, `pages/1_Overview.py` with Plotly charts and dynamic insights | **PASS (100%)** |
| **Task 4** | Customer Segmentation & RFM Clustering | `src/analytics/rfm.py`, `src/models/segmentation.py`, `models/kmeans_rfm.joblib`, `pages/2_Customer_Segmentation.py` | **PASS (100%)** |
| **Task 5** | Market Basket Analysis & Product Affinity | `src/analytics/basket.py`, `pages/3_Product_Affinity.py` with FP-Growth & Apriori, bundle recommendations | **PASS (100%)** |
| **Task 6** | Repeat Purchase Propensity Prediction | `src/models/repeat_purchase.py`, `src/models/evaluation.py`, `models/repeat_purchase_model.joblib`, `pages/4_Repeat_Purchase.py` | **PASS (100%)** |
| **Task 7** | Full UI Integration & Data Explorer | `pages/5_Data_Explorer.py`, revised `app.py`, consistent warm editorial styling & CSS across all 5 pages | **PASS (100%)** |
| **Task 8** | Testing, Browser Verification & Handover | Pytest test suite (8/8 passing), automated browser walkthrough, `README.md`, `docs/project-validation-report.md` | **PASS (100%)** |

## 3. Data Pipeline & Audit Metrics
- **Source File:** `Online Retail.xlsx` (Preserved completely untouched).
- **Total Raw Rows:** 541,909
- **Exact Duplicates Removed:** 5,268
- **Cancellations & Returns Partitioned:** 10,587 (Saved to `online_retail_cancellations.parquet`)
- **Zero / Negative Unit Prices Excluded:** 1,176
- **Valid Clean Commercial Sales:** 524,878 (Saved to `online_retail_clean.parquet`)
- **Gross Revenue:** £10,642,110.80
- **Identified Customers:** 4,338
- **Distinct Invoices:** 19,960
- **Analysis Window:** 2010-12-01 to 2011-12-09

## 4. Machine Learning & Analytical Model Metrics

### A. RFM K-Means Segmentation
- **Features:** $\log(1 + \text{Recency})$, $\log(1 + \text{Frequency})$, $\log(1 + \text{Monetary})$ with `StandardScaler`.
- **Optimal Clusters:** $k = 4$
- **Silhouette Coefficient:** `0.338` (evaluated against $k \in [2, 7]$).
- **Identified Segments:**
  1. *Champions / High-Value Loyal:* Median spend £2,042, median orders 8, median recency 16d.
  2. *Active Regulars:* Median spend £939, median orders 3, median recency 37d.
  3. *Occasional / Promising:* Median spend £377, median orders 2, median recency 57d.
  4. *Hibernating / At Risk:* Median spend £238, median orders 1, median recency 231d.

### B. Repeat Purchase Classifier (Held-Out Out-of-Time Test Set)
- **Snapshot Formulation:** 90-day lookback for feature generation; 30-day forward window for target calculation.
- **Held-Out Test Cohort Size:** 2,461 customers at November 1, 2011.
- **Positive Repurchase Base Rate:** 41.5%
- **Majority Baseline Accuracy:** 58.5% (Precision: 0.0%, Recall: 0.0%, F1: 0.000)
- **Random Forest Performance:**
  - **Precision:** `60.4%`
  - **Recall:** `63.7%`
  - **F1-Score:** `0.620`
  - **ROC-AUC:** `0.718`
  - **PR-AUC:** `0.639`
- **Key Predictive Drivers:** Days since last purchase (`recency_days`), orders in lookback window (`orders_count`), customer catalog variety (`unique_products`).

## 5. End-to-End Automated Testing & Browser Walkthrough
- **Automated Unit Tests:** 8/8 tests passed in `tests/test_loader_and_cleaning.py` and `tests/test_analytics_and_models.py`.
- **Browser Subagent Session:**
  - Recording artifact: `flux_e2e_test_1791827905456.webp`
  - All 6 routes (`/`, `/Overview`, `/Customer_Segmentation`, `/Product_Affinity`, `/Repeat_Purchase`, `/Data_Explorer`) navigated and visually verified.
  - Zero JavaScript errors, zero runtime exceptions, zero layout overflow.
  - All interactive elements verified: Plotly zoom/hover, dropdown selectors, drill-down customer inspection, cross-selling bundle recommendations, and CSV downloads.
