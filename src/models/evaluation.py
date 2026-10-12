"""
Model evaluation visualization and reporting utilities for Flux.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.utils.ui import configure_plotly_figure

def plot_confusion_matrix(cm: List[List[int]], title: str = "Confusion Matrix") -> go.Figure:
    """
    Renders an editorial styled confusion matrix heatmap.
    """
    labels = ["No Re-order", "Will Re-order"]
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)

    fig = px.imshow(
        cm_df,
        text_auto=True,
        color_continuous_scale=[[0, "#FFFFFF"], [0.5, "#BFDBFE"], [1, "#1C1917"]],
        labels=dict(x="Predicted Class", y="Actual Realized Outcome", color="Observations"),
        title=title,
    )
    fig.update_layout(height=340, margin=dict(l=40, r=40, t=50, b=40))
    configure_plotly_figure(fig)
    return fig

def plot_feature_importances(importances: List[Dict[str, Any]], top_n: int = 8) -> go.Figure:
    """
    Renders a clean horizontal bar chart of feature importances.
    """
    df = pd.DataFrame(importances).head(top_n).sort_values(by="importance", ascending=True)

    fig = px.bar(
        df,
        x="importance",
        y="feature",
        orientation="h",
        color_discrete_sequence=["#1C1917"],
        title="Predictive Signal Ranking (Feature Importance)",
        labels={"importance": "Gini Importance", "feature": "Customer Feature"},
    )
    fig.update_layout(height=340, margin=dict(l=40, r=40, t=50, b=40))
    configure_plotly_figure(fig)
    return fig
