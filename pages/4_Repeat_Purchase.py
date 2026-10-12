"""
Flux — Repeat Purchase Prediction
Module 4: Supervised Repurchase Classification & Propensity Scoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data.loader import load_cached_clean_data
from src.models.repeat_purchase import (
    get_or_train_repeat_model,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)
from src.models.evaluation import plot_confusion_matrix, plot_feature_importances
from src.utils.ui import (
    apply_editorial_theme,
    render_header,
    render_card,
    configure_plotly_figure,
)
from src.config import PLOTLY_PALETTE, THEME_COLORS

st.set_page_config(
    page_title="Repeat Purchase Prediction — Flux",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_editorial_theme()

render_header(
    title="Repeat Purchase Propensity",
    subtitle="Time-aware supervised classification predicting 30-day customer re-order likelihood with zero data leakage.",
    tag="PREDICTIVE BEHAVIOURAL MODEL"
)

# Load Clean Sales Data
try:
    df_sales = load_cached_clean_data()
except Exception as e:
    st.error(f"Error loading clean dataset: {e}")
    st.stop()

# Sidebar Controls
with st.sidebar:
    st.markdown('<div class="ui-label">MODEL SETTINGS</div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    selected_model_type = st.radio("Active Classifier", ["Random Forest", "Logistic Regression"], index=0)
    force_retrain = st.button("Retrain Chronological Pipeline", type="secondary")

# Model Training / Loading
with st.spinner("Extracting historical snapshots and evaluating classifiers..."):
    artifact, snap_df = get_or_train_repeat_model(df_sales, force_retrain=force_retrain)

metrics = artifact["metrics"]
model_key = "random_forest" if selected_model_type == "Random Forest" else "logistic_regression"
active_metrics = metrics[model_key]

# Executive Metrics Row
p1, p2, p3, p4, p5, p6 = st.columns(6)
with p1:
    st.metric("Test Cohort Size", f"{metrics['test_sample_size']:,}")
with p2:
    st.metric("Positive Base Rate", f"{metrics['test_positive_rate']*100:.1f}%")
with p3:
    st.metric("Precision", f"{active_metrics['precision']*100:.1f}%")
with p4:
    st.metric("Recall", f"{active_metrics['recall']*100:.1f}%")
with p5:
    st.metric("F1-Score", f"{active_metrics['f1']:.3f}")
with p6:
    st.metric("ROC-AUC", f"{active_metrics['roc_auc']:.3f}")

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# Problem Formulation & Chronological Split Narrative
formulation_html = fr"""
<div style="font-size: 0.88rem; color: #1C1917; line-height: 1.7;">
    <b>Unit of Prediction:</b> Customer active during the 90-day lookback window prior to snapshot date.<br/>
    <b>Historical Features:</b> Strictly extracted from <code>[T - 90 days, T]</code>. Zero future observations leak into feature vectors.<br/>
    <b>Target Definition ($Y=1$):</b> Made $\ge 1$ verified purchase during the subsequent 30 days <code>[T, T + 30 days]</code>.<br/>
    <b>Held-Out Test Cutoff:</b> Snapshot evaluated strictly at <code>{artifact['test_snapshot_date'][:10]}</code>. Baseline majority accuracy: <b>{metrics['baseline']['accuracy']*100:.1f}%</b>.
</div>
"""
render_card(title="TIME-AWARE EXPERIMENTAL FORMULATION", content_html=formulation_html, badge="LEAKAGE-FREE")

# Diagnostic Plots Row: Confusion Matrix & Feature Importances
st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
c_cm, c_fi = st.columns(2, gap="medium")

with c_cm:
    fig_cm = plot_confusion_matrix(
        active_metrics["confusion_matrix"],
        title=f"Held-Out Confusion Matrix ({selected_model_type})",
    )
    st.plotly_chart(fig_cm, use_container_width=True)

with c_fi:
    fig_fi = plot_feature_importances(metrics["feature_importances"], top_n=7)
    st.plotly_chart(fig_fi, use_container_width=True)

# Interactive Customer Propensity Scoring
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
st.markdown('<div class="ui-label">CUSTOMER-LEVEL PROPENSITY INFERENCE</div>', unsafe_allow_html=True)

c_input, c_result = st.columns([1, 2], gap="large")

with c_input:
    cust_list = snap_df["customer_id"].unique().tolist()
    chosen_cust = st.selectbox(
        "Select Customer from Evaluation Snapshot",
        options=cust_list,
        index=0,
    )
    
    cust_record = snap_df[snap_df["customer_id"] == chosen_cust].iloc[0]
    
    st.markdown(
        f"""
        <div class="flux-card" style="margin-top: 0.5rem;">
            <div class="ui-label">LOOKBACK FEATURES (T - 90d)</div>
            <table style="width: 100%; font-size: 0.82rem; color: #78716C; margin-top: 0.5rem;">
                <tr><td>Days Since Purchase:</td><td style="color: #1C1917; text-align: right;"><b>{cust_record['recency_days']}d</b></td></tr>
                <tr><td>Orders in Lookback:</td><td style="color: #1C1917; text-align: right;"><b>{cust_record['orders_count']}</b></td></tr>
                <tr><td>Spend in Lookback:</td><td style="color: #1C1917; text-align: right;"><b>£{cust_record['total_spend']:,.2f}</b></td></tr>
                <tr><td>Average Order Value:</td><td style="color: #1C1917; text-align: right;"><b>£{cust_record['avg_order_value']:.2f}</b></td></tr>
                <tr><td>Catalog Variety:</td><td style="color: #1C1917; text-align: right;"><b>{cust_record['unique_products']} items</b></td></tr>
                <tr><td>Market:</td><td style="color: #1C1917; text-align: right;"><b>{cust_record['market_group']}</b></td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_result:
    # Generate inference
    pipeline = artifact["pipeline"] if selected_model_type == "Random Forest" else artifact["lr_pipeline"]
    feature_row = pd.DataFrame([cust_record[NUMERIC_FEATURES + CATEGORICAL_FEATURES]])
    prob = float(pipeline.predict_proba(feature_row)[0, 1])
    pred_class = int(pipeline.predict(feature_row)[0])
    
    propensity_label = "HIGH PROPENSITY" if prob >= 0.65 else ("MODERATE PROPENSITY" if prob >= 0.40 else "LOW PROPENSITY")
    badge_color = "#059669" if prob >= 0.65 else ("#D97706" if prob >= 0.40 else "#78716C")

    st.markdown(
        f"""
        <div class="flux-card">
            <div class="ui-label">INFERRED FUTURE REPURCHASE PROPENSITY</div>
            <div style="display: flex; align-items: baseline; gap: 1rem; margin: 0.5rem 0;">
                <span style="font-size: 2.4rem; font-weight: 850; color: #1C1917;">{prob*100:.1f}%</span>
                <span style="font-size: 0.85rem; font-weight: 600; color: {badge_color}; text-transform: uppercase;">
                    {propensity_label}
                </span>
            </div>
            <div style="background-color: #F5F5F4; border-radius: 4px; height: 8px; width: 100%; margin-bottom: 1rem; overflow: hidden;">
                <div style="background-color: #1C1917; height: 100%; width: {prob*100:.1f}%;"></div>
            </div>
            <div style="font-size: 0.85rem; color: #78716C; line-height: 1.6;">
                <b>Commercial Interpretation:</b> This customer exhibits an estimated <b>{prob*100:.1f}%</b> probability of completing a follow-on order within the subsequent 30 calendar days. 
                Historical actual outcome on held-out window: <b>{'Repurchased' if cust_record['target_repurchase'] == 1 else 'Did not repurchase'}</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Model Governance & Strategic Trade-offs
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
with st.expander("Model Governance, Trade-offs & Strategic Limitations"):
    st.markdown(
        """
        - **Probabilistic Framing:** Model output represents estimated propensity ($P(Y=1|X)$) under historical assumptions, never deterministic certainty.
        - **Precision vs. Recall Trade-off:** 
          - *High Precision Priority:* Minimizes unnecessary retention discounts to customers who would have purchased anyway.
          - *High Recall Priority:* Captures maximum potential churners at the cost of higher promotional expense.
        - **Chronological Validity:** Training exclusively on pre-November 2011 transactions and evaluating on the November–December holiday lead-up provides true out-of-time generalisation testing.
        """
    )
