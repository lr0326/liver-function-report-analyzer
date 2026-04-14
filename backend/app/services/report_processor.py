"""
Report Processor — end-to-end pipeline orchestrator.

Ties together OCRService, MedicalKnowledgeBase and AIAnalyzer to produce a
fully structured analysis report from a raw uploaded file.

Typical flow:
  1. OCRService extracts raw text and initial indicator candidates from the file.
  2. MedicalKnowledgeBase assesses each indicator and grades severity.
  3. AIAnalyzer generates a narrative medical interpretation.
  4. ReportProcessor computes a risk score and assembles the final report.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from .ai_analyzer import AIAnalyzer
from .medical_kb import AbnormalSeverity, MedicalKnowledgeBase
from .ocr_service import OCRService

logger = logging.getLogger(__name__)

# Risk score weights per severity level (0-100 scale)
_SEVERITY_WEIGHT: dict[str, int] = {
    AbnormalSeverity.NORMAL: 0,
    AbnormalSeverity.MILD: 10,
    AbnormalSeverity.MODERATE: 25,
    AbnormalSeverity.SEVERE: 50,
}


def _compute_risk_score(abnormal_indicators: dict[str, dict[str, Any]]) -> int:
    """
    Compute an overall risk score (0-100) from the set of abnormal indicators.

    Each abnormal indicator contributes a severity-weighted score; the total is
    capped at 100.
    """
    if not abnormal_indicators:
        return 0

    total = 0
    for data in abnormal_indicators.values():
        sev = data.get("severity", AbnormalSeverity.NORMAL)
        # Support both enum instances and plain strings (e.g. after JSON round-trip)
        if isinstance(sev, str) and not isinstance(sev, AbnormalSeverity):
            try:
                sev = AbnormalSeverity(sev)
            except ValueError:
                sev = AbnormalSeverity.NORMAL
        total += _SEVERITY_WEIGHT.get(sev, 0)
    return min(total, 100)


def _risk_label(score: int) -> str:
    """Convert a numeric risk score to a Chinese label."""
    if score == 0:
        return "正常"
    elif score <= 20:
        return "低风险"
    elif score <= 50:
        return "中等风险"
    else:
        return "高风险"


class ReportProcessor:
    """
    Orchestrates the full report processing pipeline.

    Args:
        ocr_service: OCRService instance (or None to use a default one).
        knowledge_base: MedicalKnowledgeBase instance (or None).
        ai_analyzer: AIAnalyzer instance (or None).
    """

    def __init__(
        self,
        ocr_service: OCRService | None = None,
        knowledge_base: MedicalKnowledgeBase | None = None,
        ai_analyzer: AIAnalyzer | None = None,
    ):
        self.ocr = ocr_service or OCRService()
        self.kb = knowledge_base or MedicalKnowledgeBase()
        self.analyzer = ai_analyzer or AIAnalyzer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(
        self,
        file_content: bytes,
        filename: str,
        patient_gender: str = "all",
        patient_age_group: str = "adult",
    ) -> dict[str, Any]:
        """
        Process an uploaded liver function report file end-to-end.

        Args:
            file_content: Raw bytes of the uploaded file.
            filename: Original filename (determines OCR path: PDF vs image).
            patient_gender: 'male', 'female', or 'all'.
            patient_age_group: 'adult', 'child', or 'elderly'.

        Returns:
            A structured report dict (see :py:meth:`_assemble_report`).
        """
        report_id = str(uuid.uuid4())
        logger.info("Processing report %s (%s)", report_id, filename)

        # Step 1: OCR
        try:
            ocr_result = self.ocr.process_file(file_content, filename)
        except Exception as exc:
            logger.exception("OCR failed for report %s: %s", report_id, exc)
            return self._error_report(report_id, "OCR processing failed. Please check the file and try again.")

        raw_indicators = ocr_result.get("indicators", {})
        raw_text = ocr_result.get("raw_text", "")

        if not raw_indicators:
            logger.warning("No indicators extracted from report %s", report_id)

        # Step 2: Knowledge base assessment
        try:
            assessed = self.kb.assess_report(raw_indicators, patient_gender, patient_age_group)
            abnormal = self.kb.get_abnormal_indicators(raw_indicators, patient_gender, patient_age_group)
        except Exception as exc:
            logger.exception("KB assessment failed for report %s: %s", report_id, exc)
            assessed = {}
            abnormal = {}

        # Step 3: AI analysis
        try:
            analysis = self.analyzer.analyze(
                indicators=assessed,
                abnormal_indicators=abnormal,
                gender=patient_gender,
                age_group=patient_age_group,
                raw_text=raw_text,
            )
        except Exception as exc:
            logger.exception("AI analysis failed for report %s: %s", report_id, exc)
            analysis = {
                "summary": "AI 分析暂时不可用，请稍后重试。",
                "health_recommendations": [],
                "follow_up_plan": "建议咨询医生。",
                "urgency_level": "soon",
                "disclaimer": "本分析仅供参考。",
            }

        # Step 4: Assemble final report
        risk_score = _compute_risk_score(abnormal)
        return self._assemble_report(
            report_id=report_id,
            filename=filename,
            raw_text=raw_text,
            ocr_page_count=ocr_result.get("page_count", 1),
            file_type=ocr_result.get("file_type", "unknown"),
            assessed_indicators=assessed,
            abnormal_indicators=abnormal,
            analysis=analysis,
            risk_score=risk_score,
            patient_gender=patient_gender,
            patient_age_group=patient_age_group,
        )

    def process_text(
        self,
        text: str,
        patient_gender: str = "all",
        patient_age_group: str = "adult",
    ) -> dict[str, Any]:
        """
        Process plain text directly (useful for testing or pre-extracted text).

        Skips the OCR step and feeds text directly into the knowledge base.
        """
        report_id = str(uuid.uuid4())
        raw_indicators = self.ocr.parse_indicators_from_text(text)
        assessed = self.kb.assess_report(raw_indicators, patient_gender, patient_age_group)
        abnormal = self.kb.get_abnormal_indicators(raw_indicators, patient_gender, patient_age_group)

        analysis = self.analyzer.analyze(
            indicators=assessed,
            abnormal_indicators=abnormal,
            gender=patient_gender,
            age_group=patient_age_group,
            raw_text=text,
        )

        risk_score = _compute_risk_score(abnormal)
        return self._assemble_report(
            report_id=report_id,
            filename="text_input",
            raw_text=text,
            ocr_page_count=0,
            file_type="text",
            assessed_indicators=assessed,
            abnormal_indicators=abnormal,
            analysis=analysis,
            risk_score=risk_score,
            patient_gender=patient_gender,
            patient_age_group=patient_age_group,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _assemble_report(
        report_id: str,
        filename: str,
        raw_text: str,
        ocr_page_count: int,
        file_type: str,
        assessed_indicators: dict[str, dict[str, Any]],
        abnormal_indicators: dict[str, dict[str, Any]],
        analysis: dict[str, Any],
        risk_score: int,
        patient_gender: str,
        patient_age_group: str,
    ) -> dict[str, Any]:
        """Build the final structured report dictionary."""
        # Serialize severity enums to strings for JSON compatibility
        def _clean(d: dict) -> dict:
            out = {}
            for k, v in d.items():
                if hasattr(v, "value"):
                    out[k] = v.value
                elif isinstance(v, dict):
                    out[k] = _clean(v)
                elif isinstance(v, list):
                    out[k] = [item.value if hasattr(item, "value") else item for item in v]
                else:
                    out[k] = v
            return out

        clean_assessed = {code: _clean(data) for code, data in assessed_indicators.items()}
        clean_abnormal = {code: _clean(data) for code, data in abnormal_indicators.items()}

        return {
            "report_id": report_id,
            "filename": filename,
            "file_type": file_type,
            "page_count": ocr_page_count,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "patient_info": {
                "gender": patient_gender,
                "age_group": patient_age_group,
            },
            "extracted_indicators": clean_assessed,
            "abnormal_indicators": clean_abnormal,
            "abnormal_count": len(abnormal_indicators),
            "risk_score": risk_score,
            "risk_label": _risk_label(risk_score),
            "analysis": analysis,
            "health_recommendations": analysis.get("health_recommendations", []),
            "follow_up_plan": analysis.get("follow_up_plan", ""),
            "urgency_level": analysis.get("urgency_level", "none"),
            "summary": analysis.get("summary", ""),
            "disclaimer": analysis.get("disclaimer", "本分析仅供参考。"),
            "raw_text_snippet": raw_text[:300] if raw_text else "",
        }

    @staticmethod
    def _error_report(report_id: str, error_message: str) -> dict[str, Any]:
        """Return a structured error report."""
        return {
            "report_id": report_id,
            "error": error_message,
            "status": "failed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "extracted_indicators": {},
            "abnormal_indicators": {},
            "abnormal_count": 0,
            "risk_score": 0,
            "risk_label": "未知",
            "health_recommendations": [],
            "follow_up_plan": "请重新上传报告或联系技术支持。",
            "urgency_level": "none",
            "summary": "报告处理失败。",
            "disclaimer": "本分析仅供参考。",
        }
