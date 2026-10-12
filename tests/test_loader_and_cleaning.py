"""
Automated unit tests for data loader, validation, and cleaning pipeline.
Uses controlled test fixtures only (never mutates real workbook).
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.data.validation import validate_raw_schema, validate_cleaned_dataset, ValidationError
from src.data.cleaning import clean_dataset

@pytest.fixture
def sample_raw_data():
    """Generates a small controlled raw transactions DataFrame with known edge cases."""
    return pd.DataFrame({
        "InvoiceNo": ["536365", "536365", "C536366", "536367", "536368", "536368"],
        "StockCode": ["85123A", "85123A", "85123A", "71053", "84406B", "84406B"],
        "Description": ["WHITE HANGING HEART", "WHITE HANGING HEART", "RETURN HEART", "LANTERN", "CREST", "CREST"],
        "Quantity": [6, 6, -2, 10, 0, -5],
        "InvoiceDate": [
            datetime(2011, 1, 1, 10, 0),
            datetime(2011, 1, 1, 10, 0),  # Duplicate
            datetime(2011, 1, 2, 11, 0),  # Cancellation 'C'
            datetime(2011, 1, 3, 12, 0),  # Valid
            datetime(2011, 1, 4, 13, 0),  # Zero qty
            datetime(2011, 1, 5, 14, 0),  # Neg qty without 'C'
        ],
        "UnitPrice": [2.55, 2.55, 2.55, 3.39, 0.0, 4.00],
        "CustomerID": [17850.0, 17850.0, 17850.0, None, 13047.0, 13047.0],
        "Country": ["United Kingdom", "United Kingdom", "United Kingdom", "France", "United Kingdom", "United Kingdom"],
    })

def test_validate_raw_schema():
    valid_df = pd.DataFrame(columns=[
        "InvoiceNo", "StockCode", "Description", "Quantity",
        "InvoiceDate", "UnitPrice", "CustomerID", "Country"
    ])
    is_valid, missing = validate_raw_schema(valid_df)
    assert is_valid is True
    assert len(missing) == 0

    invalid_df = pd.DataFrame(columns=["InvoiceNo", "Quantity"])
    is_valid, missing = validate_raw_schema(invalid_df)
    assert is_valid is False
    assert "StockCode" in missing

def test_cleaning_deduplication_and_cancellations(sample_raw_data):
    from src.config import COLUMN_MAPPING
    canonical_df = sample_raw_data.rename(columns=COLUMN_MAPPING)
    sales, cancels, audit = clean_dataset(canonical_df)

    # Duplicate was row 1
    assert audit["exact_duplicates_removed"] == 1

    # Cancellations: C536366 and row 5 with qty -5
    assert len(cancels) == 2
    assert (cancels["quantity"] < 0).all()

    # Valid sales: row 0 (qty 6, price 2.55) and row 3 (qty 10, price 3.39)
    assert len(sales) == 2
    assert (sales["quantity"] > 0).all()
    assert (sales["unit_price"] > 0).all()

    # Verify line total calculation
    expected_sales_rev = (6 * 2.55) + (10 * 3.39)
    assert pytest.approx(sales["line_total"].sum(), 0.01) == expected_sales_rev

def test_customer_id_formatting(sample_raw_data):
    from src.config import COLUMN_MAPPING
    canonical_df = sample_raw_data.rename(columns=COLUMN_MAPPING)
    sales, _, _ = clean_dataset(canonical_df)

    # 17850.0 should be cast to string "17850"
    assert "17850" in sales["customer_id"].values
    # Null Customer ID preserved as None
    assert sales["customer_id"].isnull().sum() == 1
