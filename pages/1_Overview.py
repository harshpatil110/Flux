"""
Flux — Retail Overview & Exploratory Intelligence
Module 1: Macro KPIs, Sales Dynamics, Geography & Temporal Trends
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.data.loader import load_cached_clean_data
from src.analytics.kpis import calculate_macro_kpis
from src.analytics.eda import (
    get_sales_trend,
    get_top_products,
    get_country_breakdown,
    get_day_hour_matrix,
    generate_editorial_insights,
)
from src.utils.ui import (
    apply_editorial_theme,
    render_header,
    render_card,
    configure_plotly_figure,
)
from src.config import PLOTLY_PALETTE, THEME_COLORS

st.set_page_config(
    page_title="Retail Overview — Flux",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_editorial_theme()

# Header
render_header(
    title="Commercial Overview",
    subtitle="Macro transaction metrics, demand pacing, geographic concentration, and catalog dynamics.",
    tag="EXECUTIVE REPORTING"
)

# Load Cleaned Data
try:
    df_sales = load_cached_clean_data()
except Exception as e:
    st.error(f"Error loading clean dataset: {e}")
    st.stop()

# Cancellations for return metrics
cancellations_path = df_sales = df_sales # fallback
try:
    from src.config import PROCESSED_DATA_DIR
    cancels_file = PROCESSED_DATA_DIR / "online_retail_cancellations.parquet"
    if cancels_file.exists():
        df_cancels = pd.read_parquet(cancels_file)
    else:
        df_cancels = None
except Exception:
    df_cancels = None

# Sidebar Filters
with st.sidebar:
    st.markdown('<div class="ui-label">DATA FILTERS</div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Date Filter
    min_date = df_sales["invoice_date"].min().date()
    max_date = df_sales["invoice_date"].max().date()
    
    selected_dates = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Country Filter
    countries = ["All Countries"] + sorted(df_sales["country"].dropna().unique().tolist())
    selected_country = st.selectbox("Market / Country", countries, index=0)

    # Reset / Refresh
    st.markdown("<hr style='border: none; border-top: 1px solid #E7E5E4; margin: 1.5rem 0;'/>", unsafe_allow_html=True)
    if st.button("Reload Pipeline Cache", type="secondary"):
        st.cache_data.clear()
        st.rerun()

# Apply Filters
start_date = selected_dates[0] if isinstance(selected_dates, (tuple, list)) and len(selected_dates) > 0 else min_date
end_date = selected_dates[1] if isinstance(selected_dates, (tuple, list)) and len(selected_dates) > 1 else max_date

filtered_sales = df_sales[
    (df_sales["invoice_date"].dt.date >= start_date) &
    (df_sales["invoice_date"].dt.date <= end_date)
]
if selected_country != "All Countries":
    filtered_sales = filtered_sales[filtered_sales["country"] == selected_country]

# Filter cancellations similarly
filtered_cancels = None
if df_cancels is not None and not df_cancels.empty:
    filtered_cancels = df_cancels[
        (df_cancels["invoice_date"].dt.date >= start_date) &
        (df_cancels["invoice_date"].dt.date <= end_date)
    ]
    if selected_country != "All Countries":
        filtered_cancels = filtered_cancels[filtered_cancels["country"] == selected_country]

# Calculate KPIs
kpis = calculate_macro_kpis(filtered_sales, filtered_cancels)

# Metric Row
m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1:
    st.metric("Gross Revenue", f"£{kpis['gross_revenue']:,.0f}")
with m2:
    st.metric("Valid Orders", f"{kpis['total_orders']:,}")
with m3:
    st.metric("Average Basket", f"£{kpis['aov']:.2f}")
with m4:
    st.metric("Customers", f"{kpis['identified_customers']:,}")
with m5:
    st.metric("Units Sold", f"{kpis['units_sold']:,}")
with m6:
    st.metric("Repeat Rate", f"{kpis['repeat_customer_rate']*100:.1f}%")

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

# Editorial Insight Callout
insights = generate_editorial_insights(kpis, filtered_sales)
insight_html = "".join([f"<p style='margin: 0.35rem 0; color: #1C1917;'>• {item}</p>" for item in insights])
render_card(title="EXECUTIVE NARRATIVE", content_html=insight_html, badge="CALCULATED")

# Chart Row 1: Sales Dynamics Over Time
st.markdown('<div class="ui-label" style="margin-top: 1.5rem; margin-bottom: 0.5rem;">TEMPORAL REVENUE VELOCITY</div>', unsafe_allow_html=True)
c_trend, c_geo = st.columns([2, 1], gap="medium")

with c_trend:
    freq_choice = st.radio("Aggregation Frequency", ["Weekly", "Daily", "Monthly"], horizontal=True, index=0)
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "M"}
    trend_df = get_sales_trend(filtered_sales, freq=freq_map[freq_choice])

    if not trend_df.empty:
        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Bar(
                x=trend_df["date"],
                y=trend_df["revenue"],
                name="Revenue (£)",
                marker_color="#1C1917",
                opacity=0.9,
            )
        )
        fig_trend.add_trace(
            go.Scatter(
                x=trend_df["date"],
                y=trend_df["orders"],
                name="Orders",
                yaxis="y2",
                line=dict(color="#3B82F6", width=2),
            )
        )
        fig_trend.update_layout(
            yaxis2=dict(
                title=dict(text="Orders", font=dict(color="#3B82F6")),
                overlaying="y",
                side="right",
                showgrid=False,
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=380,
        )
        configure_plotly_figure(fig_trend)
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("No temporal records in this filter window.")

with c_geo:
    st.markdown('<div class="ui-label">TOP MARKETS BY VOLUME</div>', unsafe_allow_html=True)
    geo_df = get_country_breakdown(filtered_sales, top_n=6)
    if not geo_df.empty:
        fig_geo = px.bar(
            geo_df,
            x="revenue",
            y="country",
            orientation="h",
            color_discrete_sequence=["#93C5FD"],
            labels={"revenue": "Revenue (£)", "country": "Market"},
        )
        fig_geo.update_layout(yaxis=dict(autorange="reversed"), height=380)
        configure_plotly_figure(fig_geo)
        st.plotly_chart(fig_geo, use_container_width=True)

# Chart Row 2: Top Catalog Products & Day/Hour Patterns
c_prod, c_time = st.columns([1, 1], gap="medium")

with c_prod:
    st.markdown('<div class="ui-label">TOP CATALOG PERFORMERS</div>', unsafe_allow_html=True)
    rank_by = st.selectbox("Rank Catalog By", ["Revenue (£)", "Units Sold"], index=0)
    top_prods = get_top_products(
        filtered_sales,
        top_n=8,
        by="revenue" if rank_by == "Revenue (£)" else "quantity"
    )
    if not top_prods.empty:
        fig_prod = px.bar(
            top_prods,
            x="revenue" if rank_by == "Revenue (£)" else "units",
            y="description",
            orientation="h",
            color_discrete_sequence=["#1C1917"],
            labels={"description": "Item", "revenue": "Revenue (£)", "units": "Quantity"},
        )
        fig_prod.update_layout(
            yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
            height=360,
        )
        configure_plotly_figure(fig_prod)
        st.plotly_chart(fig_prod, use_container_width=True)

with c_time:
    st.markdown('<div class="ui-label">PURCHASING CADENCE (DAY VS HOUR)</div>', unsafe_allow_html=True)
    day_hour_df = get_day_hour_matrix(filtered_sales)
    if not day_hour_df.empty:
        fig_heat = px.imshow(
            day_hour_df,
            color_continuous_scale=[[0, "#F7F5F0"], [0.5, "#BFDBFE"], [1, "#1C1917"]],
            labels=dict(x="Hour of Day", y="Day of Week", color="Orders"),
            aspect="auto",
        )
        fig_heat.update_layout(height=360)
        configure_plotly_figure(fig_heat)
        st.plotly_chart(fig_heat, use_container_width=True)

# Methodology & Download Tray
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
col_down, col_def = st.columns([1, 2], gap="large")

with col_down:
    render_card(
        title="DATA EXPORT",
        content_html=f"""
        <div style="font-size: 0.85rem; color: #78716C; margin-bottom: 0.75rem;">
            Export the current filtered transaction subset ({len(filtered_sales):,} lines) as CSV.
        </div>
        """,
        badge="CSV"
    )
    csv_data = filtered_sales.head(5000).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Sample CSV (5,000 Rows)",
        data=csv_data,
        file_name=f"flux_overview_{start_date}_{end_date}.csv",
        mime="text/csv",
    )

with col_def:
    with st.expander("Methodology & Mathematical Definitions"):
        st.markdown(
            """
            - **Gross Revenue:** Calculated strictly as $\\sum (\\text{quantity} \\times \\text{unit\\_price})$ for completed commercial transactions ($Q > 0, P > 0$).
            - **Cancellations & Returns:** Identified via `InvoiceNo` starting with `'C'` or $Q < 0$. These are isolated in the cancellation ledger to prevent misstating completed sales.
            - **Net Revenue:** $\\text{Gross Revenue} - \\text{Refund Amount}$.
            - **Repeat Rate:** Percentage of identified customers possessing 2 or more distinct order IDs. Customers without an assigned Customer ID are excluded from customer-level metrics.
            - **AOV (Average Order Value):** $\\text{Gross Revenue} / \\text{Unique Invoices}$.
            """
        )
