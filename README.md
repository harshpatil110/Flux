# FLUX — Customer Purchase Behaviour Analysis Platform

Flux is a high-performance, interactive customer intelligence platform built using Streamlit and Python. Designed with a bespoke **Warm Editorial Minimalism** aesthetic inspired by architectural publications and product catalogs, Flux transforms raw transactional data into actionable commercial insights, unsupervised behavioral clusters, cross-selling affinities, and leakage-free repeat-purchase predictions.

---

## ◈ Product Capabilities

1. **Executive Overview & Commercial Reporting (`1_Overview.py`):**
   - Verified macro KPIs: Gross Revenue (£10.64M), Valid Orders (19,960), Average Order Value (£533.17), Unique Customers (4,338), Units Sold (5.58M), and Repeat Customer Rate (69.6%).
   - Dynamic temporal pacing charts (Daily, Weekly, Monthly) with dual-axis order counts.
   - Geographic market breakdown and catalog volume leaderboards.
   - 24/7 Day-vs-Hour purchasing intensity heatmaps and dynamic plain-language narrative insights.

2. **Customer Segmentation & RFM Typologies (`2_Customer_Segmentation.py`):**
   - Recency, Frequency, and Monetary feature extraction from completed transactions.
   - Log-transformed and standard-scaled K-Means clustering ($k=4$, silhouette score = 0.338).
   - Data-driven behavioral typologies: *Champions / High-Value Loyal*, *Active Regulars*, *Occasional / Promising*, and *Hibernating / At Risk*.
   - Interactive 2D/3D cluster projections, elbow/silhouette diagnostics, customer search drill-down, and CSV segment exports.

3. **Market Basket Analysis & Product Affinity (`3_Product_Affinity.py`):**
   - High-performance frequent itemset mining via FP-Growth and Apriori algorithms (`mlxtend`).
   - Dynamic support, confidence, and lift thresholds.
   - Data-driven cross-selling bundle recommendations with measurable lift multipliers (e.g. 15x–35x cross-sell lift).
   - Interactive rule space scatter plot, association rule leaderboard, and CSV download.

4. **Repeat Purchase Propensity Prediction (`4_Repeat_Purchase.py`):**
   - Time-aware, leakage-free supervised classification problem formulation.
   - Features strictly extracted from $[T - 90\text{d}, T]$; target evaluated strictly on future window $[T, T + 30\text{d}]$.
   - Chronological out-of-time evaluation on held-out test cohort ($N=2,461$).
   - Model comparison: Random Forest (ROC-AUC: 0.718, F1: 0.620, Recall: 63.7%) vs. Logistic Regression vs. Baseline.
   - Diagnostic confusion matrix, feature importance rankings, and individual customer propensity scoring.

5. **Data Explorer & Audit Ledger (`5_Data_Explorer.py`):**
   - Full provenance inspection: 541,909 raw rows ingested, 5,268 exact duplicates removed, 10,587 cancellations partitioned, and 524,878 valid sales verified.
   - Searchable, filterable transaction browser with multi-column filtering and CSV export.
   - Transparent returns and cancellations ledger.

---

## ◈ Repository Architecture

```text
Flux/
├── Online Retail.xlsx                  # Source workbook (preserved completely unchanged)
├── app.py                             # Executive Portal and Streamlit entry point
├── assets/
│   └── custom.css                     # Warm Editorial Minimalism design system tokens
├── pages/
│   ├── 1_Overview.py                  # Macro sales & exploratory analysis
│   ├── 2_Customer_Segmentation.py     # RFM features & K-Means clustering
│   ├── 3_Product_Affinity.py          # Market Basket Analysis & association rules
│   ├── 4_Repeat_Purchase.py           # Supervised repeat-purchase classification
│   └── 5_Data_Explorer.py             # Schema audit, record browser & cancellations ledger
├── src/
│   ├── config.py                      # Central relative paths, settings & theme tokens
│   ├── data/
│   │   ├── loader.py                  # Cached Excel/Parquet data loader
│   │   ├── validation.py              # Schema assertions & integrity validator
│   │   └── cleaning.py                # Auditable data cleaning & partition pipeline
│   ├── analytics/
│   │   ├── kpis.py                    # Resilient business metric formulas
│   │   ├── eda.py                     # Aggregations, trends & dynamic insights
│   │   ├── rfm.py                     # Customer-level RFM feature extractor
│   │   └── basket.py                  # Transaction matrix & rule mining engine
│   ├── models/
│   │   ├── segmentation.py            # K-Means training, profiling & evaluation
│   │   ├── repeat_purchase.py         # Snapshot builder & chronological classifier
│   │   └── evaluation.py              # Confusion matrix & feature importance visuals
│   └── utils/
│       └── ui.py                      # Editorial styling, card components & Plotly theme
├── data/
│   └── processed/
│       ├── online_retail_clean.parquet        # High-performance clean sales cache
│       ├── online_retail_clean.csv            # Clean sales CSV fallback
│       ├── online_retail_cancellations.parquet# Partitioned return records
│       └── cleaning_audit.json                # Audit breakdown and row reconciliation
├── models/
│   ├── kmeans_rfm.joblib              # Persisted RFM scaler & K-Means model bundle
│   └── repeat_purchase_model.joblib   # Persisted repeat-purchase pipeline & metrics
├── docs/
│   ├── design-implementation-notes.md # UI design tokens mapped to Streamlit/CSS
│   ├── source-data-profile.md         # Comprehensive empirical profile of source Excel
│   ├── cleaning-audit-report.md       # Exact counts and rationale for row filtering
│   └── project-validation-report.md   # Final end-to-end verification and testing report
├── tests/
│   ├── conftest.py                    # Test configuration and path setup
│   ├── test_loader_and_cleaning.py    # Unit tests for ingestion and cleaning
│   └── test_analytics_and_models.py   # Unit tests for KPIs, RFM, baskets & ML
├── requirements.txt                   # Complete project dependencies
└── README.md
```

---

## ◈ Quick Start & Installation

### 1. Requirements
- Python 3.10+ (tested on Python 3.12.6)
- Dependencies in `requirements.txt`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

### 4. Running the Automated Test Suite
```bash
python -m pytest tests/ -v
```

---

## ◈ Methodology & Definitions

- **Gross Revenue:** $\sum (\text{quantity} \times \text{unit\_price})$ for valid completed orders ($\text{Quantity} > 0, \text{UnitPrice} > 0$, non-cancellation).
- **Cancellations & Returns:** Invoices starting with `'C'` or transactions with $\text{Quantity} < 0$. These are partitioned into a dedicated ledger rather than subtracted silently.
- **Net Revenue:** $\text{Gross Revenue} - \text{Refund Amount}$.
- **Average Order Value (AOV):** $\text{Gross Revenue} / \text{Unique Invoices}$.
- **Repeat Rate:** Percentage of identified customers placing $\ge 2$ distinct orders.
- **RFM Features:**
  - *Recency:* Elapsed days between fixed analysis reference date and customer's latest purchase.
  - *Frequency:* Count of distinct order IDs (invoices), not line items.
  - *Monetary:* Total customer spend.
- **Leakage Prevention in Predictive Modeling:**
  - Historical snapshots are established at chronological cutoffs (June, July, September, November 2011).
  - Lookback window: $[T - 90\text{d}, T]$ strictly informs feature generation.
  - Target label: $[T, T + 30\text{d}]$ strictly determines whether the customer repurchased.
  - Chronological split: Model evaluated exclusively on held-out November 2011 snapshot.

---

## ◈ License & Provenance
Built for the Antigravity pair programming workspace. All analysis is driven strictly by real transactional data in `Online Retail.xlsx`. Zero artificial data is fabricated.
