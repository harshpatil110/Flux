"""
Customer Segmentation via K-Means clustering on RFM features for Flux.
"""

from typing import Dict, Any, Tuple, List
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

from src.config import RFM_MODEL_PATH, RANDOM_SEED, MODELS_DIR
from src.analytics.rfm import calculate_rfm

FEATURE_COLS = ["recency", "frequency", "monetary"]

def evaluate_clusters(rfm_df: pd.DataFrame, k_range: range = range(2, 8)) -> pd.DataFrame:
    """
    Evaluates cluster counts across k_range using Inertia (Elbow) and Silhouette Score.
    """
    X_log = np.log1p(rfm_df[FEATURE_COLS].clip(lower=0))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_log)

    eval_records = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_SEED, n_init=10)
        km.fit(X_scaled)
        labels = km.labels_
        sil = silhouette_score(X_scaled, labels)
        eval_records.append({
            "k": k,
            "inertia": float(km.inertia_),
            "silhouette": float(sil),
        })

    return pd.DataFrame(eval_records)

def assign_segment_labels(profiles: pd.DataFrame) -> Dict[int, str]:
    """
    Generates data-driven segment titles by ranking cluster centroid properties.
    High Monetary + Low Recency = Champions
    Moderate Recency + High Frequency = Loyal Regulars
    High Recency + Low Frequency = Hibernating / At Risk
    Low Recency + Low Frequency = New / Occasional
    """
    label_map = {}
    # Rank by composite value score: frequency * monetary / recency
    profiles_copy = profiles.copy()
    profiles_copy["score"] = (
        (profiles_copy["frequency"] * profiles_copy["monetary"]) /
        profiles_copy["recency"].replace(0, 1)
    )
    sorted_clusters = profiles_copy.sort_values(by="score", ascending=False).index.tolist()

    if len(sorted_clusters) == 4:
        label_map[sorted_clusters[0]] = "Champions / High-Value Loyal"
        label_map[sorted_clusters[1]] = "Active Regulars"
        label_map[sorted_clusters[2]] = "Occasional / Promising"
        label_map[sorted_clusters[3]] = "Hibernating / At Risk"
    else:
        for rank, cid in enumerate(sorted_clusters):
            if rank == 0:
                label_map[cid] = "Tier 1: High Value / Loyal"
            elif rank == len(sorted_clusters) - 1:
                label_map[cid] = "Tier Last: Low Engagement / At Risk"
            else:
                label_map[cid] = f"Tier {rank+1}: Moderate Engagement"

    return label_map

def train_segmentation_model(
    rfm_df: pd.DataFrame,
    n_clusters: int = 4,
    save_artifact: bool = True,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Trains K-Means on log-transformed, standard-scaled RFM features.
    Returns the segmented customer dataframe and the fitted artifact bundle.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    X_log = np.log1p(rfm_df[FEATURE_COLS].clip(lower=0))
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_log)

    kmeans = KMeans(n_clusters=n_clusters, random_state=RANDOM_SEED, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    sil_score = float(silhouette_score(X_scaled, clusters))

    segmented_df = rfm_df.copy()
    segmented_df["cluster"] = clusters

    # Calculate cluster profiles
    profiles = segmented_df.groupby("cluster").agg(
        customer_count=("customer_id", "count"),
        total_revenue=("monetary", "sum"),
        recency=("recency", "median"),
        frequency=("frequency", "median"),
        monetary=("monetary", "median"),
        avg_aov=("aov", "mean"),
    )
    profiles["revenue_share"] = (
        profiles["total_revenue"] / segmented_df["monetary"].sum() * 100
    ).round(1)

    label_map = assign_segment_labels(profiles)
    segmented_df["segment_name"] = segmented_df["cluster"].map(label_map)

    artifact = {
        "model": kmeans,
        "scaler": scaler,
        "n_clusters": n_clusters,
        "silhouette_score": sil_score,
        "inertia": float(kmeans.inertia_),
        "label_map": label_map,
        "profiles": profiles.to_dict(orient="index"),
        "features": FEATURE_COLS,
        "random_seed": RANDOM_SEED,
    }

    if save_artifact:
        joblib.dump(artifact, RFM_MODEL_PATH)

    return segmented_df, artifact

def get_or_train_rfm_segments(
    sales_df: pd.DataFrame,
    n_clusters: int = 4,
    force_retrain: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cached or persistent loader for RFM segmentation.
    """
    rfm_df = calculate_rfm(sales_df)

    if not force_retrain and RFM_MODEL_PATH.exists():
        try:
            artifact = joblib.load(RFM_MODEL_PATH)
            if artifact.get("n_clusters") == n_clusters:
                scaler = artifact["scaler"]
                kmeans = artifact["model"]
                label_map = artifact["label_map"]

                X_log = np.log1p(rfm_df[FEATURE_COLS].clip(lower=0))
                X_scaled = scaler.transform(X_log)
                rfm_df["cluster"] = kmeans.predict(X_scaled)
                rfm_df["segment_name"] = rfm_df["cluster"].map(label_map)
                return rfm_df, artifact
        except Exception:
            pass

    return train_segmentation_model(rfm_df, n_clusters=n_clusters, save_artifact=True)
