"""
Flux — Product Affinity & Market Basket Analysis
Module 3: Co-occurrence Discovery, Association Rules & Cross-Sell Bundles
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.data.loader import load_cached_clean_data
from src.analytics.basket import (
    build_basket_matrix,
    run_basket_analysis,
    get_recommendations_for_product,
)
from src.utils.ui import (
    apply_editorial_theme,
    render_header,
    render_card,
    configure_plotly_figure,
)
from src.config import PLOTLY_PALETTE, THEME_COLORS

st.set_page_config(
    page_title="Product Affinity — Flux",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_editorial_theme()

render_header(
    title="Product Affinity Analysis",
    subtitle="Market basket co-occurrence discovery, rule mining, and data-driven cross-selling bundle suggestions.",
    tag="CROSS-MERCHANDISING INTELLIGENCE"
)

# Load Clean Sales Data
try:
    df_sales = load_cached_clean_data()
except Exception as e:
    st.error(f"Error loading clean dataset: {e}")
    st.stop()

# Sidebar Controls
with st.sidebar:
    st.markdown('<div class="ui-label">MARKET BASKET SETTINGS</div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Market selector
    country_opts = ["United Kingdom", "All Countries", "Germany", "France", "EIRE"]
    available_countries = [c for c in country_opts if c == "All Countries" or c in df_sales["country"].values]
    selected_market = st.selectbox("Market Segment", available_countries, index=0)

    min_supp_pct = st.slider("Minimum Support (%)", min_value=0.8, max_value=4.0, value=1.5, step=0.1)
    min_conf_pct = st.slider("Minimum Confidence (%)", min_value=10, max_value=80, value=25, step=5)
    min_lift_val = st.slider("Minimum Lift", min_value=1.1, max_value=10.0, value=1.5, step=0.1)

    use_fpgrowth = st.radio("Mining Algorithm", ["FP-Growth (Fast)", "Apriori"], index=0) == "FP-Growth (Fast)"

# Filter Market
if selected_market != "All Countries":
    market_sales = df_sales[df_sales["country"] == selected_market]
else:
    market_sales = df_sales

@st.cache_data(show_spinner=False)
def get_cached_basket_results(market_key: str, supp: float, conf: float, lift: float, fpg: bool):
    # Pass market_sales indirectly via cache
    basket_mat, code_map = build_basket_matrix(market_sales, min_product_frequency=25)
    itemsets, rules = run_basket_analysis(
        basket_mat,
        min_support=supp,
        min_confidence=conf,
        min_lift=lift,
        use_fpgrowth=fpg,
    )
    return basket_mat.shape, itemsets, rules

with st.spinner("Extracting frequent itemsets and mining association rules..."):
    mat_shape, itemsets, rules = get_cached_basket_results(
        selected_market,
        min_supp_pct / 100.0,
        min_conf_pct / 100.0,
        min_lift_val,
        use_fpgrowth,
    )

# KPI Row
b1, b2, b3, b4 = st.columns(4)
with b1:
    st.metric("Total Baskets", f"{mat_shape[0]:,}")
with b2:
    st.metric("Catalog Products", f"{mat_shape[1]:,}")
with b3:
    st.metric("Frequent Itemsets", f"{len(itemsets):,}")
with b4:
    st.metric("Association Rules", f"{len(rules):,}")

st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

if rules.empty:
    st.warning(
        "No association rules met the specified support/confidence/lift thresholds in this market segment. "
        "Try lowering the Minimum Support or Confidence slider in the sidebar."
    )
else:
    # Rule Space Visualization
    st.markdown('<div class="ui-label" style="margin-bottom: 0.5rem;">ASSOCIATION RULE SPACE (SUPPORT VS CONFIDENCE)</div>', unsafe_allow_html=True)
    
    fig_rules = px.scatter(
        rules.head(100),
        x="support",
        y="confidence",
        size="lift",
        color="lift",
        hover_data=["antecedent_str", "consequent_str", "lift"],
        labels={"support": "Support (Frequency of Occurrence)", "confidence": "Confidence (P(B|A))", "lift": "Lift Multiplier"},
        color_continuous_scale=[[0, "#93C5FD"], [0.5, "#3B82F6"], [1, "#1C1917"]],
    )
    fig_rules.update_layout(height=420)
    configure_plotly_figure(fig_rules)
    st.plotly_chart(fig_rules, use_container_width=True)

    # Cross-Selling & Bundle Suggestions
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="ui-label">DATA-DRIVEN CROSS-SELLING BUNDLES</div>', unsafe_allow_html=True)
    
    col_prod_sel, col_bundle_disp = st.columns([1, 2], gap="large")
    
    with col_prod_sel:
        # Extract unique products from antecedents
        unique_antecedents = sorted(list(set(rules["antecedent_str"].str.split(", ").explode().tolist())))
        selected_prod = st.selectbox(
            "Select Anchor Product",
            options=unique_antecedents,
            index=0 if unique_antecedents else None,
        )
        
        if selected_prod:
            recs = get_recommendations_for_product(selected_prod, rules, top_n=3)
            if not recs.empty:
                st.markdown(
                    f"""
                    <div class="flux-card" style="margin-top: 0.5rem;">
                        <div class="ui-label">PROMOTIONAL BUNDLE CONCEPT</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: #1C1917; margin: 0.5rem 0;">
                            Anchor: <span style="color: #1E40AF;">{selected_prod}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #78716C; line-height: 1.5;">
                            Pair this product at checkout with items having proven cross-order lift to increase Average Order Value.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    
    with col_bundle_disp:
        if selected_prod:
            recs = get_recommendations_for_product(selected_prod, rules, top_n=5)
            if not recs.empty:
                st.markdown('<div class="ui-label">RECOMMENDED COMPLEMENTARY PRODUCTS</div>', unsafe_allow_html=True)
                for _, rec_row in recs.iterrows():
                    lift_val = rec_row['lift']
                    conf_pct = rec_row['confidence'] * 100
                    st.markdown(
                        f"""
                        <div class="flux-card" style="padding: 0.85rem 1.25rem; margin-bottom: 0.6rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="font-size: 0.92rem; font-weight: 600; color: #1C1917;">
                                    {rec_row['consequent_str']}
                                </div>
                                <span class="flux-badge">{lift_val:.1f}x LIFT</span>
                            </div>
                            <div style="font-size: 0.8rem; color: #78716C; margin-top: 0.3rem;">
                                Confidence: <b>{conf_pct:.1f}%</b> • Support: <b>{rec_row['support']*100:.2f}%</b> of all transactions
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info(f"No strong rules found where '{selected_prod}' acts as antecedent at current thresholds.")

    # Ranked Rules Table
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="ui-label">ASSOCIATION RULES LEADERBOARD</div>', unsafe_allow_html=True)
    
    display_rules = rules[["antecedent_str", "consequent_str", "support", "confidence", "lift", "leverage"]].rename(
        columns={
            "antecedent_str": "Antecedent (If Bought)",
            "consequent_str": "Consequent (Then Also Bought)",
            "support": "Support",
            "confidence": "Confidence",
            "lift": "Lift",
            "leverage": "Leverage",
        }
    )
    st.dataframe(display_rules.head(50), use_container_width=True, hide_index=True)

# Export and Non-Causality Methodology
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
col_down, col_meth = st.columns([1, 2], gap="large")

with col_down:
    render_card(
        title="EXPORT RULES",
        content_html=f"""
        <div style="font-size: 0.85rem; color: #78716C; margin-bottom: 0.75rem;">
            Download discovered association rules ({len(rules):,} rules) as CSV.
        </div>
        """,
        badge="EXPORT"
    )
    if not rules.empty:
        rules_csv = rules.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Association Rules CSV",
            data=rules_csv,
            file_name=f"flux_affinity_rules_{selected_market.lower().replace(' ', '_')}.csv",
            mime="text/csv",
        )

with col_meth:
    with st.expander("Methodology & Non-Causality Warning"):
        st.markdown(
            """
            - **Non-Causality:** Association rules measure statistical co-occurrence ($P(B|A)$), not causal determination. Products bought together may share common external causes (e.g. holiday gift packaging or tea sets).
            - **Support:** Proportion of total baskets containing both items: $\\text{Support}(A \\rightarrow B) = \\frac{\\text{freq}(A, B)}{N}$.
            - **Confidence:** Probability that basket contains $B$ given it contains $A$: $\\text{Confidence}(A \\rightarrow B) = \\frac{\\text{Support}(A, B)}{\\text{Support}(A)}$.
            - **Lift:** Ratio of observed joint probability to expected independent probability: $\\text{Lift} = \\frac{\\text{Confidence}(A \\rightarrow B)}{\\text{Support}(B)}$. Values $> 1.0$ indicate positive affinity.
            """
        )
