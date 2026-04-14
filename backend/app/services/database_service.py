"""
Data-access layer: CRUD operations for all ORM models.

All functions accept an optional ``session`` parameter so they can be
composed within a single transaction by the caller.  When no session is
provided a new one is created and committed automatically.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.database import db_session, get_db
from app.models.analysis_result import AnalysisResult, SeverityLevel
from app.models.health_record import HealthRecord, HealthStatus
from app.models.report import FileType, Report, ReportStatus
from app.models.user import Gender, User

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _commit_or_flush(session: Session, *, owns_session: bool) -> None:
    """Commit if we own the session, otherwise just flush."""
    if owns_session:
        session.commit()
    else:
        session.flush()


def _session(provided: Session | None):
    """Return (session, owns_session) tuple."""
    if provided is not None:
        return provided, False
    return get_db(), True


# ===========================================================================
# User CRUD
# ===========================================================================


def create_user(
    username: str,
    email: str,
    password: str,
    full_name: str | None = None,
    age: int | None = None,
    gender: str | Gender | None = None,
    *,
    session: Session | None = None,
) -> User:
    """
    Create a new user.

    Args:
        username: Unique username.
        email: Unique e-mail address.
        password: Plain-text password (will be hashed).
        full_name: Optional display name.
        age: Optional age in years.
        gender: Optional Gender enum value or string ('Male'/'Female'/'Other').
        session: Optional external session for transaction composition.

    Returns:
        The newly created User instance.
    """
    s, owns = _session(session)
    try:
        if isinstance(gender, str):
            gender = Gender(gender)
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            age=age,
            gender=gender,
        )
        user.set_password(password)
        s.add(user)
        _commit_or_flush(s, owns_session=owns)
        s.refresh(user)
        logger.info("User created: %s", user.id)
        return user
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def get_user_by_id(user_id: str, *, session: Session | None = None) -> User | None:
    s, owns = _session(session)
    try:
        return s.get(User, user_id)
    finally:
        if owns:
            s.close()


def get_user_by_username(username: str, *, session: Session | None = None) -> User | None:
    s, owns = _session(session)
    try:
        return s.query(User).filter(User.username == username).first()
    finally:
        if owns:
            s.close()


def get_user_by_email(email: str, *, session: Session | None = None) -> User | None:
    s, owns = _session(session)
    try:
        return s.query(User).filter(User.email == email).first()
    finally:
        if owns:
            s.close()


def update_user(
    user_id: str,
    *,
    session: Session | None = None,
    **kwargs: Any,
) -> User | None:
    """
    Update an existing user's fields.

    Accepted kwargs: ``full_name``, ``age``, ``gender``, ``password``,
    ``email``, ``username``.
    """
    s, owns = _session(session)
    try:
        user = s.get(User, user_id)
        if user is None:
            return None

        for key, value in kwargs.items():
            if key == "password":
                user.set_password(value)
            elif key == "gender" and isinstance(value, str):
                setattr(user, key, Gender(value))
            else:
                setattr(user, key, value)

        user.updated_at = datetime.now(timezone.utc)
        _commit_or_flush(s, owns_session=owns)
        s.refresh(user)
        return user
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def delete_user(user_id: str, *, session: Session | None = None) -> bool:
    s, owns = _session(session)
    try:
        user = s.get(User, user_id)
        if user is None:
            return False
        s.delete(user)
        _commit_or_flush(s, owns_session=owns)
        return True
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def get_all_users(*, session: Session | None = None) -> list[User]:
    s, owns = _session(session)
    try:
        return s.query(User).order_by(User.created_at.desc()).all()
    finally:
        if owns:
            s.close()


# ===========================================================================
# Report CRUD
# ===========================================================================


def create_report(
    filename: str,
    *,
    user_id: str | None = None,
    file_type: str | FileType | None = None,
    file_path: str | None = None,
    raw_text: str | None = None,
    session: Session | None = None,
) -> Report:
    s, owns = _session(session)
    try:
        if isinstance(file_type, str):
            file_type = FileType(file_type.upper())
        report = Report(
            user_id=user_id,
            filename=filename,
            file_type=file_type,
            file_path=file_path,
            raw_text=raw_text,
            status=ReportStatus.Pending,
        )
        s.add(report)
        _commit_or_flush(s, owns_session=owns)
        s.refresh(report)
        logger.info("Report created: %s", report.id)
        return report
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def get_report_by_id(report_id: str, *, session: Session | None = None) -> Report | None:
    s, owns = _session(session)
    try:
        return s.get(Report, report_id)
    finally:
        if owns:
            s.close()


def get_reports_by_user(
    user_id: str,
    *,
    limit: int = 20,
    offset: int = 0,
    session: Session | None = None,
) -> list[Report]:
    s, owns = _session(session)
    try:
        return (
            s.query(Report)
            .filter(Report.user_id == user_id)
            .order_by(Report.upload_date.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    finally:
        if owns:
            s.close()


def update_report_status(
    report_id: str,
    status: str | ReportStatus,
    *,
    session: Session | None = None,
) -> Report | None:
    s, owns = _session(session)
    try:
        report = s.get(Report, report_id)
        if report is None:
            return None
        if isinstance(status, str):
            status = ReportStatus(status)
        report.status = status
        report.updated_at = datetime.now(timezone.utc)
        _commit_or_flush(s, owns_session=owns)
        s.refresh(report)
        return report
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def delete_report(report_id: str, *, session: Session | None = None) -> bool:
    s, owns = _session(session)
    try:
        report = s.get(Report, report_id)
        if report is None:
            return False
        s.delete(report)
        _commit_or_flush(s, owns_session=owns)
        return True
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def get_report_count(user_id: str, *, session: Session | None = None) -> int:
    s, owns = _session(session)
    try:
        return s.query(Report).filter(Report.user_id == user_id).count()
    finally:
        if owns:
            s.close()


# ===========================================================================
# AnalysisResult CRUD
# ===========================================================================


def create_analysis_result(
    report_id: str,
    *,
    extracted_indicators: dict | None = None,
    risk_score: float | None = None,
    severity_level: str | SeverityLevel | None = None,
    abnormal_indicators: list | None = None,
    health_suggestions: list | None = None,
    follow_up_plan: str | None = None,
    ai_analysis: str | None = None,
    analysis_timestamp: datetime | None = None,
    session: Session | None = None,
) -> AnalysisResult:
    s, owns = _session(session)
    try:
        if isinstance(severity_level, str):
            severity_level = SeverityLevel(severity_level)
        result = AnalysisResult(
            report_id=report_id,
            extracted_indicators=extracted_indicators,
            risk_score=risk_score,
            severity_level=severity_level,
            abnormal_indicators=abnormal_indicators,
            health_suggestions=health_suggestions,
            follow_up_plan=follow_up_plan,
            ai_analysis=ai_analysis,
            analysis_timestamp=analysis_timestamp or datetime.now(timezone.utc),
        )
        s.add(result)
        _commit_or_flush(s, owns_session=owns)
        s.refresh(result)
        logger.info("AnalysisResult created: %s", result.id)
        return result
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def get_analysis_by_report_id(
    report_id: str, *, session: Session | None = None
) -> AnalysisResult | None:
    s, owns = _session(session)
    try:
        return (
            s.query(AnalysisResult)
            .filter(AnalysisResult.report_id == report_id)
            .first()
        )
    finally:
        if owns:
            s.close()


def get_analysis_by_id(
    analysis_id: str, *, session: Session | None = None
) -> AnalysisResult | None:
    s, owns = _session(session)
    try:
        return s.get(AnalysisResult, analysis_id)
    finally:
        if owns:
            s.close()


def update_analysis_result(
    analysis_id: str,
    *,
    session: Session | None = None,
    **kwargs: Any,
) -> AnalysisResult | None:
    s, owns = _session(session)
    try:
        result = s.get(AnalysisResult, analysis_id)
        if result is None:
            return None
        for key, value in kwargs.items():
            if key == "severity_level" and isinstance(value, str):
                value = SeverityLevel(value)
            setattr(result, key, value)
        result.updated_at = datetime.now(timezone.utc)
        _commit_or_flush(s, owns_session=owns)
        s.refresh(result)
        return result
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def get_latest_analysis(
    user_id: str, *, session: Session | None = None
) -> AnalysisResult | None:
    """Return the most recent AnalysisResult for the given user."""
    s, owns = _session(session)
    try:
        return (
            s.query(AnalysisResult)
            .join(Report, AnalysisResult.report_id == Report.id)
            .filter(Report.user_id == user_id)
            .order_by(AnalysisResult.analysis_timestamp.desc())
            .first()
        )
    finally:
        if owns:
            s.close()


# ===========================================================================
# HealthRecord CRUD
# ===========================================================================


def create_health_record(
    user_id: str,
    health_status: str | HealthStatus,
    *,
    report_id: str | None = None,
    notes: str | None = None,
    record_date: datetime | None = None,
    session: Session | None = None,
) -> HealthRecord:
    s, owns = _session(session)
    try:
        if isinstance(health_status, str):
            health_status = HealthStatus(health_status)
        record = HealthRecord(
            user_id=user_id,
            report_id=report_id,
            health_status=health_status,
            notes=notes,
            record_date=record_date or datetime.now(timezone.utc),
        )
        s.add(record)
        _commit_or_flush(s, owns_session=owns)
        s.refresh(record)
        logger.info("HealthRecord created: %s", record.id)
        return record
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def get_health_records_by_user(
    user_id: str,
    *,
    limit: int = 50,
    session: Session | None = None,
) -> list[HealthRecord]:
    s, owns = _session(session)
    try:
        return (
            s.query(HealthRecord)
            .filter(HealthRecord.user_id == user_id)
            .order_by(HealthRecord.record_date.desc())
            .limit(limit)
            .all()
        )
    finally:
        if owns:
            s.close()


def get_health_record_by_id(
    record_id: str, *, session: Session | None = None
) -> HealthRecord | None:
    s, owns = _session(session)
    try:
        return s.get(HealthRecord, record_id)
    finally:
        if owns:
            s.close()


def update_health_record(
    record_id: str,
    *,
    session: Session | None = None,
    **kwargs: Any,
) -> HealthRecord | None:
    s, owns = _session(session)
    try:
        record = s.get(HealthRecord, record_id)
        if record is None:
            return None
        for key, value in kwargs.items():
            if key == "health_status" and isinstance(value, str):
                value = HealthStatus(value)
            setattr(record, key, value)
        record.updated_at = datetime.now(timezone.utc)
        _commit_or_flush(s, owns_session=owns)
        s.refresh(record)
        return record
    except Exception:
        if owns:
            s.rollback()
        raise
    finally:
        if owns:
            s.close()


def get_health_status_trend(
    user_id: str,
    *,
    days: int = 90,
    session: Session | None = None,
) -> list[HealthRecord]:
    """
    Return health records for the given user within the last *days* days,
    ordered from oldest to newest (suitable for trend visualisation).
    """
    s, owns = _session(session)
    try:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            s.query(HealthRecord)
            .filter(
                HealthRecord.user_id == user_id,
                HealthRecord.record_date >= since,
            )
            .order_by(HealthRecord.record_date.asc())
            .all()
        )
    finally:
        if owns:
            s.close()
