"""
Flux — Customer Purchase Behaviour Analysis
Executive Entrypoint and System Status Portal
"""

import streamlit as st
import os
from pathlib import Path
from src.config import WORKBOOK_PATH, WORKSHEET_NAME, THEME_COLORS, PROJECT_ROOT
from src.utils.ui import apply_editorial_theme, render_header, render_card

# Streamlit Page Setup
st.set_page_config(
    page_title="Flux — Customer Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Warm Editorial Minimalism Theme
apply_editorial_theme()

# Sidebar Brand
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1.5rem 0; border-bottom: 1px solid #E7E5E4; margin-bottom: 1rem;">
            <div style="font-size: 1.25rem; font-weight: 800; letter-spacing: -0.03em; color: #1C1917;">
                FLUX ◈
            </div>
            <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #78716C; margin-top: 0.2rem;">
                Retail Intelligence Studio
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="font-size: 0.8rem; color: #78716C; margin-bottom: 1.5rem;">
            <b>Workbook:</b> <code>{WORKBOOK_PATH.name}</code><br/>
            <b>Sheet:</b> <code>{WORKSHEET_NAME}</code>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Page Header
render_header(
    title="Customer Purchase Behaviour",
    subtitle="A rigorous, data-grounded exploration of retail transactions, customer clusters, and repeat affinity.",
    tag="EXECUTIVE OVERVIEW & DATA STATUS"
)

# Workbook Discovery & Health Check
col_status, col_nav = st.columns([1, 1], gap="large")

with col_status:
    st.markdown('<div class="ui-label" style="margin-bottom: 0.5rem;">SOURCE WORKBOOK STATUS</div>', unsafe_allow_html=True)
    
    if WORKBOOK_PATH.exists():
        file_size_mb = WORKBOOK_PATH.stat().st_size / (1024 * 1024)
        status_html = f"""
        <div style="line-height: 1.8; color: #1C1917; font-size: 0.95rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #059669;"></span>
                <b style="color: #059669; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.05em;">Workbook Verified & Ready</b>
            </div>
            <div style="color: #78716C; font-size: 0.85rem; margin-bottom: 0.5rem;">
                Source file successfully detected at relative location:
            </div>
            <div style="background-color: #F5F5F4; padding: 0.5rem 0.75rem; border-radius: 4px; font-family: monospace; font-size: 0.82rem; margin-bottom: 0.75rem;">
                {WORKBOOK_PATH.relative_to(PROJECT_ROOT)}
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                <tr><td style="color: #78716C; padding: 0.25rem 0;">File Size:</td><td><b>{file_size_mb:.2f} MB</b></td></tr>
                <tr><td style="color: #78716C; padding: 0.25rem 0;">Target Worksheet:</td><td><code>{WORKSHEET_NAME}</code></td></tr>
                <tr><td style="color: #78716C; padding: 0.25rem 0;">Engine:</td><td><code>openpyxl / pandas</code></td></tr>
            </table>
        </div>
        """
        render_card(title="DATA INGESTION HEALTH", content_html=status_html, badge="VERIFIED")
    else:
        missing_html = f"""
        <div style="color: #DC2626; line-height: 1.6;">
            <b>Source Workbook Not Found</b><br/>
            Expected path: <code>{WORKBOOK_PATH}</code><br/><br/>
            <span style="color: #78716C; font-size: 0.85rem;">
                Please ensure <code>Online Retail.xlsx</code> is located in the project root directory or set the 
                <code>FLUX_WORKBOOK_PATH</code> environment variable.
            </span>
        </div>
        """
        render_card(title="DATA INGESTION HEALTH", content_html=missing_html, badge="ACTION REQUIRED")

with col_nav:
    st.markdown('<div class="ui-label" style="margin-bottom: 0.5rem;">ANALYTICAL MODULES</div>', unsafe_allow_html=True)
    
    modules_html = """
    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
        <div style="border-left: 2px solid #1C1917; padding-left: 0.75rem;">
            <b style="font-size: 0.9rem;">1. Retail Overview & KPIs</b><br/>
            <span style="font-size: 0.82rem; color: #78716C;">Macro revenue, valid orders, unique customers, temporal trends and country distributions.</span>
        </div>
        <div style="border-left: 2px solid #93C5FD; padding-left: 0.75rem;">
            <b style="font-size: 0.9rem;">2. Customer Segmentation (RFM)</b><br/>
            <span style="font-size: 0.82rem; color: #78716C;">Unsupervised K-Means clustering across Recency, Frequency, and Monetary dimensions.</span>
        </div>
        <div style="border-left: 2px solid #78716C; padding-left: 0.75rem;">
            <b style="font-size: 0.9rem;">3. Market Basket Analysis</b><br/>
            <span style="font-size: 0.82rem; color: #78716C;">Product affinity discovery using Apriori/FP-Growth, lift metrics, and cross-sell bundles.</span>
        </div>
        <div style="border-left: 2px solid #D97706; padding-left: 0.75rem;">
            <b style="font-size: 0.9rem;">4. Repeat Purchase Prediction</b><br/>
            <span style="font-size: 0.82rem; color: #78716C;">Leakage-safe supervised classification predicting future 30-day customer re-order propensity.</span>
        </div>
        <div style="border-left: 2px solid #059669; padding-left: 0.75rem;">
            <b style="font-size: 0.9rem;">5. Data Explorer & Audit</b><br/>
            <span style="font-size: 0.82rem; color: #78716C;">Transparent cleaning audit, row reconciliation, cancellation summaries, and filtered export.</span>
        </div>
    </div>
    """
    render_card(title="NAVIGATION GUIDE", content_html=modules_html, badge="5 MODULES")

st.markdown("<hr style='border: none; border-top: 1px solid #E7E5E4; margin: 2rem 0;'/>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: left; font-size: 0.82rem; color: #78716C;">
        Flux Customer Intelligence Platform • Follows Warm Editorial Minimalism design specifications • Zero artificial data.
    </div>
    """,
    unsafe_allow_html=True
)
