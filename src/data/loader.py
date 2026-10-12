"""
Excel ingestion and data loading service for Flux.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import streamlit as st

from src.config import (
    WORKBOOK_PATH,
    WORKSHEET_NAME,
    CLEANED_DATA_PARQUET,
    CLEANED_DATA_CSV,
    COLUMN_MAPPING,
)
from src.data.validation import validate_raw_schema, ValidationError

def load_raw_data(
    workbook_path: Optional[Path] = None,
    sheet_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    Loads raw Excel workbook rows without modifications, validates schema,
    and applies canonical column names.
    """
    path = workbook_path or WORKBOOK_PATH
    sheet = sheet_name or WORKSHEET_NAME

    if not Path(path).exists():
        raise FileNotFoundError(
            f"Excel workbook not found at '{path}'. "
            "Please verify that Online Retail.xlsx is in the project root."
        )

    # Ingest using openpyxl engine
    df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")

    is_valid, missing_cols = validate_raw_schema(df)
    if not is_valid:
        raise ValidationError(
            f"Source workbook '{path}' is missing required columns: {missing_cols}. "
            f"Available columns: {list(df.columns)}"
        )

    # Standardize to canonical column names
    df = df.rename(columns=COLUMN_MAPPING)
    return df

@st.cache_data(show_spinner=False)
def load_cached_clean_data(force_refresh: bool = False) -> pd.DataFrame:
    """
    Streamlit-cached loader. Returns the processed clean transaction dataset.
    Loads from Parquet/CSV if exists; otherwise triggers cleaning pipeline.
    """
    if not force_refresh:
        if CLEANED_DATA_PARQUET.exists():
            return pd.read_parquet(CLEANED_DATA_PARQUET)
        elif CLEANED_DATA_CSV.exists():
            df = pd.read_csv(CLEANED_DATA_CSV, parse_dates=["invoice_date"])
            return df

    # If processed file does not exist or refresh is forced:
    from src.data.cleaning import run_cleaning_pipeline
    clean_df, _, _ = run_cleaning_pipeline()
    return clean_df
