"""
OCR Service for liver function report analysis.

Supports PDF and image (JPG, PNG) file formats.
Uses PaddleOCR for high-accuracy Chinese/English text recognition.
Extracts structured indicator data (name, value, unit, reference range)
from liver function test reports.
"""

import io
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Mapping of indicator aliases to canonical names
INDICATOR_ALIASES: dict[str, str] = {
    # ALT
    "alt": "ALT",
    "谷丙转氨酶": "ALT",
    "丙氨酸氨基转移酶": "ALT",
    "alanine aminotransferase": "ALT",
    "sgpt": "ALT",
    # AST
    "ast": "AST",
    "谷草转氨酶": "AST",
    "天冬氨酸氨基转移酶": "AST",
    "aspartate aminotransferase": "AST",
    "sgot": "AST",
    # ALP
    "alp": "ALP",
    "碱性磷酸酶": "ALP",
    "alkaline phosphatase": "ALP",
    # GGT
    "ggt": "GGT",
    "γ-谷氨酰转移酶": "GGT",
    "γ谷氨酰转移酶": "GGT",
    "谷氨酰转移酶": "GGT",
    "gamma-glutamyl transferase": "GGT",
    "r-ggt": "GGT",
    # TBIL
    "tbil": "TBIL",
    "总胆红素": "TBIL",
    "total bilirubin": "TBIL",
    # DBIL
    "dbil": "DBIL",
    "直接胆红素": "DBIL",
    "结合胆红素": "DBIL",
    "direct bilirubin": "DBIL",
    # IBIL
    "ibil": "IBIL",
    "间接胆红素": "IBIL",
    "非结合胆红素": "IBIL",
    "indirect bilirubin": "IBIL",
    # ALB
    "alb": "ALB",
    "白蛋白": "ALB",
    "albumin": "ALB",
    # GLB
    "glb": "GLB",
    "球蛋白": "GLB",
    "globulin": "GLB",
    # A/G ratio
    "a/g": "A/G",
    "白球比": "A/G",
    "白球比例": "A/G",
    "白蛋白/球蛋白": "A/G",
    "albumin/globulin": "A/G",
    # TP
    "tp": "TP",
    "总蛋白": "TP",
    "total protein": "TP",
}

# Regex pattern: indicator name | value (with optional decimal) | optional unit | optional reference range
_INDICATOR_LINE_PATTERN = re.compile(
    r"(?P<name>[^\d\s][^\d]*?)\s+"
    r"(?P<value>\d+\.?\d*)\s*"
    r"(?P<unit>[^\d\s\[\(↑↓HLhl]*?)?\s*"
    r"(?:[\[\(]?\s*(?P<ref_low>\d+\.?\d*)\s*[-~–]\s*(?P<ref_high>\d+\.?\d*)\s*[\]\)]?)?",
    re.IGNORECASE,
)

# Simpler pattern for value extraction when the above is too greedy
_VALUE_PATTERN = re.compile(r"\b(\d+\.?\d*)\b")
_UNIT_PATTERN = re.compile(r"\b(U/L|g/L|μmol/L|umol/L|nmol/L|mg/dL|g/dL|IU/L)\b", re.IGNORECASE)
_REF_RANGE_PATTERN = re.compile(
    r"(\d+\.?\d*)\s*[-~–]\s*(\d+\.?\d*)"
)


def _try_import_paddleocr():
    """Attempt to import PaddleOCR; return None if not installed."""
    try:
        from paddleocr import PaddleOCR  # noqa: PLC0415
        return PaddleOCR
    except ImportError:
        logger.warning("PaddleOCR is not installed. OCR functionality will be limited.")
        return None


def _try_import_pdf2image():
    """Attempt to import pdf2image; return None if not installed."""
    try:
        from pdf2image import convert_from_bytes  # noqa: PLC0415
        return convert_from_bytes
    except ImportError:
        logger.warning("pdf2image is not installed. PDF processing will be disabled.")
        return None


def _try_import_pypdf2():
    """Attempt to import PyPDF2; return None if not installed."""
    try:
        import PyPDF2  # noqa: PLC0415
        return PyPDF2
    except ImportError:
        logger.warning("PyPDF2 is not installed. PDF text extraction will be disabled.")
        return None


def _normalize_indicator_name(raw: str) -> str | None:
    """
    Normalize a raw indicator name string to its canonical form.

    Returns the canonical name (e.g. 'ALT') or None if not recognized.
    """
    cleaned = raw.strip().lower().replace(" ", "").replace("（", "(").replace("）", ")")
    return INDICATOR_ALIASES.get(cleaned)


def _parse_indicators_from_text(text: str) -> dict[str, dict[str, Any]]:
    """
    Parse liver function indicators from a block of OCR text.

    Returns a dict keyed by canonical indicator name with value, unit and
    reference range as sub-keys.
    """
    indicators: dict[str, dict[str, Any]] = {}
    lines = text.splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Try to match each known alias against the beginning of the line
        matched_name: str | None = None
        remaining: str = line

        for alias, canonical in INDICATOR_ALIASES.items():
            pattern = re.compile(re.escape(alias), re.IGNORECASE)
            m = pattern.search(line)
            if m:
                matched_name = canonical
                remaining = line[m.end():]
                break

        if matched_name is None:
            continue

        # Extract numeric value
        value_match = _VALUE_PATTERN.search(remaining)
        if not value_match:
            continue
        value = float(value_match.group(1))

        # Extract unit
        unit_match = _UNIT_PATTERN.search(remaining)
        unit = unit_match.group(0) if unit_match else ""

        # Extract reference range
        ref_low: float | None = None
        ref_high: float | None = None
        ref_match = _REF_RANGE_PATTERN.search(remaining)
        if ref_match:
            ref_low = float(ref_match.group(1))
            ref_high = float(ref_match.group(2))

        # Determine abnormal flag based on reference range if available
        abnormal: bool | None = None
        if ref_low is not None and ref_high is not None:
            abnormal = not (ref_low <= value <= ref_high)

        indicators[matched_name] = {
            "value": value,
            "unit": unit,
            "reference_range": f"{ref_low}-{ref_high}" if ref_low is not None else "",
            "abnormal": abnormal,
            "raw_text": line,
        }

    return indicators


class OCRService:
    """
    Service for extracting text and structured indicators from liver function reports.

    Supports PDF (via pdf2image + PaddleOCR or PyPDF2 text extraction) and
    image files (JPG/PNG) via PaddleOCR.
    """

    def __init__(self, language: str = "ch", use_gpu: bool = False):
        """
        Initialize the OCR service.

        Args:
            language: OCR language code. 'ch' supports Chinese + English.
            use_gpu: Whether to use GPU acceleration for PaddleOCR.
        """
        self.language = language
        self.use_gpu = use_gpu
        self._ocr_engine = None  # Lazy initialization

    def _get_ocr_engine(self):
        """Return the PaddleOCR engine, initializing it on first use."""
        if self._ocr_engine is None:
            PaddleOCR = _try_import_paddleocr()
            if PaddleOCR is None:
                raise RuntimeError(
                    "PaddleOCR is required for image OCR but is not installed. "
                    "Install it with: pip install paddleocr"
                )
            self._ocr_engine = PaddleOCR(use_angle_cls=True, lang=self.language, use_gpu=self.use_gpu)
        return self._ocr_engine

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_file(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """
        Process an uploaded file and extract liver function indicators.

        Args:
            file_content: Raw bytes of the uploaded file.
            filename: Original filename (used to determine format).

        Returns:
            Dict with keys:
                - ``raw_text``: full OCR text from the document
                - ``indicators``: dict of extracted indicator data
                - ``page_count``: number of pages processed
                - ``file_type``: 'pdf' or 'image'
        """
        ext = Path(filename).suffix.lower().lstrip(".")
        if ext == "pdf":
            return self._process_pdf(file_content)
        elif ext in {"jpg", "jpeg", "png"}:
            return self._process_image(file_content)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Supported: pdf, jpg, jpeg, png")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _process_pdf(self, file_content: bytes) -> dict[str, Any]:
        """
        Extract text from a PDF file.

        First attempts PaddleOCR on rendered page images (higher accuracy for
        scanned documents).  Falls back to PyPDF2 direct text extraction for
        digital PDFs if pdf2image is unavailable.
        """
        convert_from_bytes = _try_import_pdf2image()

        if convert_from_bytes is not None:
            # Render PDF pages to images and run OCR
            images = convert_from_bytes(file_content, dpi=300)
            full_text_parts: list[str] = []

            for page_image in images:
                # Convert PIL image to bytes for PaddleOCR
                img_bytes = io.BytesIO()
                page_image.save(img_bytes, format="PNG")
                img_bytes.seek(0)

                page_text = self._ocr_image_bytes(img_bytes.read())
                full_text_parts.append(page_text)

            full_text = "\n".join(full_text_parts)
            indicators = _parse_indicators_from_text(full_text)
            return {
                "raw_text": full_text,
                "indicators": indicators,
                "page_count": len(images),
                "file_type": "pdf",
            }

        # Fallback: direct text extraction via PyPDF2
        PyPDF2 = _try_import_pypdf2()
        if PyPDF2 is None:
            raise RuntimeError(
                "Neither pdf2image nor PyPDF2 is installed. "
                "Install one of them to process PDF files."
            )

        reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        pages_text: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        full_text = "\n".join(pages_text)
        indicators = _parse_indicators_from_text(full_text)
        return {
            "raw_text": full_text,
            "indicators": indicators,
            "page_count": len(reader.pages),
            "file_type": "pdf",
        }

    def _process_image(self, file_content: bytes) -> dict[str, Any]:
        """Run PaddleOCR on a raw image (JPG or PNG)."""
        text = self._ocr_image_bytes(file_content)
        indicators = _parse_indicators_from_text(text)
        return {
            "raw_text": text,
            "indicators": indicators,
            "page_count": 1,
            "file_type": "image",
        }

    def _ocr_image_bytes(self, image_bytes: bytes) -> str:
        """
        Run PaddleOCR on raw image bytes and return the concatenated text.

        Writes to a temporary file because PaddleOCR reads from file paths.
        """
        engine = self._get_ocr_engine()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        try:
            result = engine.ocr(tmp_path, cls=True)
            lines: list[str] = []
            if result:
                for page_result in result:
                    if page_result:
                        for item in page_result:
                            # item format: [bbox, (text, confidence)]
                            if item and len(item) >= 2:
                                text_info = item[1]
                                if isinstance(text_info, (list, tuple)) and len(text_info) >= 1:
                                    lines.append(text_info[0])
            return "\n".join(lines)
        finally:
            os.unlink(tmp_path)

    # ------------------------------------------------------------------
    # Utility helpers exposed for testing / re-use
    # ------------------------------------------------------------------

    @staticmethod
    def parse_indicators_from_text(text: str) -> dict[str, dict[str, Any]]:
        """Public wrapper around the module-level text parser."""
        return _parse_indicators_from_text(text)
