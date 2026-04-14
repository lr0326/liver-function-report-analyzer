"""
Unit tests for ReportProcessor.
"""

import pytest
from app.services.report_processor import ReportProcessor, _compute_risk_score, _risk_label
from app.services.medical_kb import AbnormalSeverity


class TestComputeRiskScore:
    def test_no_abnormal_returns_zero(self):
        assert _compute_risk_score({}) == 0

    def test_mild_abnormal(self):
        abnormal = {
            "ALT": {"severity": AbnormalSeverity.MILD},
        }
        score = _compute_risk_score(abnormal)
        assert score == 10

    def test_severe_abnormal(self):
        abnormal = {
            "ALT": {"severity": AbnormalSeverity.SEVERE},
        }
        score = _compute_risk_score(abnormal)
        assert score == 50

    def test_capped_at_100(self):
        abnormal = {f"IND{i}": {"severity": AbnormalSeverity.SEVERE} for i in range(10)}
        score = _compute_risk_score(abnormal)
        assert score == 100

    def test_multiple_moderate(self):
        abnormal = {
            "ALT": {"severity": AbnormalSeverity.MODERATE},
            "AST": {"severity": AbnormalSeverity.MODERATE},
        }
        score = _compute_risk_score(abnormal)
        assert score == 50


class TestRiskLabel:
    def test_zero_is_normal(self):
        assert _risk_label(0) == "正常"

    def test_low_risk(self):
        label = _risk_label(15)
        assert label == "低风险"

    def test_medium_risk(self):
        label = _risk_label(35)
        assert label == "中等风险"

    def test_high_risk(self):
        label = _risk_label(70)
        assert label == "高风险"


class TestReportProcessorProcessText:
    """Tests using process_text() to avoid requiring OCR dependencies."""

    @pytest.fixture()
    def processor(self):
        return ReportProcessor()

    def test_process_normal_text(self, processor):
        text = "ALT 30 U/L 7-56\nAST 25 U/L 10-40"
        report = processor.process_text(text)
        assert "report_id" in report
        assert report["risk_score"] == 0
        assert report["abnormal_count"] == 0

    def test_process_abnormal_text(self, processor):
        text = "ALT 200 U/L 7-56"
        report = processor.process_text(text)
        assert report["abnormal_count"] > 0
        assert report["risk_score"] > 0

    def test_report_has_required_keys(self, processor):
        report = processor.process_text("ALT 30 U/L 7-56")
        required = {
            "report_id",
            "extracted_indicators",
            "abnormal_indicators",
            "abnormal_count",
            "risk_score",
            "risk_label",
            "analysis",
            "health_recommendations",
            "follow_up_plan",
            "urgency_level",
            "summary",
            "disclaimer",
        }
        assert required.issubset(report.keys())

    def test_process_unsupported_file_type_returns_error(self, processor):
        report = processor.process(b"data", "report.docx")
        assert "error" in report

    def test_severity_values_are_strings(self, processor):
        """AbnormalSeverity enums should be serialized to strings in the report."""
        text = "ALT 200 U/L 7-56"
        report = processor.process_text(text)
        for code, data in report["extracted_indicators"].items():
            assert isinstance(data.get("severity"), str)
