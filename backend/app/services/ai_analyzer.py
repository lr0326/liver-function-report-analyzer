"""
AI Analysis Engine for liver function report interpretation.

Integrates with OpenAI GPT (or a local Ollama-compatible LLM) to generate
professional medical analysis reports in Chinese.

The engine accepts structured indicator data (extracted by OCRService and
assessed by MedicalKnowledgeBase) and produces a narrative analysis covering:
- Interpretation of each abnormal indicator
- Identified health risk patterns
- Actionable health recommendations
- Follow-up plan
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """你是一位经验丰富的肝病科医生和医学分析专家。
你的任务是对患者的肝功能检查结果进行专业、详细的医学解读。

请遵循以下原则：
1. 语言使用专业但易于患者理解的中文
2. 结合所有异常指标进行综合分析，而不是孤立解读每个指标
3. 识别可能的疾病模式和潜在健康风险
4. 给出实际可行的健康建议
5. 在结论中明确说明是否需要就医
6. 始终提醒患者本分析仅供参考，不能替代专业医生诊断

输出格式要求：返回 JSON 格式，包含以下字段：
{
  "summary": "综合评估摘要（2-3句话）",
  "abnormal_analysis": "对所有异常指标的详细分析",
  "risk_assessment": "识别到的健康风险和可能的疾病模式",
  "health_recommendations": ["建议1", "建议2", ...],
  "follow_up_plan": "随访计划建议",
  "urgency_level": "immediate/soon/routine/none（就医紧迫程度）",
  "disclaimer": "免责声明"
}"""

_USER_PROMPT_TEMPLATE = """请分析以下肝功能检查结果：

**患者信息：**
- 性别：{gender}
- 年龄组：{age_group}

**检查指标概览：**
{indicators_summary}

**异常指标详情：**
{abnormal_details}

**原始报告文本（如有）：**
{raw_text}

请根据以上信息提供专业的医学分析。"""


def _format_indicators_summary(indicators: dict[str, dict[str, Any]]) -> str:
    """Format all indicators into a human-readable table string."""
    lines = []
    for code, data in indicators.items():
        if isinstance(data, dict):
            value = data.get("value", "N/A")
            unit = data.get("unit", "")
            ref = data.get("reference_range", "")
            severity = data.get("severity", "")
            abnormal = "⚠️ 异常" if data.get("is_abnormal") else "✓ 正常"
            lines.append(
                f"- {code}: {value} {unit}  (参考范围: {ref})  [{severity}] {abnormal}"
            )
        else:
            lines.append(f"- {code}: {data}")
    return "\n".join(lines) if lines else "无指标数据"


def _format_abnormal_details(abnormal_indicators: dict[str, dict[str, Any]]) -> str:
    """Format detailed information about abnormal indicators."""
    if not abnormal_indicators:
        return "未发现异常指标，所有检测指标均在正常范围内。"

    parts = []
    for code, data in abnormal_indicators.items():
        direction = data.get("direction", "")
        direction_str = "偏高" if direction == "high" else "偏低" if direction == "low" else "异常"
        parts.append(
            f"**{code} ({data.get('chinese_name', code)})**: "
            f"检测值 {data.get('value')} {data.get('unit', '')}，"
            f"参考范围 {data.get('reference_range', 'N/A')}，"
            f"{direction_str}（{data.get('severity', '')}）。\n"
            f"临床意义：{data.get('description', '')} "
            f"相关疾病：{', '.join(data.get('related_conditions', []))}"
        )
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

def _severity_value(sev) -> str:
    """Return the plain string value of a severity field (enum or str)."""
    if hasattr(sev, "value"):
        return sev.value
    return str(sev).lower()


class _BaseProvider:
    """Abstract base for LLM provider implementations."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class _OpenAIProvider(_BaseProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str = "gpt-4", max_tokens: int = 2000):
        try:
            from openai import OpenAI  # noqa: PLC0415
            self._client = OpenAI(api_key=api_key)
        except ImportError as exc:
            raise RuntimeError(
                "The 'openai' package is required. Install with: pip install openai"
            ) from exc
        self.model = model
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=self.max_tokens,
            temperature=0.3,  # Low temperature for consistent medical analysis
        )
        return response.choices[0].message.content or ""


class _LocalLLMProvider(_BaseProvider):
    """Local LLM provider via Ollama-compatible REST API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        try:
            import requests  # noqa: PLC0415
            self._requests = requests
        except ImportError as exc:
            raise RuntimeError(
                "The 'requests' package is required. Install with: pip install requests"
            ) from exc
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        response = self._requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("message", {}).get("content", "")


# ---------------------------------------------------------------------------
# Main service
# ---------------------------------------------------------------------------

class AIAnalyzer:
    """
    AI-powered analyzer for liver function reports.

    Supports OpenAI GPT and local Ollama-compatible LLMs.
    Produces structured JSON analysis reports in Chinese.
    """

    def __init__(
        self,
        openai_api_key: str = "",
        openai_model: str = "gpt-4",
        openai_max_tokens: int = 2000,
        use_local_llm: bool = False,
        local_llm_url: str = "http://localhost:11434",
        local_llm_model: str = "llama3",
    ):
        """
        Initialize the AI analyzer.

        If *use_local_llm* is True, the local LLM provider is used regardless of
        whether an OpenAI key is provided.  If neither is configured, a fallback
        rule-based analysis is used.
        """
        self._provider: _BaseProvider | None = None

        if use_local_llm:
            try:
                self._provider = _LocalLLMProvider(local_llm_url, local_llm_model)
                logger.info("AIAnalyzer: using local LLM at %s (%s)", local_llm_url, local_llm_model)
            except RuntimeError as exc:
                logger.warning("AIAnalyzer: local LLM setup failed — %s", exc)
        elif openai_api_key:
            try:
                self._provider = _OpenAIProvider(openai_api_key, openai_model, openai_max_tokens)
                logger.info("AIAnalyzer: using OpenAI model %s", openai_model)
            except RuntimeError as exc:
                logger.warning("AIAnalyzer: OpenAI setup failed — %s", exc)

        if self._provider is None:
            logger.warning(
                "AIAnalyzer: no LLM provider configured; falling back to rule-based analysis."
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(
        self,
        indicators: dict[str, dict[str, Any]],
        abnormal_indicators: dict[str, dict[str, Any]],
        gender: str = "all",
        age_group: str = "adult",
        raw_text: str = "",
    ) -> dict[str, Any]:
        """
        Analyze a set of liver function indicators.

        Args:
            indicators: Full set of assessed indicators (from MedicalKnowledgeBase).
            abnormal_indicators: Subset of only the abnormal indicators.
            gender: Patient gender ('male', 'female', 'all').
            age_group: Patient age group ('adult', 'child', 'elderly').
            raw_text: Optional original OCR text for additional context.

        Returns:
            Structured analysis dict with keys: summary, abnormal_analysis,
            risk_assessment, health_recommendations, follow_up_plan,
            urgency_level, disclaimer.
        """
        if self._provider is not None:
            return self._llm_analyze(indicators, abnormal_indicators, gender, age_group, raw_text)
        else:
            return self._rule_based_analyze(indicators, abnormal_indicators)

    # ------------------------------------------------------------------
    # LLM analysis
    # ------------------------------------------------------------------

    def _llm_analyze(
        self,
        indicators: dict[str, dict[str, Any]],
        abnormal_indicators: dict[str, dict[str, Any]],
        gender: str,
        age_group: str,
        raw_text: str,
    ) -> dict[str, Any]:
        """Generate analysis via the configured LLM provider."""
        gender_label = {"male": "男", "female": "女"}.get(gender, "未知")
        age_label = {"adult": "成人", "child": "儿童", "elderly": "老年人"}.get(age_group, "成人")

        user_prompt = _USER_PROMPT_TEMPLATE.format(
            gender=gender_label,
            age_group=age_label,
            indicators_summary=_format_indicators_summary(indicators),
            abnormal_details=_format_abnormal_details(abnormal_indicators),
            raw_text=raw_text[:500] if raw_text else "无",
        )

        try:
            raw_response = self._provider.generate(_SYSTEM_PROMPT, user_prompt)  # type: ignore[union-attr]
            # Extract JSON from the response
            result = self._parse_llm_response(raw_response)
            return result
        except Exception as exc:
            logger.exception("LLM analysis failed: %s", exc)
            # Fallback to rule-based on LLM failure
            return self._rule_based_analyze(indicators, abnormal_indicators)

    @staticmethod
    def _parse_llm_response(raw: str) -> dict[str, Any]:
        """Extract a JSON object from LLM output (handles markdown code fences)."""
        # Remove markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            # Strip opening and closing fences
            lines = [l for l in lines if not l.startswith("```")]
            cleaned = "\n".join(lines)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Best-effort: return a structured dict with the raw text
            return {
                "summary": "AI 分析结果解析失败，请查看原始分析文本。",
                "abnormal_analysis": raw,
                "risk_assessment": "",
                "health_recommendations": [],
                "follow_up_plan": "建议咨询医生。",
                "urgency_level": "soon",
                "disclaimer": "本分析仅供参考，不能替代专业医生诊断。",
            }

    # ------------------------------------------------------------------
    # Rule-based fallback analysis
    # ------------------------------------------------------------------

    def _rule_based_analyze(
        self,
        indicators: dict[str, dict[str, Any]],
        abnormal_indicators: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Generate a basic analysis without an LLM.

        Uses knowledge base data to produce a meaningful but less nuanced report.
        """
        n_abnormal = len(abnormal_indicators)
        severe_codes = [
            code for code, data in abnormal_indicators.items()
            if _severity_value(data.get("severity", "")) == "severe"
        ]
        moderate_codes = [
            code for code, data in abnormal_indicators.items()
            if _severity_value(data.get("severity", "")) == "moderate"
        ]

        # Urgency determination
        if severe_codes:
            urgency = "immediate"
        elif moderate_codes:
            urgency = "soon"
        elif n_abnormal > 0:
            urgency = "routine"
        else:
            urgency = "none"

        # Summary
        if n_abnormal == 0:
            summary = "本次肝功能检查各项指标均在正常范围内，肝功能状况良好。"
        else:
            abnormal_list = "、".join(abnormal_indicators.keys())
            summary = (
                f"本次肝功能检查发现 {n_abnormal} 项指标异常：{abnormal_list}。"
                "建议结合临床症状进一步评估。"
            )

        # Abnormal analysis
        abnormal_parts = []
        for code, data in abnormal_indicators.items():
            direction = "偏高" if data.get("direction") == "high" else "偏低"
            abnormal_parts.append(
                f"{code}（{data.get('chinese_name', code)}）{direction}，"
                f"检测值 {data.get('value')} {data.get('unit', '')}，"
                f"参考范围 {data.get('reference_range', 'N/A')}。"
                f"{data.get('description', '')}"
            )
        abnormal_analysis = "\n".join(abnormal_parts) if abnormal_parts else "所有指标正常。"

        # Generic recommendations
        recommendations: list[str] = ["定期复查肝功能，监测指标变化趋势。"]
        if n_abnormal > 0:
            recommendations += [
                "尽量避免饮酒，减少肝脏负担。",
                "清淡饮食，减少高脂肪、高糖食物摄入。",
                "避免自行服用可能损害肝脏的药物或保健品。",
                "保持规律作息，避免过度劳累。",
            ]
        if severe_codes:
            recommendations.insert(0, "⚠️ 存在重度异常指标，建议尽快就医进行进一步检查。")
        elif moderate_codes:
            recommendations.insert(0, "存在中度异常指标，建议近期就医就诊。")

        # Follow-up plan
        if urgency == "immediate":
            follow_up = "建议尽快（1-3天内）就医，进行肝脏超声等进一步检查。"
        elif urgency == "soon":
            follow_up = "建议1-2周内就医复诊，进行相关检查。"
        elif urgency == "routine":
            follow_up = "建议1个月内复查肝功能，观察指标变化。"
        else:
            follow_up = "建议6-12个月后定期复查肝功能。"

        # Risk assessment
        if n_abnormal == 0:
            risk = "未发现明显肝功能异常风险。"
        else:
            conditions = set()
            for data in abnormal_indicators.values():
                conditions.update(data.get("related_conditions", []))
            conditions_str = "、".join(list(conditions)[:5]) if conditions else "待评估"
            risk = f"异常指标提示可能存在以下风险：{conditions_str}。需结合病史和其他检查综合判断。"

        return {
            "summary": summary,
            "abnormal_analysis": abnormal_analysis,
            "risk_assessment": risk,
            "health_recommendations": recommendations,
            "follow_up_plan": follow_up,
            "urgency_level": urgency,
            "disclaimer": "本分析结果由自动系统生成，仅供参考，不能替代专业医生的诊断和治疗建议。如有疑问请咨询医生。",
        }
