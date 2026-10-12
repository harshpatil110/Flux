"""
Flux configuration module.
Provides environment-aware, relative paths and consistent analytical constants.
"""

from pathlib import Path
import os

# Project root resolution (always relative to project directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data Paths
DEFAULT_WORKBOOK_NAME = "Online Retail.xlsx"
WORKBOOK_PATH = Path(os.getenv("FLUX_WORKBOOK_PATH", PROJECT_ROOT / DEFAULT_WORKBOOK_NAME))
WORKSHEET_NAME = os.getenv("FLUX_WORKSHEET_NAME", "Online Retail")

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
MODELS_DIR = PROJECT_ROOT / "models"
DOCS_DIR = PROJECT_ROOT / "docs"
ASSETS_DIR = PROJECT_ROOT / "assets"

CLEANED_DATA_PARQUET = PROCESSED_DATA_DIR / "online_retail_clean.parquet"
CLEANED_DATA_CSV = PROCESSED_DATA_DIR / "online_retail_clean.csv"
CLEANING_AUDIT_JSON = PROCESSED_DATA_DIR / "cleaning_audit.json"

# Model Artifact Paths
RFM_MODEL_PATH = MODELS_DIR / "kmeans_rfm.joblib"
REPEAT_PURCHASE_MODEL_PATH = MODELS_DIR / "repeat_purchase_model.joblib"

# Canonical Column Schema Mapping
COLUMN_MAPPING = {
    "InvoiceNo": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "UnitPrice": "unit_price",
    "CustomerID": "customer_id",
    "Country": "country",
}

# Inverted mapping if needed
REVERSE_COLUMN_MAPPING = {v: k for k, v in COLUMN_MAPPING.items()}

# Analytical Settings & Seeds
RANDOM_SEED = 42

# RFM Configuration
RFM_DEFAULT_CLUSTERS = 4
RFM_MIN_CLUSTERS = 2
RFM_MAX_CLUSTERS = 8

# Basket Analysis Configuration
DEFAULT_MIN_SUPPORT = 0.015
DEFAULT_MIN_CONFIDENCE = 0.20
DEFAULT_MIN_LIFT = 1.2

# Repeat Purchase Prediction Configuration
REPEAT_LOOKBACK_DAYS = 90
REPEAT_LABEL_DAYS = 30

# Theme Tokens (Warm Editorial Minimalism)
THEME_COLORS = {
    "canvas": "#F7F5F0",
    "canvas_alt": "#F2F0EA",
    "card": "#FFFFFF",
    "elevated": "#FAFAF9",
    "text_primary": "#1C1917",
    "text_secondary": "#78716C",
    "text_muted": "#A8A29E",
    "border_default": "#E7E5E4",
    "border_subtle": "#F5F5F4",
    "accent_primary": "#BFDBFE",
    "action_accent": "#93C5FD",
    "text_on_accent": "#1E40AF",
    "focus_accent": "#60A5FA",
    "success": "#059669",
    "warning": "#D97706",
    "danger": "#DC2626",
}

# Plotly Color Palette matching Warm Editorial Minimalism
PLOTLY_PALETTE = [
    "#1C1917",  # Stone 900
    "#3B82F6",  # Blue 500
    "#78716C",  # Stone 500
    "#93C5FD",  # Blue 300
    "#059669",  # Emerald 600
    "#D97706",  # Amber 600
    "#475569",  # Slate 600
    "#2563EB",  # Blue 600
]
