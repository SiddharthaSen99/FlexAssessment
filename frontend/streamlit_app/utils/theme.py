import streamlit as st
from typing import Optional


def inject_theme() -> None:
    css = """
    <style>
      :root {
        --brand-bg: #0e1117;
        --brand-card: #141821;
        --brand-text: #e6e6e6;
        --brand-muted: #9aa4b2;
        --brand-accent: #00C2A8; /* teal accent similar to modern hospitality sites */
        --brand-border: #232a34;
      }

      .flx-hero {
        width: 100%;
        height: 220px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(0,194,168,0.18), rgba(14,17,23,0.6)), url('https://picsum.photos/1200/400?blur=3') center/cover no-repeat;
        border: 1px solid var(--brand-border);
        display: flex; align-items: end; padding: 20px;
      }

      .flx-title {
        font-size: 28px; font-weight: 700; color: var(--brand-text);
      }
      .flx-subtitle { color: var(--brand-muted); font-size: 14px; margin-top: 4px; }

      .flx-summary {
        display: flex; gap: 16px; align-items: center; margin-top: 12px;
      }
      .flx-badge {
        background: rgba(0,194,168,0.15); color: #9ff7eb; border: 1px solid var(--brand-accent);
        border-radius: 999px; padding: 6px 12px; font-weight: 600; font-size: 13px;
      }

      .flx-card {
        border: 1px solid var(--brand-border);
        border-radius: 12px; padding: 16px; background: var(--brand-card);
      }
      .flx-card + .flx-card { margin-top: 12px; }

      .flx-stars { color: #FFD166; letter-spacing: 1px; font-size: 14px; }
      .flx-review-text { color: var(--brand-text); font-size: 15px; line-height: 1.6; }
      .flx-meta { color: var(--brand-muted); font-size: 12px; margin-bottom: 6px; }

      /* KPI cards */
      .flx-kpi-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; margin: 8px 0 12px 0; }
      .flx-kpi { background: linear-gradient(180deg, rgba(20,24,33,1), rgba(20,24,33,0.6)); border: 1px solid var(--brand-border); border-radius: 12px; padding: 14px; }
      .flx-kpi-label { color: var(--brand-muted); font-size: 12px; }
      .flx-kpi-value { color: var(--brand-text); font-weight: 700; font-size: 22px; }
      .flx-kpi-help { color: var(--brand-muted); font-size: 11px; margin-top: 4px; }

      /* Extra badges */
      .flx-badge-secondary { background: rgba(154,164,178,0.15); color: #c7cfdb; border: 1px solid var(--brand-border); border-radius: 999px; padding: 4px 10px; font-size: 12px; }
      .flx-badge-success { background: rgba(0,194,168,0.15); color: #9ff7eb; border: 1px solid var(--brand-accent); border-radius: 999px; padding: 4px 10px; font-size: 12px; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_stars(rating_out_of_10: Optional[float]) -> str:
    if rating_out_of_10 is None:
        return "<span class='flx-stars'>☆☆☆☆☆</span>"
    # Convert 0-10 to 0-5 scale
    five = max(0, min(5, round(float(rating_out_of_10) / 2)))
    return "<span class='flx-stars'>" + ("★" * five + "☆" * (5 - five)) + "</span>"


def render_badge(text: str, variant: str = "secondary") -> str:
    cls = "flx-badge-success" if variant == "success" else "flx-badge-secondary"
    return f"<span class='{cls}'>{text}</span>"


def render_kpi(label: str, value: str, help_text: Optional[str] = None) -> str:
    help_html = f"<div class='flx-kpi-help'>{help_text}</div>" if help_text else ""
    return (
        "<div class='flx-kpi'>"
        f"<div class='flx-kpi-label'>{label}</div>"
        f"<div class='flx-kpi-value'>{value}</div>"
        f"{help_html}"
        "</div>"
    )
