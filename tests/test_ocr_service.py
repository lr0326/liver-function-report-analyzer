"""
Unit tests for OCRService text parsing (no PaddleOCR required).
"""

import pytest
from app.services.ocr_service import OCRService, _parse_indicators_from_text


class TestParseIndicatorsFromText:
    """Tests for the pure text-parsing logic (no external dependencies)."""

    def test_parse_alt_from_chinese_text(self):
        text = "谷丙转氨酶  45 U/L  7-56"
        indicators = _parse_indicators_from_text(text)
        assert "ALT" in indicators
        assert indicators["ALT"]["value"] == 45.0

    def test_parse_alt_abbreviation(self):
        text = "ALT  120  U/L  7-56"
        indicators = _parse_indicators_from_text(text)
        assert "ALT" in indicators
        assert indicators["ALT"]["value"] == 120.0

    def test_parse_multiple_indicators(self):
        text = (
            "ALT  45 U/L 7-56\n"
            "AST  38 U/L 10-40\n"
            "总胆红素  15.0 μmol/L 3.4-20.5\n"
        )
        indicators = _parse_indicators_from_text(text)
        assert "ALT" in indicators
        assert "AST" in indicators
        assert "TBIL" in indicators

    def test_abnormal_flag_when_above_range(self):
        text = "ALT  200 U/L 7-56"
        indicators = _parse_indicators_from_text(text)
        assert indicators["ALT"]["abnormal"] is True

    def test_normal_flag_within_range(self):
        text = "ALT  30 U/L 7-56"
        indicators = _parse_indicators_from_text(text)
        assert indicators["ALT"]["abnormal"] is False

    def test_no_indicators_in_empty_text(self):
        indicators = _parse_indicators_from_text("")
        assert indicators == {}

    def test_no_indicators_in_irrelevant_text(self):
        indicators = _parse_indicators_from_text("患者姓名：张三  性别：男  年龄：45")
        assert len(indicators) == 0

    def test_reference_range_extracted(self):
        text = "ALT  45 U/L 7-56"
        indicators = _parse_indicators_from_text(text)
        ref = indicators["ALT"]["reference_range"]
        assert "7" in ref
        assert "56" in ref


class TestOCRServiceParseIndicatorsFromTextStatic:
    """Verify the public static method delegates correctly."""

    def test_static_method_parses_alt(self):
        text = "ALT 50 U/L 7-56"
        result = OCRService.parse_indicators_from_text(text)
        assert "ALT" in result

    def test_unsupported_extension_raises(self):
        service = OCRService()
        with pytest.raises(ValueError, match="Unsupported file format"):
            service.process_file(b"data", "report.docx")
