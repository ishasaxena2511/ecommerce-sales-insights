"""Executive Business Insights & Strategic Action Plans — E-Commerce Sales BI Platform.

Automated decision-intelligence page presenting 12 executive insights computed dynamically
from the active dataset slice via src/insights.py. Respects all global sidebar filters.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

# Configure wide page layout
st.set_page_config(
    page_title="Strategic Insights | E-Commerce Sales BI",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Resolve repo root and register in sys.path
PAGES_DIR: Path = Path(__file__).resolve().parent
APP_DIR: Path = PAGES_DIR.parent
REPO_ROOT: Path = APP_DIR.parent
for _p in [str(REPO_ROOT), str(APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Import utilities
try:
    from utils.charts import THEME, is_dark_mode
    from utils.filters import render_sidebar_filters
except (ModuleNotFoundError, ImportError):
    from app.utils.charts import THEME, is_dark_mode
    from app.utils.filters import render_sidebar_filters

from src.insights import generate_business_insights
from src.metrics import completed_orders, format_inr, kpi_summary


def get_insight_card_css() -> str:
    """Generates theme-adaptive styling for insight cards."""
    dark = is_dark_mode()
    if dark:
        return """
<style>
    .insight-card {
        background-color: #1E293B !important;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 22px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
        border: 1px solid #334155 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .insight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
    }
    .insight-card-danger {
        border-left: 5px solid #F87171 !important;
    }
    .insight-card-warning {
        border-left: 5px solid #FBBF24 !important;
    }
    .insight-card-info {
        border-left: 5px solid #60A5FA !important;
    }
    .insight-card-success {
        border-left: 5px solid #2DD4BF !important;
    }

    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-right: 8px;
    }
    .badge-danger {
        background-color: #450A0A !important;
        color: #FECACA !important;
    }
    .badge-warning {
        background-color: #451A03 !important;
        color: #FEF3C7 !important;
    }
    .badge-info {
        background-color: #082F49 !important;
        color: #BAE6FD !important;
    }
    .badge-success {
        background-color: #064E3B !important;
        color: #A7F3D0 !important;
    }
    .badge-metric {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border: 1px solid #475569 !important;
    }

    .insight-title {
        font-size: 1.18rem;
        font-weight: 800;
        color: #F8FAFC !important;
        margin: 10px 0 14px 0;
        letter-spacing: -0.01em;
    }

    .section-box {
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 0.90rem;
        line-height: 1.5;
    }
    .finding-box {
        background-color: #0F172A !important;
        border-left: 3px solid #64748B !important;
        color: #E2E8F0 !important;
    }
    .why-box {
        background-color: #451A03 !important;
        border-left: 3px solid #F59E0B !important;
        color: #FEF3C7 !important;
    }
    .action-box {
        background-color: #064E3B !important;
        border-left: 3px solid #10B981 !important;
        color: #D1FAE5 !important;
    }
</style>
"""
    else:
        return """
<style>
    .insight-card {
        background-color: #FFFFFF !important;
        border-radius: 12px;
        padding: 22px 26px;
        margin-bottom: 22px;
        box-shadow: 0 2px 10px rgba(11, 37, 69, 0.06) !important;
        border: 1px solid #E2E8F0 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .insight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(11, 37, 69, 0.10) !important;
    }
    .insight-card-danger {
        border-left: 5px solid #E63946 !important;
    }
    .insight-card-warning {
        border-left: 5px solid #F4A261 !important;
    }
    .insight-card-info {
        border-left: 5px solid #13315C !important;
    }
    .insight-card-success {
        border-left: 5px solid #1B998B !important;
    }

    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-right: 8px;
    }
    .badge-danger {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    .badge-warning {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .badge-info {
        background-color: #E0F2FE;
        color: #075985;
    }
    .badge-success {
        background-color: #DCFCE7;
        color: #166534;
    }
    .badge-metric {
        background-color: #F1F5F9;
        color: #0F172A;
        border: 1px solid #CBD5E1;
    }

    .insight-title {
        font-size: 1.18rem;
        font-weight: 800;
        color: #0B2545 !important;
        margin: 10px 0 14px 0;
        letter-spacing: -0.01em;
    }

    .section-box {
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 0.90rem;
        line-height: 1.5;
    }
    .finding-box {
        background-color: #F8FAFC !important;
        border-left: 3px solid #64748B !important;
        color: #1E293B !important;
    }
    .why-box {
        background-color: #FFFBEB !important;
        border-left: 3px solid #F59E0B !important;
        color: #78350F !important;
    }
    .action-box {
        background-color: #F0FDF4 !important;
        border-left: 3px solid #10B981 !important;
        color: #065F46 !important;
    }
</style>
"""


@st.cache_data
def load_clean_dataset() -> pd.DataFrame:
    """Loads and caches the cleaned sales dataset."""
    data_path = REPO_ROOT / "data" / "processed" / "ecommerce_sales_clean.csv"
    if not data_path.exists():
        st.error(f"Processed dataset not found at `{data_path}`. Run `python src/clean_data.py` first.")
        st.stop()
    df = pd.read_csv(data_path)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def render_insight_card(item: Dict[str, Any]) -> None:
    """Renders a single structured insight card with finding, why it matters, and action."""
    sev = item.get("severity", "info")
    card_class = f"insight-card insight-card-{sev}"
    badge_class = f"badge-pill badge-{sev}"

    sev_labels = {
        "danger": "🚨 Critical Priority",
        "warning": "⚠️ High Priority",
        "info": "ℹ️ Medium Priority",
        "success": "✅ Strategic Growth",
    }
    sev_label = sev_labels.get(sev, "Strategic Note")

    finding_html = item["finding"].replace("**", "<strong>").replace("**", "</strong>")
    why_html = item["why_it_matters"]
    action_html = item["recommended_action"]

    html = f"""<div class="{card_class}">
<div style="display: flex; align-items: center; flex-wrap: wrap; gap: 6px; margin-bottom: 4px;">
<span class="badge-pill badge-metric"><strong>{item['id']}</strong></span>
<span class="badge-pill badge-metric">{item['category']}</span>
<span class="{badge_class}">{sev_label}</span>
<span class="badge-pill badge-metric">📌 {item['metric_badge']}</span>
</div>
<div class="insight-title">{item['title']}</div>
<div class="section-box finding-box">
<strong>🔍 Data Finding:</strong><br>
{finding_html}
</div>
<div class="section-box why-box">
<strong>⚖️ Why It Matters:</strong><br>
{why_html}
</div>
<div class="section-box action-box">
<strong>🎯 Recommended Action:</strong><br>
{action_html}
</div>
</div>"""
    st.markdown(html, unsafe_allow_html=True)


def main() -> None:
    raw_df = load_clean_dataset()

    # Sidebar global filters
    filtered_df = render_sidebar_filters(raw_df)
    st.markdown(get_insight_card_css(), unsafe_allow_html=True)

    # Executive Banner
    st.markdown(
        """<div class="page-header">
<h1 class="page-header-title" style="color: #FFFFFF !important; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 6px 0;"><span style="color: #FFFFFF !important;">Executive Strategic Insights &amp; Recommendations</span></h1>
<p class="page-header-subtitle" style="color: #CBD5E1 !important; margin: 0; font-size: 0.88rem;">Automated business intelligence engine calculating 12 commercial findings across margins, VIP customer concentration, discount break-evens, and fulfillment SLAs.</p>
</div>""",
        unsafe_allow_html=True,
    )

    # Compute insights dynamically from the current filtered slice
    insights = generate_business_insights(filtered_df)
    kpis = kpi_summary(filtered_df)

    # Top summary metrics strip
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Analyzed Orders", f"{kpis['total_all_orders']:,}", f"{kpis['total_orders']:,} Completed")
    with k2:
        st.metric("Analyzed Revenue", format_inr(kpis["total_sales"]))
    with k3:
        st.metric("Blended Margin", f"{kpis['margin_pct']:.1f}%")
    with k4:
        critical_count = sum(1 for item in insights if item.get("severity") == "danger")
        st.metric("Critical Action Items", f"{critical_count} Flagged", delta_color="inverse")

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    if not insights:
        st.info("No insights could be generated for the current selection. Please adjust your filters.")
        st.stop()

    # Category and Severity interactive filters for the page
    col_f1, col_f2 = st.columns([1.5, 1.0])
    all_domains = ["All Domains"] + sorted(list({item["category"] for item in insights}))
    all_severities = ["All Priorities", "Critical Priority", "High Priority", "Strategic Growth", "Medium Priority"]

    with col_f1:
        selected_domain = st.selectbox("Filter Insights by Domain:", options=all_domains, index=0)
    with col_f2:
        selected_sev = st.selectbox("Filter Insights by Severity:", options=all_severities, index=0)

    sev_mapping = {
        "Critical Priority": "danger",
        "High Priority": "warning",
        "Strategic Growth": "success",
        "Medium Priority": "info",
    }

    # Filter insights list
    display_insights = insights
    if selected_domain != "All Domains":
        display_insights = [item for item in display_insights if item["category"] == selected_domain]
    if selected_sev != "All Priorities":
        target_sev = sev_mapping.get(selected_sev)
        display_insights = [item for item in display_insights if item["severity"] == target_sev]

    st.markdown(f"**Showing {len(display_insights)} of {len(insights)} Strategic Insights**")

    # Render each insight card
    for item in display_insights:
        render_insight_card(item)

    # Export Insights
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📥 Export Intelligence Briefing")

    # Generate Markdown text for download
    md_text = f"# Executive Insights Briefing\n\nScope: {kpis['total_all_orders']:,} Orders | {format_inr(kpis['total_sales'])} Sales | {kpis['margin_pct']:.1f}% Margin\n\n"
    for item in insights:
        clean_finding = item["finding"].replace("<strong>", "").replace("</strong>", "")
        md_text += f"## {item['id']}: {item['title']}\n"
        md_text += f"- **Domain**: {item['category']}\n"
        md_text += f"- **Priority**: {item['severity'].upper()}\n"
        md_text += f"- **Metric**: {item['metric_badge']}\n\n"
        md_text += f"### Finding\n{clean_finding}\n\n"
        md_text += f"### Why It Matters\n{item['why_it_matters']}\n\n"
        md_text += f"### Recommended Action\n{item['recommended_action']}\n\n---\n\n"

    st.download_button(
        label="📄 Download Executive Insights Report (Markdown)",
        data=md_text.encode("utf-8"),
        file_name="executive_insights_report.md",
        mime="text/markdown",
        type="secondary",
    )


if __name__ == "__main__":
    main()
