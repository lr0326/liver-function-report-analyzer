"""
AnalysisResult ORM model.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SeverityLevel(str, PyEnum):
    Normal = "Normal"
    Mild = "Mild"
    Moderate = "Moderate"
    Severe = "Severe"


class AnalysisResult(Base):
    """Stores the result of analysing a liver-function report."""

    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    report_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("reports.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # Extracted lab indicators stored as JSON
    # Format: {"ALT": {"value": 45, "unit": "U/L", "status": "normal"}, ...}
    extracted_indicators: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Overall risk score 0-100
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    severity_level: Mapped[SeverityLevel | None] = mapped_column(
        Enum(SeverityLevel, name="severity_level_enum"), nullable=True
    )

    # Lists stored as JSON
    abnormal_indicators: Mapped[list | None] = mapped_column(JSON, nullable=True)
    health_suggestions: Mapped[list | None] = mapped_column(JSON, nullable=True)

    follow_up_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)

    analysis_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship
    report: Mapped["Report"] = relationship(  # noqa: F821
        "Report", back_populates="analysis_result"
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return a concise summary of the analysis."""
        return {
            "id": self.id,
            "report_id": self.report_id,
            "risk_score": self.risk_score,
            "severity_level": self.severity_level.value if self.severity_level else None,
            "abnormal_count": (
                len(self.abnormal_indicators) if self.abnormal_indicators else 0
            ),
            "analysis_timestamp": (
                self.analysis_timestamp.isoformat() if self.analysis_timestamp else None
            ),
        }

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "report_id": self.report_id,
            "extracted_indicators": self.extracted_indicators,
            "risk_score": self.risk_score,
            "severity_level": self.severity_level.value if self.severity_level else None,
            "abnormal_indicators": self.abnormal_indicators,
            "health_suggestions": self.health_suggestions,
            "follow_up_plan": self.follow_up_plan,
            "ai_analysis": self.ai_analysis,
            "analysis_timestamp": (
                self.analysis_timestamp.isoformat() if self.analysis_timestamp else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<AnalysisResult id={self.id!r} report_id={self.report_id!r} "
            f"risk_score={self.risk_score!r}>"
        )
