"""
Schema and data validation routines for Flux.
"""

from typing import Tuple, List, Dict, Any
import pandas as pd
from src.config import COLUMN_MAPPING

REQUIRED_RAW_COLUMNS = list(COLUMN_MAPPING.keys())
REQUIRED_CANONICAL_COLUMNS = list(COLUMN_MAPPING.values())

class ValidationError(Exception):
    """Raised when data fails critical schema or integrity validation."""
    pass

def validate_raw_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Checks if the loaded raw dataframe contains all required columns."""
    missing = [col for col in REQUIRED_RAW_COLUMNS if col not in df.columns]
    if missing:
        return False, missing
    return True, []

def validate_canonical_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Checks if the dataframe matches the canonical column schema."""
    missing = [col for col in REQUIRED_CANONICAL_COLUMNS if col not in df.columns]
    if missing:
        return False, missing
    return True, []

def validate_cleaned_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs integrity assertions on the cleaned sales dataset.
    Ensures non-empty dataframe, positive quantities and prices, and valid timestamps.
    """
    issues = []
    
    if df.empty:
        raise ValidationError("Cleaned dataset is empty!")
        
    if (df["quantity"] <= 0).any():
        issues.append(f"Found {(df['quantity'] <= 0).sum()} non-positive quantity rows in valid sales.")
        
    if (df["unit_price"] <= 0).any():
        issues.append(f"Found {(df['unit_price'] <= 0).sum()} non-positive unit_price rows in valid sales.")
        
    if df["invoice_date"].isnull().any():
        issues.append(f"Found {df['invoice_date'].isnull().sum()} null invoice dates.")
        
    if df["invoice_no"].isnull().any():
        issues.append(f"Found {df['invoice_no'].isnull().sum()} null invoice numbers.")
        
    return {
        "is_valid": len(issues) == 0,
        "row_count": len(df),
        "issues": issues,
    }
