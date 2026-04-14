"""
Medical Knowledge Base for liver function indicators.

Contains reference data for 11 common liver function test indicators including:
- Normal reference ranges (with gender/age adjustments)
- Clinical significance
- Abnormal presentation descriptions
- Severity grading logic
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AbnormalSeverity(str, Enum):
    """Severity classification for abnormal indicator values."""

    NORMAL = "normal"          # 正常
    MILD = "mild"              # 轻度异常
    MODERATE = "moderate"      # 中度异常
    SEVERE = "severe"          # 重度异常


@dataclass
class ReferenceRange:
    """Normal reference range with optional gender/age specificity."""

    low: float
    high: float
    unit: str
    gender: str = "all"   # 'male', 'female', or 'all'
    age_group: str = "adult"  # 'adult', 'child', 'elderly'

    def contains(self, value: float) -> bool:
        """Return True if *value* falls within [low, high]."""
        return self.low <= value <= self.high

    def __str__(self) -> str:
        return f"{self.low}-{self.high} {self.unit}"


@dataclass
class IndicatorInfo:
    """Complete clinical information for a single liver function indicator."""

    code: str                          # Canonical code, e.g. 'ALT'
    chinese_name: str                  # Chinese full name
    english_name: str                  # English full name
    reference_ranges: list[ReferenceRange] = field(default_factory=list)
    clinical_significance: str = ""    # What the indicator measures
    high_description: str = ""         # Meaning when elevated
    low_description: str = ""          # Meaning when below normal
    related_conditions: list[str] = field(default_factory=list)  # Associated diseases
    notes: str = ""                    # Additional clinical notes

    # Thresholds for severity grading (multiples of upper normal limit)
    mild_threshold: float = 1.5
    moderate_threshold: float = 3.0
    severe_threshold: float = 5.0

    def get_reference_range(self, gender: str = "all", age_group: str = "adult") -> ReferenceRange | None:
        """Return the best-matching reference range for the given demographics."""
        # Try exact match first
        for rr in self.reference_ranges:
            if rr.gender == gender and rr.age_group == age_group:
                return rr
        # Fall back to gender-specific adult range
        for rr in self.reference_ranges:
            if rr.gender == gender and rr.age_group == "adult":
                return rr
        # Fall back to universal adult range
        for rr in self.reference_ranges:
            if rr.gender == "all" and rr.age_group == "adult":
                return rr
        # Return first available
        return self.reference_ranges[0] if self.reference_ranges else None

    def assess_severity(self, value: float, gender: str = "all", age_group: str = "adult") -> AbnormalSeverity:
        """
        Classify the severity of an abnormal value.

        Uses the upper normal limit (ULN) for elevated values and the lower
        normal limit (LLN) for below-normal values.
        """
        rr = self.get_reference_range(gender, age_group)
        if rr is None:
            return AbnormalSeverity.NORMAL

        if rr.contains(value):
            return AbnormalSeverity.NORMAL

        if value > rr.high:
            ratio = value / rr.high
            if ratio >= self.severe_threshold:
                return AbnormalSeverity.SEVERE
            elif ratio >= self.moderate_threshold:
                return AbnormalSeverity.MODERATE
            elif ratio >= self.mild_threshold:
                return AbnormalSeverity.MILD
            else:
                return AbnormalSeverity.MILD  # Slightly above ULN
        else:
            # Below lower normal limit — use proportion below LLN
            if rr.low == 0:
                return AbnormalSeverity.MILD
            ratio = rr.low / value if value > 0 else float("inf")
            if ratio >= self.severe_threshold:
                return AbnormalSeverity.SEVERE
            elif ratio >= self.moderate_threshold:
                return AbnormalSeverity.MODERATE
            else:
                return AbnormalSeverity.MILD


# ---------------------------------------------------------------------------
# Knowledge Base Data
# ---------------------------------------------------------------------------

_INDICATORS: dict[str, IndicatorInfo] = {
    "ALT": IndicatorInfo(
        code="ALT",
        chinese_name="谷丙转氨酶",
        english_name="Alanine Aminotransferase",
        reference_ranges=[
            ReferenceRange(7, 56, "U/L", gender="all", age_group="adult"),
            ReferenceRange(7, 40, "U/L", gender="female", age_group="adult"),
            ReferenceRange(7, 56, "U/L", gender="male", age_group="adult"),
            ReferenceRange(5, 45, "U/L", gender="all", age_group="child"),
        ],
        clinical_significance=(
            "ALT 是评估肝细胞损伤最敏感的指标之一。主要存在于肝细胞中，"
            "当肝细胞受损时大量释放入血液。"
        ),
        high_description=(
            "升高提示肝细胞损伤，常见于病毒性肝炎、药物性肝损伤、酒精性肝病、"
            "脂肪肝、肝硬化急性期等。"
        ),
        low_description="ALT 偏低通常无临床意义。",
        related_conditions=["病毒性肝炎", "药物性肝损伤", "酒精性肝病", "非酒精性脂肪肝", "肝硬化"],
        notes="ALT 对肝脏损伤高度特异，是肝功能检查的核心指标。",
        mild_threshold=1.5,
        moderate_threshold=3.0,
        severe_threshold=10.0,
    ),

    "AST": IndicatorInfo(
        code="AST",
        chinese_name="谷草转氨酶",
        english_name="Aspartate Aminotransferase",
        reference_ranges=[
            ReferenceRange(10, 40, "U/L", gender="all", age_group="adult"),
            ReferenceRange(10, 35, "U/L", gender="female", age_group="adult"),
            ReferenceRange(10, 40, "U/L", gender="male", age_group="adult"),
        ],
        clinical_significance=(
            "AST 存在于肝细胞、心肌细胞和骨骼肌细胞中。"
            "AST/ALT 比值有助于鉴别肝脏疾病类型。"
        ),
        high_description=(
            "升高见于肝炎、心肌梗塞、肌肉疾病等。"
            "AST/ALT > 2 提示酒精性肝病；比值接近 1 多见于病毒性肝炎。"
        ),
        low_description="AST 偏低通常无临床意义。",
        related_conditions=["肝炎", "心肌梗塞", "酒精性肝病", "肌肉损伤"],
        notes="AST 特异性不及 ALT，需结合其他指标综合判断。",
        mild_threshold=1.5,
        moderate_threshold=3.0,
        severe_threshold=10.0,
    ),

    "ALP": IndicatorInfo(
        code="ALP",
        chinese_name="碱性磷酸酶",
        english_name="Alkaline Phosphatase",
        reference_ranges=[
            ReferenceRange(30, 120, "U/L", gender="all", age_group="adult"),
            ReferenceRange(30, 100, "U/L", gender="female", age_group="adult"),
            ReferenceRange(45, 125, "U/L", gender="male", age_group="adult"),
            ReferenceRange(100, 400, "U/L", gender="all", age_group="child"),
        ],
        clinical_significance=(
            "ALP 是胆汁淤积的重要标志酶，存在于肝脏、骨骼、肠道等组织中。"
        ),
        high_description=(
            "升高提示胆汁淤积性肝病、肝内外胆道梗阻、骨病（如佩吉特病）、"
            "妊娠期生理性升高等。"
        ),
        low_description="ALP 偏低见于甲状腺功能减退、恶性贫血等。",
        related_conditions=["胆汁淤积", "胆道梗阻", "原发性硬化性胆管炎", "骨转移癌"],
        notes="儿童及青少年因骨骼发育旺盛，ALP 生理性偏高。",
        mild_threshold=1.5,
        moderate_threshold=3.0,
        severe_threshold=5.0,
    ),

    "GGT": IndicatorInfo(
        code="GGT",
        chinese_name="γ-谷氨酰转移酶",
        english_name="Gamma-Glutamyl Transferase",
        reference_ranges=[
            ReferenceRange(9, 48, "U/L", gender="all", age_group="adult"),
            ReferenceRange(9, 36, "U/L", gender="female", age_group="adult"),
            ReferenceRange(10, 60, "U/L", gender="male", age_group="adult"),
        ],
        clinical_significance=(
            "GGT 对酒精性肝病最为敏感，也是胆汁淤积和肝癌的敏感标志物。"
        ),
        high_description=(
            "升高见于酒精性肝病、胆汁淤积、脂肪肝、肝癌、药物性肝损伤等。"
            "长期饮酒者 GGT 往往显著升高。"
        ),
        low_description="GGT 偏低通常无临床意义。",
        related_conditions=["酒精性肝病", "胆汁淤积", "肝癌", "脂肪肝"],
        notes="GGT 对酒精摄入非常敏感，是监测戒酒的良好指标。",
        mild_threshold=1.5,
        moderate_threshold=3.0,
        severe_threshold=5.0,
    ),

    "TBIL": IndicatorInfo(
        code="TBIL",
        chinese_name="总胆红素",
        english_name="Total Bilirubin",
        reference_ranges=[
            ReferenceRange(3.4, 20.5, "μmol/L", gender="all", age_group="adult"),
        ],
        clinical_significance=(
            "TBIL 是评估肝脏胆红素代谢能力的指标，包括直接胆红素和间接胆红素。"
            "升高表现为黄疸。"
        ),
        high_description=(
            "升高（黄疸）分为溶血性、肝细胞性、阻塞性三类。"
            "可见于肝炎、胆道梗阻、溶血性疾病等。"
        ),
        low_description="TBIL 偏低通常无临床意义。",
        related_conditions=["黄疸", "肝炎", "胆道梗阻", "溶血性贫血", "吉尔伯特综合征"],
        notes="TBIL > 34.2 μmol/L 出现临床可见黄疸。",
        mild_threshold=1.5,
        moderate_threshold=3.0,
        severe_threshold=10.0,
    ),

    "DBIL": IndicatorInfo(
        code="DBIL",
        chinese_name="直接胆红素",
        english_name="Direct Bilirubin",
        reference_ranges=[
            ReferenceRange(0, 6.8, "μmol/L", gender="all", age_group="adult"),
        ],
        clinical_significance=(
            "DBIL（结合胆红素）由肝脏将间接胆红素与葡萄糖醛酸结合后形成，"
            "经胆道排入肠道。升高提示肝脏排泄功能障碍或胆道梗阻。"
        ),
        high_description=(
            "升高提示肝脏排泄障碍或胆道梗阻，见于胆汁淤积性肝病、"
            "胆道结石、胆管癌等。"
        ),
        low_description="DBIL 偏低通常无临床意义。",
        related_conditions=["胆汁淤积", "胆道梗阻", "肝炎"],
        notes="DBIL/TBIL > 0.5 提示阻塞性或肝细胞性黄疸。",
    ),

    "IBIL": IndicatorInfo(
        code="IBIL",
        chinese_name="间接胆红素",
        english_name="Indirect Bilirubin",
        reference_ranges=[
            ReferenceRange(1.7, 13.7, "μmol/L", gender="all", age_group="adult"),
        ],
        clinical_significance=(
            "IBIL（非结合胆红素）是血红蛋白分解产物，由肝脏摄取后转化为直接胆红素。"
        ),
        high_description=(
            "升高见于溶血性疾病、吉尔伯特综合征、新生儿黄疸等。"
            "IBIL 占 TBIL 80% 以上提示溶血性黄疸。"
        ),
        low_description="IBIL 偏低通常无临床意义。",
        related_conditions=["溶血性贫血", "吉尔伯特综合征", "新生儿黄疸"],
        notes="",
    ),

    "ALB": IndicatorInfo(
        code="ALB",
        chinese_name="白蛋白",
        english_name="Albumin",
        reference_ranges=[
            ReferenceRange(35, 55, "g/L", gender="all", age_group="adult"),
            ReferenceRange(32, 55, "g/L", gender="all", age_group="elderly"),
        ],
        clinical_significance=(
            "ALB 是评估肝脏合成功能的重要指标，也反映机体营养状态。"
            "半衰期约 20 天，是慢性肝病预后评估的关键指标。"
        ),
        high_description="ALB 升高见于严重脱水。",
        low_description=(
            "降低见于慢性肝病（肝硬化）、营养不良、肾病综合征、"
            "慢性感染、恶性肿瘤等。"
        ),
        related_conditions=["肝硬化", "肾病综合征", "营养不良", "慢性感染"],
        notes=(
            "ALB < 30 g/L 为重度低白蛋白血症，提示肝脏合成功能严重受损或"
            "严重营养不良。"
        ),
        mild_threshold=0.85,  # Ratio relative to lower normal for low-side severity
        moderate_threshold=0.70,
        severe_threshold=0.55,
    ),

    "GLB": IndicatorInfo(
        code="GLB",
        chinese_name="球蛋白",
        english_name="Globulin",
        reference_ranges=[
            ReferenceRange(20, 35, "g/L", gender="all", age_group="adult"),
        ],
        clinical_significance=(
            "GLB 由免疫系统产生，反映机体的免疫功能状态。"
            "GLB = TP - ALB。"
        ),
        high_description=(
            "升高见于慢性肝病（肝硬化）、自身免疫性肝病、慢性感染、"
            "多发性骨髓瘤等。"
        ),
        low_description="降低见于免疫功能低下，如长期使用糖皮质激素或先天性免疫缺陷。",
        related_conditions=["肝硬化", "自身免疫性肝病", "多发性骨髓瘤", "慢性感染"],
        notes="",
    ),

    "A/G": IndicatorInfo(
        code="A/G",
        chinese_name="白蛋白/球蛋白比值",
        english_name="Albumin/Globulin Ratio",
        reference_ranges=[
            ReferenceRange(1.2, 2.5, "", gender="all", age_group="adult"),
        ],
        clinical_significance=(
            "A/G 比值是综合评估肝脏功能和免疫状态的指标。"
            "正常情况下 ALB > GLB，比值 > 1。"
        ),
        high_description="A/G 比值升高通常无临床意义。",
        low_description=(
            "比值 < 1（倒置）提示 ALB 降低或 GLB 升高，"
            "见于慢性肝病、肝硬化、自身免疫性疾病等。"
        ),
        related_conditions=["肝硬化", "自身免疫性肝炎", "慢性活动性肝炎"],
        notes="A/G 比值倒置是慢性肝病预后不良的指标之一。",
    ),

    "TP": IndicatorInfo(
        code="TP",
        chinese_name="总蛋白",
        english_name="Total Protein",
        reference_ranges=[
            ReferenceRange(60, 83, "g/L", gender="all", age_group="adult"),
            ReferenceRange(55, 80, "g/L", gender="all", age_group="elderly"),
        ],
        clinical_significance=(
            "TP = ALB + GLB，是评估肝脏合成功能和机体营养状态的综合指标。"
        ),
        high_description=(
            "升高见于严重脱水、多发性骨髓瘤、慢性感染伴球蛋白升高等。"
        ),
        low_description=(
            "降低见于慢性肝病、营养不良、肾病综合征、"
            "慢性消耗性疾病等。"
        ),
        related_conditions=["肝硬化", "营养不良", "肾病综合征", "多发性骨髓瘤"],
        notes="",
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class MedicalKnowledgeBase:
    """
    Query interface for the liver function indicator knowledge base.

    Provides indicator lookup, reference range queries, and severity assessment.
    """

    def __init__(self):
        self._data = _INDICATORS

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def get_indicator(self, code: str) -> IndicatorInfo | None:
        """Return the IndicatorInfo for *code* (case-insensitive), or None."""
        return self._data.get(code.upper())

    def list_indicators(self) -> list[str]:
        """Return a list of all supported indicator codes."""
        return list(self._data.keys())

    def is_supported(self, code: str) -> bool:
        """Return True if *code* is in the knowledge base."""
        return code.upper() in self._data

    # ------------------------------------------------------------------
    # Assessment helpers
    # ------------------------------------------------------------------

    def assess_indicator(
        self,
        code: str,
        value: float,
        gender: str = "all",
        age_group: str = "adult",
    ) -> dict[str, Any]:
        """
        Assess a single indicator value against the reference range.

        Returns a dict with:
            - ``code``: indicator code
            - ``value``: provided value
            - ``reference_range``: reference range string
            - ``unit``: unit string
            - ``severity``: AbnormalSeverity enum value
            - ``is_abnormal``: bool
            - ``high_description`` / ``low_description``: clinical descriptions
            - ``clinical_significance``: clinical meaning
            - ``related_conditions``: list of associated conditions
        """
        info = self.get_indicator(code)
        if info is None:
            return {
                "code": code,
                "value": value,
                "severity": AbnormalSeverity.NORMAL,
                "is_abnormal": False,
                "error": f"Indicator '{code}' not found in knowledge base.",
            }

        rr = info.get_reference_range(gender, age_group)
        severity = info.assess_severity(value, gender, age_group)
        is_abnormal = severity != AbnormalSeverity.NORMAL
        direction: str = ""
        description: str = ""

        if is_abnormal and rr:
            if value > rr.high:
                direction = "high"
                description = info.high_description
            else:
                direction = "low"
                description = info.low_description

        return {
            "code": code,
            "chinese_name": info.chinese_name,
            "english_name": info.english_name,
            "value": value,
            "reference_range": str(rr) if rr else "N/A",
            "unit": rr.unit if rr else "",
            "severity": severity,
            "is_abnormal": is_abnormal,
            "direction": direction,
            "description": description,
            "clinical_significance": info.clinical_significance,
            "related_conditions": info.related_conditions,
            "notes": info.notes,
        }

    def assess_report(
        self,
        indicators: dict[str, float | dict],
        gender: str = "all",
        age_group: str = "adult",
    ) -> dict[str, dict[str, Any]]:
        """
        Assess all indicators in a report.

        *indicators* may be either ``{code: float}`` or
        ``{code: {"value": float, ...}}``.

        Returns a dict mapping each code to its assessment result.
        """
        results: dict[str, dict[str, Any]] = {}
        for code, data in indicators.items():
            if isinstance(data, dict):
                value = data.get("value")
                if value is None:
                    continue
                value = float(value)
            else:
                value = float(data)
            results[code] = self.assess_indicator(code, value, gender, age_group)
        return results

    def get_abnormal_indicators(
        self,
        indicators: dict[str, float | dict],
        gender: str = "all",
        age_group: str = "adult",
    ) -> dict[str, dict[str, Any]]:
        """Return only the abnormal indicator assessments from a report."""
        all_assessments = self.assess_report(indicators, gender, age_group)
        return {
            code: result
            for code, result in all_assessments.items()
            if result.get("is_abnormal")
        }
