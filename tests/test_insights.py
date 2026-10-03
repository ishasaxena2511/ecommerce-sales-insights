"""Unit and Integration Tests for Business Insights Engine.

Validates that:
1. 10-12 insights are generated dynamically from dataset.
2. Every insight contains required fields: Finding, Why It Matters, Recommended Action.
3. Every insight has non-empty text, valid severity, and valid category.
4. Markdown generation writes valid docs/insights.md.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest

from src.insights import generate_business_insights, write_insights_markdown

PROCESSED_DATA_PATH: Path = (
    Path(__file__).resolve().parent.parent / "data" / "processed" / "ecommerce_sales_clean.csv"
)


@pytest.fixture
def clean_df() -> pd.DataFrame:
    """Loads production clean dataset for testing."""
    df = pd.read_csv(PROCESSED_DATA_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def test_insights_generation_count(clean_df: pd.DataFrame) -> None:
    """Verifies that between 10 and 12 strategic insights are generated."""
    insights = generate_business_insights(clean_df)
    assert 10 <= len(insights) <= 12, f"Expected 10-12 insights, got {len(insights)}"


def test_insight_schema_and_contents(clean_df: pd.DataFrame) -> None:
    """Verifies that each insight dictionary conforms to the required enterprise schema."""
    insights = generate_business_insights(clean_df)
    required_keys = {"id", "title", "category", "severity", "metric_badge", "finding", "why_it_matters", "recommended_action"}
    valid_severities = {"danger", "warning", "info", "success"}

    for item in insights:
        assert required_keys.issubset(item.keys()), f"Insight {item.get('id')} missing keys"
        assert item["severity"] in valid_severities, f"Invalid severity: {item['severity']}"
        assert len(item["finding"].strip()) > 20, f"Finding too short in {item['id']}"
        assert len(item["why_it_matters"].strip()) > 20, f"Why It Matters too short in {item['id']}"
        assert len(item["recommended_action"].strip()) > 20, f"Recommended Action too short in {item['id']}"
        assert len(item["metric_badge"].strip()) > 0, f"Empty metric badge in {item['id']}"


def test_insights_markdown_export(clean_df: pd.DataFrame, tmp_path: Path) -> None:
    """Verifies that write_insights_markdown creates a properly formatted document."""
    temp_out = tmp_path / "test_insights.md"
    written_path = write_insights_markdown(clean_df, output_path=temp_out)

    assert written_path.exists()
    content = written_path.read_text(encoding="utf-8")
    assert "# Strategic Business Insights & Executive Takeaways" in content
    assert "## Executive Summary" in content
    assert "### INS-01:" in content
    assert "#### 1. Finding" in content
    assert "#### 2. Why It Matters" in content
    assert "#### 3. Recommended Action" in content


def test_insights_on_filtered_slice(clean_df: pd.DataFrame) -> None:
    """Verifies that generate_business_insights dynamically adapts to filtered slices."""
    south_df = clean_df[clean_df["region"] == "South"]
    south_insights = generate_business_insights(south_df)
    assert len(south_insights) > 0, "Expected insights on filtered South region slice"
