"""
HealthRecord ORM model.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HealthStatus(str, PyEnum):
    Normal = "Normal"
    Abnormal = "Abnormal"
    Alert = "Alert"


class HealthRecord(Base):
    """A single health-status record tied to a user (optionally a report)."""

    __tablename__ = "health_records"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    report_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("reports.id", ondelete="SET NULL"), nullable=True, index=True
    )
    record_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    health_status: Mapped[HealthStatus] = mapped_column(
        Enum(HealthStatus, name="health_status_enum"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="health_records")  # noqa: F821
    report: Mapped["Report | None"] = relationship("Report")  # noqa: F821

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "report_id": self.report_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "health_status": self.health_status.value if self.health_status else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<HealthRecord id={self.id!r} user_id={self.user_id!r} "
            f"status={self.health_status!r}>"
        )
