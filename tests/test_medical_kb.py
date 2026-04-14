"""
Unit tests for MedicalKnowledgeBase.
"""

import pytest
from app.services.medical_kb import AbnormalSeverity, MedicalKnowledgeBase


@pytest.fixture()
def kb():
    return MedicalKnowledgeBase()


class TestListIndicators:
    def test_returns_all_expected_codes(self, kb):
        codes = kb.list_indicators()
        expected = {"ALT", "AST", "ALP", "GGT", "TBIL", "DBIL", "IBIL", "ALB", "GLB", "A/G", "TP"}
        assert expected.issubset(set(codes))

    def test_count_at_least_eleven(self, kb):
        assert len(kb.list_indicators()) >= 11


class TestIsSupported:
    def test_supported_uppercase(self, kb):
        assert kb.is_supported("ALT") is True

    def test_supported_lowercase(self, kb):
        assert kb.is_supported("alt") is True

    def test_unsupported(self, kb):
        assert kb.is_supported("XYZ") is False


class TestGetIndicator:
    def test_returns_info(self, kb):
        info = kb.get_indicator("ALT")
        assert info is not None
        assert info.code == "ALT"
        assert info.chinese_name == "谷丙转氨酶"

    def test_missing_returns_none(self, kb):
        assert kb.get_indicator("MISSING") is None


class TestAssessIndicator:
    def test_normal_alt(self, kb):
        result = kb.assess_indicator("ALT", 30)
        assert result["is_abnormal"] is False
        assert result["severity"] == AbnormalSeverity.NORMAL

    def test_elevated_alt_mild(self, kb):
        result = kb.assess_indicator("ALT", 70)  # Just above 56 U/L ULN
        assert result["is_abnormal"] is True
        assert result["direction"] == "high"
        assert result["severity"] in (AbnormalSeverity.MILD,)

    def test_elevated_alt_severe(self, kb):
        result = kb.assess_indicator("ALT", 600)  # 10x+ ULN
        assert result["is_abnormal"] is True
        assert result["severity"] == AbnormalSeverity.SEVERE

    def test_low_alb(self, kb):
        result = kb.assess_indicator("ALB", 20)  # Well below 35 g/L
        assert result["is_abnormal"] is True
        assert result["direction"] == "low"

    def test_unknown_code_returns_no_error(self, kb):
        result = kb.assess_indicator("UNKNOWN", 50)
        assert result["is_abnormal"] is False
        assert "error" in result


class TestAssessReport:
    def test_all_normal(self, kb):
        indicators = {"ALT": 30, "AST": 25, "ALB": 42}
        results = kb.assess_report(indicators)
        for code, result in results.items():
            assert result["is_abnormal"] is False

    def test_mixed_report(self, kb):
        indicators = {"ALT": 200, "AST": 25}
        results = kb.assess_report(indicators)
        assert results["ALT"]["is_abnormal"] is True
        assert results["AST"]["is_abnormal"] is False

    def test_dict_value_input(self, kb):
        indicators = {"ALT": {"value": 200, "unit": "U/L"}}
        results = kb.assess_report(indicators)
        assert results["ALT"]["is_abnormal"] is True


class TestGetAbnormalIndicators:
    def test_filters_normal(self, kb):
        indicators = {"ALT": 30, "AST": 200}
        abnormal = kb.get_abnormal_indicators(indicators)
        assert "ALT" not in abnormal
        assert "AST" in abnormal

    def test_empty_when_all_normal(self, kb):
        indicators = {"ALT": 30, "AST": 25}
        abnormal = kb.get_abnormal_indicators(indicators)
        assert len(abnormal) == 0
