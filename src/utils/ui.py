"""
UI and styling utilities for the Flux Warm Editorial Minimalism design system.
"""

from pathlib import Path
import streamlit as st
from src.config import ASSETS_DIR, THEME_COLORS, PLOTLY_PALETTE
import plotly.graph_objects as go
import plotly.express as px

def apply_editorial_theme():
    """Injects custom CSS tokens and font configurations into the Streamlit session."""
    css_path = ASSETS_DIR / "custom.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def render_header(title: str, subtitle: str, tag: str = "FLUX RETAIL INTELLIGENCE"):
    """Renders a standardized Warm Editorial header with tag, display title, and editorial subtitle."""
    st.markdown(
        f"""
        <div style="margin-bottom: 2rem;">
            <div class="ui-label">{tag}</div>
            <h1 style="font-size: 2.5rem; margin-top: 0.25rem; margin-bottom: 0.5rem;">{title}</h1>
            <div class="editorial-hero-tagline">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_card(title: str, content_html: str, badge: str = None):
    """Renders a structured white paper card with stone border and optional category badge."""
    badge_html = f'<span class="flux-badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="flux-card">
            <div class="flux-card-header">
                <span class="ui-label">{title}</span>
                {badge_html}
            </div>
            <div>{content_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def configure_plotly_figure(fig):
    """Applies Warm Editorial Minimalism layout to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Inter, sans-serif",
            size=12,
            color=THEME_COLORS["text_primary"],
        ),
        title_font=dict(
            family="Inter, sans-serif",
            size=15,
            color=THEME_COLORS["text_primary"],
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor=THEME_COLORS["border_default"],
            gridwidth=0.5,
            zeroline=False,
            linecolor=THEME_COLORS["border_default"],
            tickfont=dict(size=11, color=THEME_COLORS["text_secondary"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=THEME_COLORS["border_default"],
            gridwidth=0.5,
            zeroline=False,
            linecolor=THEME_COLORS["border_default"],
            tickfont=dict(size=11, color=THEME_COLORS["text_secondary"]),
        ),
        hoverlabel=dict(
            bgcolor="#1C1917",
            font_size=12,
            font_family="Inter, sans-serif",
            font_color="#FFFFFF",
        ),
    )
    return fig
