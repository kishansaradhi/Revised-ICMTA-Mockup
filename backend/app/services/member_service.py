
import re
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models.member import Member


def next_member_id(db: Session) -> str:
    """
    Preserve the existing ICMT### format used by the supplied member CSV.
    GET_LOCK prevents two simultaneous approvals from choosing the same ID.
    """
    lock_name = "icmt_member_id_generation"
    acquired = db.execute(text("SELECT GET_LOCK(:name, 10)"), {"name": lock_name}).scalar()
    if acquired != 1:
        raise RuntimeError("Could not acquire member ID generation lock")

    try:
        rows = db.execute(
            select(Member.member_id).where(Member.member_id.is_not(None))
        ).scalars().all()

        max_number = 0
        prefix = "ICMT"
        for value in rows:
            match = re.fullmatch(r"([A-Za-z]+)(\d+)", value or "")
            if match:
                n = int(match.group(2))
                if n > max_number:
                    max_number = n
                    prefix = match.group(1).upper()

        return f"{prefix}{max_number + 1:03d}"
    finally:
        db.execute(text("SELECT RELEASE_LOCK(:name)"), {"name": lock_name})


def normalize_email(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lower()


def find_existing_member(
    db: Session,
    member_id: str | None,
    professional_email: str | None,
    mobile: str | None,
):
    if member_id:
        member = db.get(Member, member_id.strip())
        if member:
            return member

    email = normalize_email(professional_email)
    if email:
        member = db.execute(
            select(Member).where(
                func.lower(Member.professional_email) == email
            )
        ).scalar_one_or_none()
        if member:
            return member

    if mobile:
        member = db.execute(
            select(Member).where(Member.mobile == mobile.strip())
        ).scalar_one_or_none()
        if member:
            return member

    return None
