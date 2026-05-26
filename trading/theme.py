"""TradePulse — dark enterprise Streamlit theme."""

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

ACCENT = ("#059669", "#2563eb")
PRIMARY = "#34d399"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif !important; }
.block-container { padding-top: 1.25rem; max-width: 1400px; }
.ep-hero {
  background: linear-gradient(135deg, ACCENT_A, ACCENT_B);
  padding: 1.75rem 2rem; border-radius: 16px; margin-bottom: 1.25rem; color: #fff;
  box-shadow: 0 16px 48px rgba(5, 150, 105, 0.25); border: 1px solid rgba(255,255,255,0.08);
}
.ep-hero h1 { margin: 0; font-size: 1.85rem; font-weight: 700; }
.ep-hero p { margin: 0.4rem 0 0; opacity: 0.92; }
div[data-testid="stMetric"] {
  background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 12px;
}
div[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #064e3b 100%) !important; }
.stTabs [aria-selected="true"] { background: linear-gradient(135deg, ACCENT_A, ACCENT_B) !important; color: #fff !important; border-radius: 10px; }
</style>
""".replace("ACCENT_A", ACCENT[0]).replace("ACCENT_B", ACCENT[1])


def inject_theme() -> None:
    pio.templates.default = "plotly_dark"
    st.markdown(_CSS, unsafe_allow_html=True)


def hero_html(title: str, subtitle: str, icon: str = "") -> str:
    return f'<div class="ep-hero"><h1>{icon} {title}</h1><p>{subtitle}</p></div>'


def style_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(15,23,42,0.5)", font=dict(color="#e2e8f0"))
    return fig
