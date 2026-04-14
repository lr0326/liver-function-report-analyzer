"""
Report API routes.

Provides endpoints for uploading liver function reports and retrieving
analysis results.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from flask import Blueprint, current_app, jsonify, request

from ..services.ai_analyzer import AIAnalyzer
from ..services.medical_kb import MedicalKnowledgeBase
from ..services.ocr_service import OCRService
from ..services.report_processor import ReportProcessor

logger = logging.getLogger(__name__)

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

# In-memory store for demo purposes (replace with a database in production)
_report_store: dict[str, dict[str, Any]] = {}


def _get_processor() -> ReportProcessor:
    """Build a ReportProcessor from the current Flask app config."""
    cfg = current_app.config
    ocr = OCRService(
        language=cfg.get("OCR_LANGUAGE", "ch"),
        use_gpu=cfg.get("OCR_USE_GPU", False),
    )
    kb = MedicalKnowledgeBase()
    ai = AIAnalyzer(
        openai_api_key=cfg.get("OPENAI_API_KEY", ""),
        openai_model=cfg.get("OPENAI_MODEL", "gpt-4"),
        openai_max_tokens=cfg.get("OPENAI_MAX_TOKENS", 2000),
        use_local_llm=cfg.get("USE_LOCAL_LLM", False),
        local_llm_url=cfg.get("LOCAL_LLM_URL", "http://localhost:11434"),
        local_llm_model=cfg.get("LOCAL_LLM_MODEL", "llama3"),
    )
    return ReportProcessor(ocr_service=ocr, knowledge_base=kb, ai_analyzer=ai)


def _allowed_file(filename: str) -> bool:
    """Return True if the filename extension is supported."""
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "jpg", "jpeg", "png"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@reports_bp.route("/upload", methods=["POST"])
def upload_report():
    """
    Upload and analyze a liver function report.

    **Request**: multipart/form-data
      - ``file``: the report file (PDF / JPG / PNG)
      - ``gender`` (optional): 'male', 'female', or 'all' (default: 'all')
      - ``age_group`` (optional): 'adult', 'child', or 'elderly' (default: 'adult')

    **Response**: JSON with the full analysis report.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    filename = file.filename or "upload"
    if not _allowed_file(filename):
        return jsonify({
            "error": f"File type not supported. Allowed types: pdf, jpg, jpeg, png."
        }), 400

    gender = request.form.get("gender", "all")
    age_group = request.form.get("age_group", "adult")

    file_content = file.read()
    if len(file_content) == 0:
        return jsonify({"error": "Uploaded file is empty."}), 400

    max_size = current_app.config.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
    if len(file_content) > max_size:
        return jsonify({"error": "File size exceeds the maximum allowed limit."}), 413

    try:
        processor = _get_processor()
        report = processor.process(
            file_content=file_content,
            filename=filename,
            patient_gender=gender,
            patient_age_group=age_group,
        )
        # Cache for retrieval endpoint
        _report_store[report["report_id"]] = report
        return jsonify(report), 200
    except Exception as exc:
        logger.exception("Failed to process uploaded report: %s", exc)
        return jsonify({"error": "Report processing failed. Please try again."}), 500


@reports_bp.route("/analysis/<report_id>", methods=["GET"])
def get_analysis(report_id: str):
    """
    Retrieve a previously computed analysis by report ID.

    **Response**: JSON analysis report or 404 if not found.
    """
    report = _report_store.get(report_id)
    if report is None:
        return jsonify({"error": f"Report '{report_id}' not found."}), 404
    return jsonify(report), 200


@reports_bp.route("/text", methods=["POST"])
def analyze_text():
    """
    Analyze liver function indicator text directly (without file upload).

    **Request**: JSON body
      - ``text``: raw text containing indicator data
      - ``gender`` (optional): patient gender
      - ``age_group`` (optional): patient age group

    **Response**: JSON analysis report.
    """
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Request body must be JSON with a 'text' field."}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "'text' field must not be empty."}), 400

    gender = data.get("gender", "all")
    age_group = data.get("age_group", "adult")

    try:
        processor = _get_processor()
        report = processor.process_text(text, patient_gender=gender, patient_age_group=age_group)
        _report_store[report["report_id"]] = report
        return jsonify(report), 200
    except Exception as exc:
        logger.exception("Text analysis failed: %s", exc)
        return jsonify({"error": "Analysis failed. Please try again."}), 500
