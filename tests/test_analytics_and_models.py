"""
Automated unit tests for KPIs, EDA, RFM, Basket analysis, and Repeat Purchase features.
Uses isolated test fixtures.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.analytics.kpis import calculate_macro_kpis
from src.analytics.rfm import calculate_rfm
from src.analytics.basket import build_basket_matrix, run_basket_analysis
from src.models.repeat_purchase import build_customer_snapshots

@pytest.fixture
def sample_sales():
    return pd.DataFrame({
        "invoice_no": ["1001", "1001", "1002", "1003"],
        "stock_code": ["P1", "P2", "P1", "P3"],
        "description": ["Product 1", "Product 2", "Product 1", "Product 3"],
        "quantity": [2, 1, 3, 5],
        "invoice_date": [
            datetime(2011, 5, 1, 10, 0),
            datetime(2011, 5, 1, 10, 0),
            datetime(2011, 5, 15, 14, 0),
            datetime(2011, 5, 20, 16, 0),
        ],
        "unit_price": [10.0, 5.0, 10.0, 4.0],
        "customer_id": ["CUST1", "CUST1", "CUST1", "CUST2"],
        "country": ["United Kingdom", "United Kingdom", "United Kingdom", "France"],
        "line_total": [20.0, 5.0, 30.0, 20.0],
    })

def test_kpi_calculations(sample_sales):
    kpis = calculate_macro_kpis(sample_sales)
    assert kpis["gross_revenue"] == 75.0
    assert kpis["total_orders"] == 3
    assert kpis["identified_customers"] == 2
    assert kpis["units_sold"] == 11
    assert pytest.approx(kpis["aov"], 0.01) == 25.0
    # CUST1 has 2 orders (1001, 1002), CUST2 has 1 order (1003). Repeat rate = 1/2 = 50%
    assert kpis["repeat_customer_rate"] == 0.5

def test_kpi_empty_safeguard():
    empty_df = pd.DataFrame(columns=["invoice_no", "line_total", "quantity", "customer_id", "stock_code"])
    kpis = calculate_macro_kpis(empty_df)
    assert kpis["gross_revenue"] == 0.0
    assert kpis["total_orders"] == 0
    assert kpis["aov"] == 0.0

def test_rfm_calculation(sample_sales):
    ref_date = datetime(2011, 6, 1)
    rfm = calculate_rfm(sample_sales, reference_date=ref_date)

    assert len(rfm) == 2
    cust1 = rfm[rfm["customer_id"] == "CUST1"].iloc[0]
    # CUST1 latest purchase is May 15 14:00. Ref is June 1 -> 16 days
    assert cust1["recency"] == 16
    # Distinct invoices for CUST1: 1001, 1002 -> 2
    assert cust1["frequency"] == 2
    # Monetary spend: 20 + 5 + 30 = 55.0
    assert cust1["monetary"] == 55.0

def test_basket_analysis_matrix_and_rules():
    transactions = pd.DataFrame({
        "invoice_no": ["1", "1", "2", "2", "3", "3", "4"],
        "stock_code": ["A", "B", "A", "B", "A", "B", "A"],
        "description": ["Item A", "Item B", "Item A", "Item B", "Item A", "Item B", "Item A"],
        "quantity": [1, 1, 1, 1, 1, 1, 1],
        "invoice_date": [datetime(2011, 1, 1)] * 7,
        "unit_price": [1.0] * 7,
        "customer_id": ["C1"] * 7,
        "country": ["UK"] * 7,
        "line_total": [1.0] * 7,
    })
    # build matrix with min_product_frequency=1
    matrix, _ = build_basket_matrix(transactions, min_product_frequency=1)
    assert matrix.shape[0] == 4  # 4 distinct invoices
    assert matrix.shape[1] == 2  # Item A, Item B

    itemsets, rules = run_basket_analysis(matrix, min_support=0.5, min_confidence=0.5, min_lift=1.0)
    assert not itemsets.empty
    assert not rules.empty
    assert "Item A" in rules["antecedent_str"].values or "Item B" in rules["antecedent_str"].values

def test_repeat_purchase_snapshot_no_leakage(sample_sales):
    # Snapshot at 2011-05-10
    # CUST1 had order on 2011-05-01 (lookback), and repurchase on 2011-05-15 (future window)
    snapshots = [pd.Timestamp("2011-05-10")]
    snap_df = build_customer_snapshots(sample_sales, snapshots, lookback_days=30, label_days=30)

    assert len(snap_df) == 1
    cust1_snap = snap_df.iloc[0]
    assert cust1_snap["customer_id"] == "CUST1"
    # Target should be 1 because CUST1 purchased on May 15
    assert cust1_snap["target_repurchase"] == 1
    # Features must reflect ONLY May 1 purchase: 1 order, spend £25
    assert cust1_snap["orders_count"] == 1
    assert cust1_snap["total_spend"] == 25.0
