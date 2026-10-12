"""
Repeat-Purchase Prediction pipeline for Flux.
Builds leakage-safe historical customer snapshots and trains time-evaluated classifiers.
"""

from typing import Tuple, Dict, Any, List
from pathlib import Path
from datetime import datetime, timedelta
import joblib
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
)

from src.config import (
    REPEAT_PURCHASE_MODEL_PATH,
    REPEAT_LOOKBACK_DAYS,
    REPEAT_LABEL_DAYS,
    RANDOM_SEED,
    MODELS_DIR,
)

NUMERIC_FEATURES = [
    "recency_days",
    "orders_count",
    "total_spend",
    "avg_order_value",
    "units_count",
    "unique_products",
    "tenure_days",
]
CATEGORICAL_FEATURES = ["market_group"]

def build_customer_snapshots(
    sales_df: pd.DataFrame,
    snapshot_dates: List[pd.Timestamp],
    lookback_days: int = REPEAT_LOOKBACK_DAYS,
    label_days: int = REPEAT_LABEL_DAYS,
) -> pd.DataFrame:
    """
    Constructs historical customer observation records at specific cutoff dates.
    Zero leakage: Features come strictly from [T - lookback, T].
    Target comes strictly from [T, T + label_days].
    """
    valid_cust_df = sales_df.dropna(subset=["customer_id"]).copy()
    valid_cust_df["customer_id"] = valid_cust_df["customer_id"].astype(str)

    snapshot_records = []

    for snap_date in snapshot_dates:
        lookback_start = snap_date - pd.Timedelta(days=int(lookback_days))
        label_end = snap_date + pd.Timedelta(days=int(label_days))

        # 1. Historical Lookback Data (Strictly < snap_date and >= lookback_start)
        history_df = valid_cust_df[
            (valid_cust_df["invoice_date"] >= lookback_start) &
            (valid_cust_df["invoice_date"] < snap_date)
        ]

        if history_df.empty:
            continue

        # Customers active in the lookback window
        active_customers = history_df["customer_id"].unique()

        # 2. Future Window Data (Strictly >= snap_date and <= label_end)
        future_df = valid_cust_df[
            (valid_cust_df["invoice_date"] >= snap_date) &
            (valid_cust_df["invoice_date"] <= label_end)
        ]
        future_repurchasers = set(future_df["customer_id"].unique())

        # Customer first purchase date up to snapshot date
        prior_history = valid_cust_df[valid_cust_df["invoice_date"] < snap_date]
        cust_tenure = prior_history.groupby("customer_id")["invoice_date"].min()

        # Calculate features per customer
        for cust_id, group in history_df.groupby("customer_id"):
            last_date = group["invoice_date"].max()
            recency = int((snap_date - last_date).total_seconds() / 86400)
            orders = group["invoice_no"].nunique()
            spend = float(group["line_total"].sum())
            aov = float(spend / orders) if orders > 0 else 0.0
            units = int(group["quantity"].sum())
            uniq_items = group["stock_code"].nunique()

            first_date = cust_tenure.get(cust_id, last_date)
            tenure = int((snap_date - first_date).total_seconds() / 86400)

            country = group["country"].iloc[0]
            market_group = "United Kingdom" if country == "United Kingdom" else "International"

            # Label: Did customer purchase in [snap_date, snap_date + label_days]?
            target_repurchase = 1 if cust_id in future_repurchasers else 0

            snapshot_records.append({
                "snapshot_date": snap_date,
                "customer_id": cust_id,
                "recency_days": recency,
                "orders_count": orders,
                "total_spend": spend,
                "avg_order_value": aov,
                "units_count": units,
                "unique_products": uniq_items,
                "tenure_days": tenure,
                "market_group": market_group,
                "target_repurchase": target_repurchase,
            })

    return pd.DataFrame(snapshot_records)

def train_and_evaluate_models(
    sales_df: pd.DataFrame,
    save_artifact: bool = True,
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Builds chronological snapshots, splits into train and test without leakage,
    trains Logistic Regression and Random Forest models, and returns evaluation report.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Establish chronological snapshots (at least 90 days after start and 30 days before end)
    # Date range is 2010-12-01 to 2011-12-09
    snapshots = [
        pd.Timestamp("2011-06-01"),  # Train
        pd.Timestamp("2011-07-15"),  # Train
        pd.Timestamp("2011-09-01"),  # Train
        pd.Timestamp("2011-11-01"),  # Held-out Test
    ]

    snap_df = build_customer_snapshots(sales_df, snapshots)
    if snap_df.empty:
        raise ValueError("Could not extract eligible snapshots for repeat purchase prediction.")

    # Chronological Split
    test_cutoff = pd.Timestamp("2011-11-01")
    train_data = snap_df[snap_df["snapshot_date"] < test_cutoff].copy()
    test_data = snap_df[snap_df["snapshot_date"] == test_cutoff].copy()

    X_train = train_data[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_train = train_data["target_repurchase"]

    X_test = test_data[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y_test = test_data["target_repurchase"]

    # Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]), NUMERIC_FEATURES),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="constant", fill_value="Other")),
                ("encoder", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")),
            ]), CATEGORICAL_FEATURES),
        ]
    )

    # 1. Baseline: Majority class predictor
    majority_class = y_train.mode()[0]
    base_preds = np.full(len(y_test), majority_class)

    # 2. Logistic Regression Pipeline
    lr_pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("clf", LogisticRegression(class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000)),
    ])
    lr_pipe.fit(X_train, y_train)
    lr_preds = lr_pipe.predict(X_test)
    lr_probs = lr_pipe.predict_proba(X_test)[:, 1]

    # 3. Random Forest Pipeline
    rf_pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("clf", RandomForestClassifier(n_estimators=150, max_depth=6, class_weight="balanced", random_state=RANDOM_SEED)),
    ])
    rf_pipe.fit(X_train, y_train)
    rf_preds = rf_pipe.predict(X_test)
    rf_probs = rf_pipe.predict_proba(X_test)[:, 1]

    # Metrics evaluation on held-out test snapshot
    metrics = {
        "test_sample_size": len(y_test),
        "test_positive_count": int(y_test.sum()),
        "test_positive_rate": float(y_test.mean()),
        "baseline": {
            "accuracy": float((base_preds == y_test).mean()),
            "precision": float(precision_score(y_test, base_preds, zero_division=0)),
            "recall": float(recall_score(y_test, base_preds, zero_division=0)),
            "f1": float(f1_score(y_test, base_preds, zero_division=0)),
        },
        "logistic_regression": {
            "precision": float(precision_score(y_test, lr_preds, zero_division=0)),
            "recall": float(recall_score(y_test, lr_preds, zero_division=0)),
            "f1": float(f1_score(y_test, lr_preds, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, lr_probs)),
            "pr_auc": float(average_precision_score(y_test, lr_probs)),
            "confusion_matrix": confusion_matrix(y_test, lr_preds).tolist(),
        },
        "random_forest": {
            "precision": float(precision_score(y_test, rf_preds, zero_division=0)),
            "recall": float(recall_score(y_test, rf_preds, zero_division=0)),
            "f1": float(f1_score(y_test, rf_preds, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, rf_probs)),
            "pr_auc": float(average_precision_score(y_test, rf_probs)),
            "confusion_matrix": confusion_matrix(y_test, rf_preds).tolist(),
        },
    }

    # Extract Feature Importances from Random Forest
    rf_model = rf_pipe.named_steps["clf"]
    ohe_cols = rf_pipe.named_steps["preprocessor"].named_transformers_["cat"].named_steps["encoder"].get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    feature_names = NUMERIC_FEATURES + ohe_cols
    importances = pd.DataFrame({
        "feature": feature_names,
        "importance": rf_model.feature_importances_,
    }).sort_values(by="importance", ascending=False).reset_index(drop=True)

    metrics["feature_importances"] = importances.to_dict(orient="records")

    artifact = {
        "pipeline": rf_pipe,
        "lr_pipeline": lr_pipe,
        "metrics": metrics,
        "features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        "test_snapshot_date": str(test_cutoff),
        "lookback_days": REPEAT_LOOKBACK_DAYS,
        "label_days": REPEAT_LABEL_DAYS,
        "random_seed": RANDOM_SEED,
    }

    if save_artifact:
        joblib.dump(artifact, REPEAT_PURCHASE_MODEL_PATH)

    return artifact, snap_df

def get_or_train_repeat_model(
    sales_df: pd.DataFrame,
    force_retrain: bool = False,
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """
    Loads saved model artifact if present, or executes training pipeline.
    """
    if not force_retrain and REPEAT_PURCHASE_MODEL_PATH.exists():
        try:
            artifact = joblib.load(REPEAT_PURCHASE_MODEL_PATH)
            # Build current test snapshot data for interactive lookup
            test_snap = pd.Timestamp(artifact["test_snapshot_date"])
            snap_df = build_customer_snapshots(sales_df, [test_snap])
            return artifact, snap_df
        except Exception:
            pass

    return train_and_evaluate_models(sales_df, save_artifact=True)
