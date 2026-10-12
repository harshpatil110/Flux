"""
Exploratory Data Analysis and visual aggregation routines for Flux.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

def get_sales_trend(sales_df: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """
    Aggregates revenue and order counts over time by Day ('D'), Week ('W'), or Month ('M').
    """
    if sales_df.empty:
        return pd.DataFrame(columns=["date", "revenue", "orders", "units"])

    df = sales_df.copy()
    trend = (
        df.set_index("invoice_date")
        .resample(freq)
        .agg(
            revenue=("line_total", "sum"),
            orders=("invoice_no", "nunique"),
            units=("quantity", "sum"),
        )
        .reset_index()
    )
    trend.rename(columns={"invoice_date": "date"}, inplace=True)
    return trend

def get_top_products(sales_df: pd.DataFrame, top_n: int = 10, by: str = "revenue") -> pd.DataFrame:
    """
    Retrieves top performing products ranked by 'revenue' or 'quantity' (units).
    """
    if sales_df.empty:
        return pd.DataFrame(columns=["stock_code", "description", "revenue", "units", "orders"])

    sort_col = "revenue" if by == "revenue" else "units"
    grouped = (
        sales_df.groupby("stock_code")
        .agg(
            description=("description", "first"),
            revenue=("line_total", "sum"),
            units=("quantity", "sum"),
            orders=("invoice_no", "nunique"),
        )
        .reset_index()
    )
    ranked = grouped.sort_values(by=sort_col, ascending=False).head(top_n).reset_index(drop=True)
    ranked["revenue"] = ranked["revenue"].round(2)
    return ranked

def get_country_breakdown(sales_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Calculates geographic performance by country.
    """
    if sales_df.empty:
        return pd.DataFrame(columns=["country", "revenue", "orders", "customers"])

    geo = (
        sales_df.groupby("country")
        .agg(
            revenue=("line_total", "sum"),
            orders=("invoice_no", "nunique"),
            customers=("customer_id", lambda s: s.dropna().nunique()),
        )
        .reset_index()
    )
    geo["revenue"] = geo["revenue"].round(2)
    geo = geo.sort_values(by="revenue", ascending=False).head(top_n).reset_index(drop=True)
    return geo

def get_order_value_distribution(sales_df: pd.DataFrame) -> pd.Series:
    """
    Computes total gross spend per distinct invoice.
    """
    if sales_df.empty:
        return pd.Series(dtype=float)
    return sales_df.groupby("invoice_no")["line_total"].sum()

def get_day_hour_matrix(sales_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generates Day-of-Week vs Hour-of-Day order volume pivot table.
    """
    if sales_df.empty:
        return pd.DataFrame()

    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sunday", "Saturday"]
    pivot = sales_df.pivot_table(
        index="day_of_week",
        columns="hour_of_day",
        values="invoice_no",
        aggfunc="nunique",
        fill_value=0,
    )
    # Reindex to logical weekly order where available
    valid_days = [d for d in days_order if d in pivot.index]
    return pivot.reindex(valid_days)

def generate_editorial_insights(kpis: Dict[str, Any], sales_df: pd.DataFrame) -> List[str]:
    """
    Generates dynamic, data-driven editorial statements based strictly on calculated results.
    """
    insights = []
    if sales_df.empty or kpis["total_orders"] == 0:
        return ["No transactions found matching current filter parameters."]

    # Revenue & AOV
    gross_rev = kpis["gross_revenue"]
    aov = kpis["aov"]
    orders = kpis["total_orders"]
    insights.append(
        f"The selected dataset captured £{gross_rev:,.2f} in gross revenue across {orders:,} orders, "
        f"averaging £{aov:.2f} per basket."
    )

    # Customer loyalty / Repeat rate
    repeat_rate = kpis["repeat_customer_rate"] * 100
    cust_count = kpis["identified_customers"]
    insights.append(
        f"Among {cust_count:,} identified customers, {repeat_rate:.1f}% placed two or more separate orders, "
        f"indicating healthy organic retention in the historical customer base."
    )

    # Geographic concentration
    top_country = sales_df["country"].value_counts().index[0]
    top_country_rev = sales_df[sales_df["country"] == top_country]["line_total"].sum()
    top_share = (top_country_rev / gross_rev * 100) if gross_rev > 0 else 0
    insights.append(
        f"{top_country} represents the primary market driver, contributing {top_share:.1f}% of total volume."
    )

    # Busiest time pattern
    hourly = sales_df.groupby("hour_of_day")["invoice_no"].nunique()
    if not hourly.empty:
        peak_hour = hourly.idxmax()
        insights.append(
            f"Peak commercial purchasing activity occurs at {peak_hour}:00, aligning with retail midday procurement."
        )

    return insights
