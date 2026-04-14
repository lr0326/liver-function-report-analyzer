"""
Unit tests for AIAnalyzer (rule-based fallback path, no LLM required).
"""

import pytest
from app.services.ai_analyzer import AIAnalyzer
from app.services.medical_kb import AbnormalSeverity


@pytest.fixture()
def analyzer():
    """Create an AIAnalyzer with no LLM configured (uses rule-based fallback)."""
    return AIAnalyzer()  # No API key → fallback mode


class TestRuleBasedAnalyze:
    def test_all_normal_report(self, analyzer):
        indicators = {
            "ALT": {"value": 30, "unit": "U/L", "is_abnormal": False, "severity": AbnormalSeverity.NORMAL},
        }
        result = analyzer.analyze(indicators=indicators, abnormal_indicators={})
        assert result["urgency_level"] == "none"
        assert "正常" in result["summary"] or "良好" in result["summary"]

    def test_abnormal_report_includes_recommendations(self, analyzer):
        indicators = {
            "ALT": {
                "value": 200,
                "unit": "U/L",
                "is_abnormal": True,
                "severity": AbnormalSeverity.MODERATE,
                "direction": "high",
                "chinese_name": "谷丙转氨酶",
                "reference_range": "7-56 U/L",
                "description": "升高提示肝细胞损伤",
                "related_conditions": ["肝炎"],
            }
        }
        abnormal = {k: v for k, v in indicators.items() if v["is_abnormal"]}
        result = analyzer.analyze(indicators=indicators, abnormal_indicators=abnormal)
        assert len(result["health_recommendations"]) > 0
        assert result["urgency_level"] in ("soon", "immediate", "routine")

    def test_severe_abnormal_sets_immediate_urgency(self, analyzer):
        abnormal = {
            "ALT": {
                "value": 1000,
                "unit": "U/L",
                "is_abnormal": True,
                "severity": AbnormalSeverity.SEVERE,
                "direction": "high",
                "chinese_name": "谷丙转氨酶",
                "reference_range": "7-56 U/L",
                "description": "",
                "related_conditions": [],
            }
        }
        result = analyzer.analyze(indicators=abnormal, abnormal_indicators=abnormal)
        assert result["urgency_level"] == "immediate"

    def test_result_contains_required_keys(self, analyzer):
        result = analyzer.analyze(indicators={}, abnormal_indicators={})
        required_keys = {
            "summary",
            "abnormal_analysis",
            "risk_assessment",
            "health_recommendations",
            "follow_up_plan",
            "urgency_level",
            "disclaimer",
        }
        assert required_keys.issubset(result.keys())

    def test_disclaimer_present(self, analyzer):
        result = analyzer.analyze(indicators={}, abnormal_indicators={})
        assert len(result["disclaimer"]) > 0
