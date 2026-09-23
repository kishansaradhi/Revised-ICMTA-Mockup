
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event


def get_public_events(db: Session):
    return db.execute(
        select(Event)
        .where(Event.status == "Approved")
        .order_by(Event.event_date.asc(), Event.start_time.asc())
    ).scalars().all()


def approve_event(db: Session, event: Event, admin_id: int):
    if event.status != "Pending":
        raise ValueError("Only pending events can be approved.")
    event.status = "Approved"
    event.reviewed_by = admin_id
    event.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    event.rejection_reason = None


def reject_event(db: Session, event: Event, admin_id: int, reason: str | None):
    if event.status != "Pending":
        raise ValueError("Only pending events can be rejected.")
    event.status = "Rejected"
    event.reviewed_by = admin_id
    event.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    event.rejection_reason = reason
