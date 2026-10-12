"""
Flux — Customer Segmentation
Module 2: Unsupervised RFM Clustering & Behavioural Typologies
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data.loader import load_cached_clean_data
from src.analytics.rfm import calculate_rfm
from src.models.segmentation import (
    get_or_train_rfm_segments,
    evaluate_clusters,
    FEATURE_COLS,
)
from src.utils.ui import (
    apply_editorial_theme,
    render_header,
    render_card,
    configure_plotly_figure,
)
from src.config import PLOTLY_PALETTE, THEME_COLORS

st.set_page_config(
    page_title="Customer Segmentation — Flux",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_editorial_theme()

render_header(
    title="Customer Segmentation",
    subtitle="Unsupervised K-Means clustering across Recency, Frequency, and Monetary behavioural dimensions.",
    tag="BEHAVIOURAL TYPOLOGIES"
)

# Load Clean Data
try:
    df_sales = load_cached_clean_data()
except Exception as e:
    st.error(f"Error loading clean dataset: {e}")
    st.stop()

# Sidebar Controls
with st.sidebar:
    st.markdown('<div class="ui-label">SEGMENTATION SETTINGS</div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    
    k_clusters = st.slider("Number of Clusters (k)", min_value=2, max_value=6, value=4)
    force_retrain = st.button("Re-evaluate & Fit Model", type="secondary")

# Run Segmentation
with st.spinner("Analyzing customer behavioral patterns..."):
    rfm_segments, artifact = get_or_train_rfm_segments(
        df_sales,
        n_clusters=k_clusters,
        force_retrain=force_retrain,
    )

# Executive Cluster Profile Summary
st.markdown('<div class="ui-label" style="margin-bottom: 0.75rem;">IDENTIFIED BEHAVIOURAL PROFILES</div>', unsafe_allow_html=True)

profile_cols = st.columns(k_clusters)
cluster_stats = rfm_segments.groupby("segment_name").agg(
    count=("customer_id", "count"),
    revenue=("monetary", "sum"),
    med_recency=("recency", "median"),
    med_freq=("frequency", "median"),
    med_spend=("monetary", "median"),
).reset_index()

total_rev = rfm_segments["monetary"].sum()
total_cust = len(rfm_segments)

for idx, row in cluster_stats.iterrows():
    col = profile_cols[idx % k_clusters]
    rev_share = (row["revenue"] / total_rev * 100) if total_rev > 0 else 0
    cust_share = (row["count"] / total_cust * 100) if total_cust > 0 else 0
    
    with col:
        st.markdown(
            f"""
            <div class="flux-card" style="height: 100%;">
                <div class="ui-label" style="color: #1C1917; font-size: 0.78rem;">{row['segment_name']}</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #1C1917; margin: 0.4rem 0;">
                    {row['count']:,} <span style="font-size: 0.8rem; font-weight: 400; color: #78716C;">({cust_share:.1f}%)</span>
                </div>
                <div style="font-size: 0.85rem; color: #78716C; margin-bottom: 0.5rem;">
                    Revenue: <b>£{row['revenue']:,.0f}</b> ({rev_share:.1f}%)
                </div>
                <hr style="border: none; border-top: 1px solid #F5F5F4; margin: 0.5rem 0;" />
                <table style="font-size: 0.78rem; width: 100%; color: #78716C;">
                    <tr><td>Med. Recency:</td><td style="color: #1C1917; text-align: right;"><b>{int(row['med_recency'])}d</b></td></tr>
                    <tr><td>Med. Orders:</td><td style="color: #1C1917; text-align: right;"><b>{int(row['med_freq'])}</b></td></tr>
                    <tr><td>Med. Spend:</td><td style="color: #1C1917; text-align: right;"><b>£{row['med_spend']:,.0f}</b></td></tr>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Visual Distribution & Cluster Projections
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
v_tab1, v_tab2, v_tab3 = st.tabs(["2D Feature Space (R vs M)", "3D Space Projection", "Model Diagnostics (Elbow / Silhouette)"])

with v_tab1:
    fig_2d = px.scatter(
        rfm_segments,
        x="recency",
        y="monetary",
        size="frequency",
        color="segment_name",
        hover_data=["customer_id", "frequency", "country"],
        labels={"recency": "Recency (Days Since Last Order)", "monetary": "Monetary Value (£)"},
        color_discrete_sequence=PLOTLY_PALETTE,
        log_y=True,
    )
    fig_2d.update_layout(height=480, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
    configure_plotly_figure(fig_2d)
    st.plotly_chart(fig_2d, use_container_width=True)

with v_tab2:
    fig_3d = px.scatter_3d(
        rfm_segments.sample(n=min(len(rfm_segments), 2000), random_state=42),
        x="recency",
        y="frequency",
        z="monetary",
        color="segment_name",
        hover_data=["customer_id"],
        labels={"recency": "Recency", "frequency": "Orders", "monetary": "Spend (£)"},
        color_discrete_sequence=PLOTLY_PALETTE,
        log_z=True,
    )
    fig_3d.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_3d, use_container_width=True)

with v_tab3:
    eval_df = evaluate_clusters(rfm_segments, k_range=range(2, 7))
    e_col1, e_col2 = st.columns(2)
    with e_col1:
        fig_elbow = px.line(
            eval_df,
            x="k",
            y="inertia",
            markers=True,
            title="Inertia by Cluster Count (Elbow Method)",
            labels={"k": "Number of Clusters (k)", "inertia": "Sum of Squared Distances"},
        )
        fig_elbow.update_traces(line_color="#1C1917", marker=dict(size=8, color="#1C1917"))
        configure_plotly_figure(fig_elbow)
        st.plotly_chart(fig_elbow, use_container_width=True)
    with e_col2:
        fig_sil = px.line(
            eval_df,
            x="k",
            y="silhouette",
            markers=True,
            title="Silhouette Coefficient by Cluster Count",
            labels={"k": "Number of Clusters (k)", "silhouette": "Silhouette Score"},
        )
        fig_sil.update_traces(line_color="#3B82F6", marker=dict(size=8, color="#3B82F6"))
        configure_plotly_figure(fig_sil)
        st.plotly_chart(fig_sil, use_container_width=True)

# Customer Drill-down & Lookup
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
st.markdown('<div class="ui-label">INDIVIDUAL CUSTOMER DRILL-DOWN</div>', unsafe_allow_html=True)

c_search, c_details = st.columns([1, 2], gap="large")

with c_search:
    top_cust_options = rfm_segments["customer_id"].tolist()
    selected_cust_id = st.selectbox(
        "Search or Select Customer ID",
        options=top_cust_options,
        index=0,
    )
    
    cust_row = rfm_segments[rfm_segments["customer_id"] == selected_cust_id].iloc[0]
    
    st.markdown(
        f"""
        <div class="flux-card" style="margin-top: 0.5rem;">
            <div class="ui-label">CUSTOMER PROFILE: #{cust_row['customer_id']}</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #1C1917; margin: 0.4rem 0;">
                <span class="flux-badge">{cust_row['segment_name']}</span>
            </div>
            <table style="width: 100%; font-size: 0.85rem; color: #78716C; margin-top: 0.75rem;">
                <tr><td style="padding: 0.2rem 0;">Country:</td><td style="color: #1C1917; text-align: right;"><b>{cust_row['country']}</b></td></tr>
                <tr><td style="padding: 0.2rem 0;">Total Spend:</td><td style="color: #1C1917; text-align: right;"><b>£{cust_row['monetary']:,.2f}</b></td></tr>
                <tr><td style="padding: 0.2rem 0;">Order Count:</td><td style="color: #1C1917; text-align: right;"><b>{cust_row['frequency']}</b></td></tr>
                <tr><td style="padding: 0.2rem 0;">Average Basket:</td><td style="color: #1C1917; text-align: right;"><b>£{cust_row['aov']:.2f}</b></td></tr>
                <tr><td style="padding: 0.2rem 0;">Days Since Last Order:</td><td style="color: #1C1917; text-align: right;"><b>{cust_row['recency']} days</b></td></tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c_details:
    st.markdown('<div class="ui-label">RECENT TRANSACTION HISTORY</div>', unsafe_allow_html=True)
    cust_txs = df_sales[df_sales["customer_id"] == selected_cust_id].sort_values(
        by="invoice_date", ascending=False
    )[["invoice_no", "invoice_date", "stock_code", "description", "quantity", "unit_price", "line_total"]].head(10)
    
    st.dataframe(cust_txs, use_container_width=True, hide_index=True)

# Export & Limitations
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
col_exp, col_lim = st.columns([1, 2], gap="large")

with col_exp:
    render_card(
        title="DOWNLOAD SEGMENTS",
        content_html=f"""
        <div style="font-size: 0.85rem; color: #78716C; margin-bottom: 0.75rem;">
            Export the complete customer segmentation database ({len(rfm_segments):,} records) with cluster labels as CSV.
        </div>
        """,
        badge="EXPORT"
    )
    seg_csv = rfm_segments[["customer_id", "country", "recency", "frequency", "monetary", "aov", "segment_name"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Customer Segments CSV",
        data=seg_csv,
        file_name="flux_customer_segments.csv",
        mime="text/csv",
    )

with col_lim:
    with st.expander("Clustering Methodology & Limitations"):
        st.markdown(
            """
            - **Statistical Grouping:** Customer segments represent unsupervised geometric partitions in normalized log-space, not permanent behavioral traits.
            - **Arbitrary Cluster Identifiers:** Cluster numbers have no mathematical order; labels are applied through centroid rank ordering.
            - **Historical Scope:** Metrics represent the recorded 2010–2011 period and should not be misconstrued as real-time consumer status.
            - **Log Transformation:** Applied via $\\log(1 + x)$ to stabilize heavy right-skewed revenue and order counts prior to standard scaling.
            """
        )
