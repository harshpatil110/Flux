# FLUX — Customer Purchase Behaviour Analysis
## AI IDE Implementation Plan (Antigravity)

> **Project goal:** Build a polished, interactive customer analytics application named **Flux** using Streamlit for the UI and Python for data processing, analytics and machine-learning models. The application must use the existing Online Retail `.xlsx` workbook in the project root and follow the visual direction in the root-level `design.md` file.
>
> **Execution instruction for Antigravity:** Complete the tasks in order. Before implementing the UI, inspect `design.md` and the Excel workbook that already exist in the project root. Do not replace the supplied design with a generic Streamlit theme. Do not create or train on invented business data. Use the real workbook for analysis and model training. Test fixtures may be generated for unit tests only and must never be mixed into the real dataset or displayed as business results.

---

# 0. Project-wide rules and definition of done

These rules apply to all eight tasks.

### Product scope
Flux should provide five connected capabilities:

1. **Retail overview and exploratory analysis:** sales, orders, customers, products, country and time-period insights.
2. **Customer segmentation:** RFM metrics and K-Means clustering to find groups with similar purchase behaviour.
3. **Product association analysis:** Market Basket Analysis using Apriori or FP-Growth to find products commonly purchased together.
4. **Repeat-purchase prediction:** a supervised model that estimates whether a customer is likely to purchase again within a defined future window.
5. **Interactive business dashboard:** clear visualisations, filters, customer/product drill-downs and downloadable results.

### Technical decisions
- **UI:** Streamlit.
- **Language / analytics backend:** Python.
- **Data handling:** Pandas and NumPy; use `openpyxl` or an equivalent Excel engine to read `.xlsx` files.
- **Visualisation:** Plotly for interactive charts. Matplotlib/Seaborn may be used for analysis or static outputs where appropriate.
- **Machine learning:** scikit-learn.
- **Association rules:** `mlxtend` (Apriori / association rules), or FP-Growth if it is more efficient for the actual data.
- **Model persistence:** `joblib`.
- **Configuration:** environment variables or a small config module; do not hardcode local absolute paths.
- **FastAPI:** **not required for the initial version.** Streamlit can call the Python service and model functions directly. Keep analytics/model code independent of Streamlit so a FastAPI service can be added later without rewriting the core logic. Add FastAPI only if a separately deployed API, external client, or independent frontend is actually required.

### Data integrity rules
- Discover the actual workbook filename and worksheet names at the beginning. Do not assume the filename, sheet name, row count or exact column names.
- Inspect the real column names and data types, then create a documented mapping to canonical fields. The expected Online Retail fields commonly include invoice number, stock code, description, quantity, invoice date, unit price, customer ID and country, but verify these in the workbook before coding.
- Preserve the original workbook. Never overwrite or modify it.
- Keep raw, cleaned and derived data separate. Do not silently discard rows: record how many rows are removed or excluded and why.
- Handle cancellations/returns, negative quantities, invalid prices, missing customer IDs, duplicate rows and missing product descriptions explicitly. Keep return/cancellation information available for relevant analysis rather than accidentally counting it as positive sales.
- State the revenue definition clearly. For example, net sales may include returns while gross sales excludes them; use a clearly named metric and be consistent across pages.
- Avoid data leakage. Features for a prediction must be calculated only from information available before the prediction cutoff. Labels must come from the future window.
- Do not fabricate performance metrics, customer segments, recommendations, chart values or business conclusions. Every displayed result must be calculated from the loaded workbook and current filters.
- Use deterministic random seeds for repeatable model training. Save model metadata, feature names, training cutoff and evaluation metrics with each trained model.
- Keep functions small and typed where practical. Add helpful error messages and logging rather than silently failing.

### Suggested repository structure
Adapt this to the existing project rather than deleting files or overwriting a working structure.

```text
Flux/
├── design.md                         # supplied design specification; read first
├── <online_retail_workbook>.xlsx     # supplied source workbook; preserve unchanged
├── app.py                            # Streamlit entry point
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Customer_Segmentation.py
│   ├── 3_Product_Affinity.py
│   ├── 4_Repeat_Purchase.py
│   └── 5_Data_Explorer.py
├── src/
│   ├── config.py
│   ├── data/
│   │   ├── loader.py
│   │   ├── validation.py
│   │   └── cleaning.py
│   ├── analytics/
│   │   ├── kpis.py
│   │   ├── eda.py
│   │   ├── rfm.py
│   │   └── basket.py
│   ├── models/
│   │   ├── segmentation.py
│   │   ├── repeat_purchase.py
│   │   └── evaluation.py
│   └── utils/
│       ├── formatting.py
│       └── logging_config.py
├── assets/                           # only project-owned assets, if needed
├── data/
│   ├── processed/                    # generated clean/features data; not source data
│   └── reports/                      # downloadable/generated report files
├── models/                           # saved model and metadata artefacts
├── tests/
├── requirements.txt
├── README.md
└── .gitignore
```

The exact structure may differ, but maintain a clear separation between UI, data pipeline, analytics, models and tests.

---

# Task 1 — Inspect the workspace, design system and source workbook; establish the Flux foundation

## Objective
Understand the provided project files before implementation. Convert `design.md` into a practical UI specification, inspect the Online Retail workbook, and establish a clean, runnable Streamlit project foundation.

## Work to perform

### A. Inspect the design
1. Read the complete root-level `design.md` before writing page layouts or styling.
2. Extract and document its requirements: visual style, theme, colours, typography, spacing, layout/grid, navigation, cards, buttons, tables, chart treatments, icons, responsive behaviour and any referenced assets.
3. Identify which elements are mandatory and which are optional. Preserve the design's hierarchy and visual language.
4. If `design.md` references images, fonts or assets, check whether they exist in the workspace. Do not invent unavailable assets or use remote assets that may fail at runtime.
5. Create a short internal implementation note such as `docs/design-implementation-notes.md` listing the design tokens and how they map to Streamlit components/CSS.

### B. Inspect the Excel workbook
1. Locate the `.xlsx` workbook in the project root. If there are multiple candidate workbooks, list them and identify the likely Online Retail source without renaming or deleting anything.
2. Inspect available worksheets, dimensions, column names, inferred data types, sample rows, missing values, duplicate rows and date ranges.
3. Confirm which fields can identify an order, product, customer, timestamp, quantity, unit price and country. If column names differ from the common Online Retail schema, map them to canonical names in configuration rather than altering the source workbook.
4. Check whether the workbook is small enough for normal Pandas loading. If not, choose a memory-conscious loading strategy and document it.
5. Produce a data-profile report (for example, `docs/source-data-profile.md`) containing actual findings: filename, sheet, shape, columns, types, null counts, duplicate count, date range and important data-quality observations. Do not guess values.

### C. Set up the application foundation
1. Create or adapt the project structure described above without destroying existing work.
2. Create `requirements.txt` with only required, compatible dependencies.
3. Add central configuration for workbook path, worksheet (if needed), processed-data path, saved-model path, random seed and relevant analysis settings.
4. Create `app.py` with a working Streamlit entry point and initial navigation/layout consistent with the design notes.
5. Add a basic health/status area indicating whether the expected workbook was found and loaded. Errors should explain how to fix a missing or unreadable workbook.
6. Add `.gitignore` entries for Python caches, virtual environments, generated model files and temporary processed data where appropriate. Do not ignore the supplied source workbook without making that a deliberate repository decision.

## Deliverables
- Design implementation notes derived from `design.md`.
- Actual source workbook profile report.
- Project structure and dependency file.
- A Streamlit app that launches successfully and identifies the source workbook.

## Acceptance criteria
- `design.md` was read and its important rules are reflected in the implementation notes.
- The app finds the supplied workbook using a configurable relative path; no absolute path tied to one computer is required.
- Actual workbook sheets, columns, row count and date range are documented from inspection.
- No source file has been modified or replaced.
- The starter app runs with `streamlit run app.py`.

---

# Task 2 — Build a reliable Excel ingestion, validation and cleaning pipeline

## Objective
Turn the supplied workbook into a consistent, reusable transaction dataset that all analytics and models use. Cleaning must be transparent and reproducible.

## Work to perform

### A. Data loading and schema validation
1. Implement a reusable loader in `src/data/loader.py`.
2. Load the configured worksheet and validate that all fields required for the selected analyses are present.
3. Map source column names to canonical names, such as `invoice_no`, `stock_code`, `description`, `quantity`, `invoice_date`, `unit_price`, `customer_id` and `country`, only where those fields exist in the actual workbook.
4. Convert dates and numeric fields safely. Handle invalid date strings and non-numeric values with explicit reporting.
5. Provide a clear error if mandatory fields are missing. Do not continue with misleading or partially calculated results.

### B. Cleaning and business rules
1. Identify and report missing values, duplicates, invalid identifiers and impossible numeric values.
2. Standardise text fields carefully (for example, trim whitespace) without changing product identifiers in a way that merges different products.
3. Detect cancellation invoices and returns using the actual source conventions, including invoice prefixes where applicable and negative quantities. Verify the workbook's conventions rather than relying on one assumption.
4. Separate valid sales lines from cancellation/return lines. Retain a return/cancellation view or summary so the excluded data is not lost from reporting.
5. Exclude rows with missing customer IDs from customer-level segmentation and customer prediction, but keep eligible transaction/product rows for aggregate sales reporting where appropriate.
6. Validate unit prices and quantities. Do not count zero or negative values as ordinary positive sales. Treat these according to documented rules.
7. Create derived line-level measures, including sales amount (`quantity × unit_price`) where appropriate. Name gross sales, net sales and returns distinctly if all are calculated.
8. Create a consistent order/basket identifier and customer identifier based on the actual data.

### C. Caching and auditability
1. Save the cleaned output to `data/processed/` in a suitable format such as Parquet or CSV. Do not save it over the input `.xlsx`.
2. Cache expensive workbook reading/cleaning in Streamlit using a suitable cache function, while allowing the user/developer to refresh the cache when the workbook changes.
3. Save a cleaning summary with input rows, output rows and counts excluded by each rule. Avoid counting the same removed row multiple times in the final total.
4. Add validation checks for empty output, invalid dates, non-positive sale lines, missing keys and inconsistent derived values.
5. Make downstream modules import the same cleaned-data service; do not duplicate independent cleaning logic on each page.

## Deliverables
- Reusable Excel loader and data validator.
- Reproducible cleaning pipeline.
- Cleaned transaction data in a generated processed-data folder.
- Cleaning/audit report containing actual counts and applied rules.

## Acceptance criteria
- The pipeline runs from a single function/command and can be rerun safely.
- Raw data remains unchanged.
- Cancellation/return handling and missing customer-ID handling are documented and testable.
- Each analytics page receives data from the same cleaned-data pipeline.
- Errors are handled visibly and do not produce plausible-looking but incorrect charts.

---

# Task 3 — Build the business analytics and exploratory analysis module

## Objective
Provide the first useful Flux experience: a trustworthy overview of sales and purchasing patterns, with interactive filters and charts based on the cleaned workbook.

## Work to perform

### A. Define and calculate KPIs
Implement reusable calculations in `src/analytics/kpis.py`. At minimum, calculate the metrics supported by the source data:
- Total sales/revenue using a clearly stated definition.
- Number of valid orders/invoices.
- Number of unique identified customers.
- Number of unique products.
- Units sold.
- Average order value.
- Average items per order.
- Repeat-customer count or share, with the definition stated.
- Returns/cancellations summary, if those fields are available.

Guard against divide-by-zero and empty-filter cases. Do not treat transaction lines as orders or customers.

### B. Exploratory analysis
Implement functions in `src/analytics/eda.py` for:
1. Sales by day, week or month.
2. Best-selling products by units and by revenue (show the metric used).
3. Revenue/orders by country.
4. Order value distribution.
5. Customer purchase frequency distribution.
6. New versus returning customer trends, where the data supports a reliable definition.
7. Day-of-week or hour-of-day purchase patterns, if invoice timestamps support that analysis.
8. Return/cancellation trends, if they can be identified reliably.

### C. Interactivity and explanations
1. Add global or page-level filters for date range, country and any other useful dimensions supported by the workbook.
2. Ensure KPIs and charts respond consistently to filters.
3. Add useful hover information, readable axes, sensible sorting and empty-state messages.
4. Add short plain-language insight summaries generated from calculated results. These must describe the visible filtered data, not fixed example text.
5. Include a data-definition/help section explaining how revenue, orders, returning customers and returns are calculated.
6. Where appropriate, allow users to download the filtered summary or chart data as CSV.

## Deliverables
- Reusable KPI and EDA functions.
- Overview/analytics page with interactive charts and filters.
- Metric definitions and data caveats.
- Downloadable analysis data where appropriate.

## Acceptance criteria
- Every KPI reconciles with the cleaned data and its stated definition.
- A filter changes all relevant visualisations and summary values consistently.
- No hardcoded sample metrics or placeholder chart data remain in the finished page.
- Charts are readable, responsive and follow the `design.md` visual direction.

---

# Task 4 — Implement RFM customer analysis and K-Means segmentation

## Objective
Group customers based on purchase behaviour and explain what distinguishes each group. This is the main unsupervised-learning feature of Flux.

## Work to perform

### A. Build customer-level RFM features
Implement `src/analytics/rfm.py` to aggregate the cleaned sales transactions by customer:
- **Recency:** days between a clearly defined analysis/reference date and the customer's most recent valid purchase.
- **Frequency:** number of distinct valid orders/invoices for that customer, not number of transaction lines.
- **Monetary:** total customer spend using the documented sales definition.

The reference date must be explicit, reproducible and later than the latest included transaction. Make the analysis date visible in the UI. Do not use a customer's future purchases when calculating historical features for a historical prediction task.

### B. Prepare features for clustering
1. Inspect the distributions of Recency, Frequency and Monetary values.
2. Handle skew and extreme values with a documented strategy. Consider log transformation, robust scaling or carefully justified winsorisation; do not silently delete high-value customers.
3. Scale features before K-Means.
4. Evaluate sensible cluster counts using inertia/elbow and silhouette score (or another justified method). Do not automatically assume four clusters.
5. Use a deterministic random seed and persist the fitted scaler and K-Means model together with feature order and metadata.
6. Handle small datasets and cases where there are too few distinct customer records to form the requested number of clusters.

### C. Interpret and present clusters
1. Create a customer segmentation table with RFM values and assigned cluster.
2. Profile each cluster using average/median RFM values, customer count and revenue contribution.
3. Assign descriptive labels such as “High-value loyal”, “Recent/occasional”, or “Needs re-engagement” only after inspecting the actual cluster profile. Cluster names must be data-driven, not hardcoded to cluster ID numbers.
4. Visualise the clusters using suitable two-dimensional charts and/or a 3D plot if it improves understanding. Clearly explain that visual projection may not show every dimension.
5. Add a customer lookup/drill-down: select a customer and show their RFM values, segment and recent purchase summary, subject to the source data.
6. Allow download of the customer segment assignments as CSV.

### D. Explain limitations
- A segment is a statistical grouping, not a permanent customer trait.
- Cluster IDs have no inherent meaning and can change between training runs.
- This workbook covers a historical period; labels should not imply current real-world customer status.

## Deliverables
- RFM feature-generation module.
- K-Means training/evaluation and saved artefacts.
- Customer segmentation page with profiles, charts and customer drill-down.
- Downloadable customer-level segment output.

## Acceptance criteria
- Frequency counts distinct orders, not product rows.
- Recency uses one clearly defined reference date.
- Feature transformations and scaling are fitted consistently and saved with the model.
- Cluster count is justified with evaluation evidence.
- Segment labels are based on calculated cluster profiles.
- The user can inspect and download the actual segmentation results.

---

# Task 5 — Build Market Basket Analysis and product affinity discovery

## Objective
Find products that are frequently purchased together and turn those relationships into useful cross-selling and bundle insights.

## Work to perform

### A. Construct transaction baskets
1. Implement `src/analytics/basket.py`.
2. Create one basket per valid invoice/order, with products represented once per invoice unless the chosen algorithm explicitly requires quantities.
3. Use only eligible completed sales orders. Exclude cancellations/returns and invalid product rows according to the cleaning rules.
4. Decide how to handle duplicate product lines within an invoice and document the decision.
5. Provide configuration for minimum transaction/product frequency so the algorithm can be tuned to the actual data volume.

### B. Generate frequent itemsets and rules
1. Use Apriori or FP-Growth from `mlxtend`; choose based on observed runtime and number of distinct products.
2. Generate frequent itemsets with a configurable minimum support.
3. Generate association rules using confidence and lift (and display support as well).
4. Validate rules and remove unhelpful self-pairs or redundant results.
5. Handle the case where no itemsets or useful rules meet the current thresholds.
6. Explain each metric in simple language. Do not call a rule causal: products appearing together does not prove one product caused the other purchase.

### C. Product affinity UI
1. Add interactive controls for support, confidence, lift and maximum products/rules shown.
2. Provide a searchable product selector. When a product is selected, show related products and the corresponding rule metrics.
3. Provide a ranked table of product pairs/rules.
4. Add a useful visual such as a network/relationship view or ranked bar chart, but avoid clutter when there are many products.
5. Add a “bundle ideas” area that translates strong rules into readable suggestions. Make clear that these are data-derived suggestions, not guaranteed sales outcomes.
6. Allow downloading frequent itemsets and association rules as CSV.

## Deliverables
- Transaction-basket generator.
- Frequent itemset and association-rule pipeline.
- Product affinity page with controls, rule explanations and downloads.

## Acceptance criteria
- Baskets are built from valid orders and use the documented return/cancellation policy.
- Support, confidence and lift are calculated by the library/verified implementation and labelled correctly.
- Threshold changes update the results.
- The interface handles no-result cases gracefully.
- All displayed product pairings come from actual transactions in the workbook.

---

# Task 6 — Train and evaluate the repeat-purchase prediction model

## Objective
Add a supervised machine-learning module that estimates whether a customer will make another purchase during a future time window. This module must use a time-aware target construction to prevent leakage.

## Work to perform

### A. Define the prediction problem before training
1. Define a prediction unit: one customer at one historical snapshot date.
2. Define the target explicitly, for example: “Did this customer make at least one valid purchase during the 30 days after the snapshot date?”
3. Choose and document a lookback window (for example, the previous 60 or 90 days) and a future label window (for example, the next 30 days). These are starting points, not fixed requirements; inspect the actual date range and number of eligible customers before selecting them.
4. Build multiple historical customer snapshots if the dataset supports it. Exclude snapshots whose full future label window is not present in the workbook.
5. Do not create labels from purchases that occurred before the snapshot date. Do not use post-snapshot features to predict that snapshot's label.

### B. Engineer leakage-safe customer features
Potential features, calculated strictly from the lookback period:
- Days since last purchase at snapshot date.
- Number of distinct orders in the lookback window.
- Total spend in the lookback window.
- Average order value.
- Total units purchased.
- Number of distinct products/categories (if categories exist; do not invent categories).
- Average days between purchases, where enough history exists.
- Recent change in order frequency/spend, if it can be calculated using only pre-snapshot data.
- Country, if appropriate and encoded safely.

Exclude direct identifiers such as customer ID from model features. Handle missing values and categorical encoding inside a scikit-learn Pipeline so preprocessing is fitted only on training data.

### C. Train and compare models
1. Establish a simple baseline (for example, always predicting the majority class or a simple recency/frequency rule).
2. Train at least two suitable classification models, such as Logistic Regression and Random Forest. Add another model only if it adds a meaningful comparison.
3. Use a chronological/time-based train-validation-test split. Do not use a random split as the sole evaluation for this future-purchase problem.
4. Keep the most recent eligible snapshots for testing and ensure labels do not cross the chosen split boundary in a way that leaks future information.
5. Address class imbalance using appropriate class weights or training-only resampling. Never resample before the train/test split.
6. Tune only using training/validation data. Keep the final test set untouched until final evaluation.

### D. Evaluate and explain the model
Report, at minimum:
- Precision.
- Recall.
- F1-score.
- Confusion matrix.
- ROC-AUC where meaningful; use PR-AUC/precision-recall analysis when positive outcomes are rare.
- Baseline comparison and class distribution.

Explain the trade-off between false positives and false negatives. Add feature importance or model explanation using a valid method for the selected model. Do not claim a customer will definitely purchase; use language such as “estimated likelihood” or “predicted class”.

### E. Save and use the trained pipeline
1. Persist the complete fitted preprocessing/model Pipeline, not just the estimator.
2. Save metadata: feature names/order, target definition, lookback and label windows, training date range, split boundaries, random seed, evaluation metrics and model version.
3. Add a reproducible training script/function. Do not retrain on every Streamlit rerun.
4. In the UI, allow a customer selection and show the prediction only if a valid model is trained and the features can be generated consistently.
5. If the historical dataset does not provide enough valid snapshots or the model performs poorly, show an honest limitation and disable the prediction rather than displaying fabricated predictions.

## Deliverables
- Leakage-safe snapshot/label builder.
- Feature engineering and training pipeline.
- Baseline and model comparison report.
- Saved model pipeline and metadata.
- Repeat-purchase prediction page with evaluation information and customer-level estimates where supported.

## Acceptance criteria
- Target and feature windows are clearly documented.
- Every feature uses information available on or before the snapshot date.
- Evaluation uses a chronological split and compares against a baseline.
- No test data is used for preprocessing, resampling or tuning.
- Model metrics are generated from actual held-out records.
- The UI never implies certainty or shows predictions if the model/data are not valid.

---

# Task 7 — Integrate all modules into the final Flux Streamlit experience

## Objective
Deliver a cohesive, polished application. The UI must follow the supplied `design.md` and make the analysis understandable to a business user, not just a machine-learning developer.

## Work to perform

### A. Apply the supplied design consistently
1. Revisit `design.md` and the design implementation notes from Task 1.
2. Implement the specified colours, typography, spacing, background, navigation, cards, table styles, chart styling, buttons, borders, corner radii and visual hierarchy.
3. Use Streamlit's supported theme/configuration and restrained custom CSS where needed. Keep CSS maintainable and avoid fragile selectors tied to generated element IDs.
4. Use local assets from the project where supplied. Ensure missing optional assets do not break the app.
5. Make the layout work at common desktop and laptop widths. Avoid horizontal overflow, clipped charts and excessively dense tables.

### B. Build coherent navigation and pages
Suggested information architecture (adapt page names/order to `design.md`):
- **Overview:** executive KPIs, sales trends, top products/countries and key calculated insights.
- **Customer Segmentation:** RFM explanation, cluster evaluation/profile, segment visualisation, customer lookup and CSV export.
- **Product Affinity:** Apriori/FP-Growth controls, related products, association rules, bundle suggestions and downloads.
- **Repeat Purchase:** target explanation, training/evaluation metrics, confusion matrix, feature importance and customer-level estimate where supported.
- **Data Explorer:** source-data profile, cleaning summary, filters and a safe preview of processed records.

### C. Interaction quality
1. Use consistent date/country filters where applicable. Make it clear when filters affect only a page or the entire application.
2. Keep filter state sensible across pages where Streamlit supports it.
3. Use loading/progress feedback for expensive model and association-rule operations.
4. Use caching for data loading and deterministic precomputed results. Provide an explicit refresh/retrain action rather than recalculating expensive models on every interaction.
5. Add useful empty states, validation messages, tooltips and explanations for technical terms.
6. Add customer and product search/select controls. Avoid exposing unnecessary personally identifiable information; use customer IDs only where needed for analysis and drill-down.
7. Add CSV download actions for segment assignments, association rules and relevant filtered summaries.
8. Show model training date/version and warn when source data changes and saved artefacts may be stale.

### D. Optional FastAPI decision
Do not add FastAPI merely for appearance. Keep Streamlit calling the reusable Python services directly for this local project. If a real need for a separate API emerges, propose a small FastAPI layer with typed request/response schemas and tests in a separate subtask; do not duplicate business logic between FastAPI and Streamlit.

## Deliverables
- Complete Flux Streamlit application.
- All five functional areas connected to the same data and analytics services.
- Consistent design implementation based on `design.md`.
- Helpful empty/loading/error states and download actions.

## Acceptance criteria
- All pages load and navigation works.
- The application visually follows the supplied design rather than default unstyled Streamlit components.
- UI results are driven by real processed workbook data and saved model artefacts.
  
- No placeholder values, fake customer examples or dead buttons remain.
- App remains usable on typical desktop/laptop screen sizes.

---

# Task 8 — End-to-end testing, quality checks, documentation and final handover

## Objective
Verify that Flux is reproducible, trustworthy and straightforward to run on another machine.

## Work to perform

### A. Automated tests
Add unit tests for:
1. Workbook discovery, schema mapping and required-column validation.
2. Date/numeric conversion and missing-value handling.
3. Return/cancellation identification and revenue calculations.
4. Order/customer/product KPI calculations using small controlled test fixtures.
5. RFM calculations, including distinct-invoice frequency and reference-date logic.
6. Segmentation input validation and model persistence/load.
7. Basket generation, support/confidence/lift output and no-rule cases.
8. Repeat-purchase snapshot/label construction, especially cutoff boundaries and leakage prevention.
9. Model pipeline persistence and prediction schema validation.

Test fixtures may use small artificial records, but mark them as test-only and never mix them with the supplied Online Retail workbook or production dashboard data.

### B. End-to-end validation
1. Start from a clean environment and follow the documented setup instructions.
2. Run the data profile and cleaning process from the original workbook.
3. Train segmentation and basket-analysis artefacts.
4. Train/evaluate the repeat-purchase model if eligible historical snapshots are available.
5. Launch Streamlit and visit every page.
6. Test filters, customer/product lookup, downloads, empty states and failure states.
7. Change the configured workbook path temporarily to verify the app shows a useful missing-file message.
8. Confirm no model retrains on every page interaction or ordinary rerun.
9. Check performance and memory use with the actual workbook. Optimise only where measurement shows a problem.

### C. Documentation and reproducibility
Create/update `README.md` with:
- Project overview and feature list.
- Architecture and folder structure.
- Python version and installation steps.
- How to configure the `.xlsx` path and worksheet.
- How to run the data profile/cleaning pipeline.
- How to train or refresh the segmentation and repeat-purchase models.
- How to launch the Streamlit app.
- Definitions for revenue, order, customer, RFM and repeat purchase.
- Model evaluation results from the real held-out data.
- Dataset limitations, historical date range and known caveats.
- Troubleshooting for Excel engine/dependency, missing columns, memory and model artefacts.

Add a final `docs/project-validation-report.md` with completed tests, actual model metrics, known issues and any feature that was intentionally disabled due to insufficient data or unreliable results.

## Deliverables
- Test suite and test results.
- End-to-end validation report.
- Complete README and reproducible setup/run instructions.
- Final working Flux app.

## Acceptance criteria
- Tests pass in a clean environment, or any failing tests are clearly explained and resolved where possible.
- A new user can set up and launch Flux by following the README.
- Model training and data-cleaning steps are reproducible.
- Reported model metrics come from held-out real-data evaluation.
- Any unsupported feature or data limitation is disclosed instead of hidden.

---

# Recommended execution order and checkpoints

| Order | Task | Main output | Checkpoint before continuing |
|---:|---|---|---|
| 1 | Workspace, design and workbook audit | Design notes, workbook profile, app foundation | Confirm actual workbook schema and design requirements |
| 2 | Data pipeline | Cleaned transaction data and audit report | Verify returns, cancellations, missing IDs and revenue rules |
| 3 | EDA and business analytics | Overview metrics and charts | Reconcile KPIs with cleaned transactions |
| 4 | RFM and K-Means | Customer segments and saved model | Validate RFM definitions and cluster profiles |
| 5 | Market Basket Analysis | Frequent itemsets and association rules | Verify baskets and rule metrics |
| 6 | Repeat-purchase model | Leakage-safe classifier and evaluation | Approve target/window/split and inspect test metrics |
| 7 | Final UI integration | Complete Flux experience | Check every page against `design.md` |
| 8 | Testing and handover | README, tests and validation report | Verify clean setup and end-to-end run |

## Final product definition
Flux is complete when a user can open the app, understand the historical retail dataset, explore sales and customer behaviour, inspect data-driven customer segments, discover products purchased together, review a properly time-evaluated repeat-purchase model (when supported by the data), and export useful results — all within a coherent Streamlit experience that follows the supplied `design.md`.
