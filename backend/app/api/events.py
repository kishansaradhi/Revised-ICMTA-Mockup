
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin_user import AdminUser
from app.models.event import Event
from app.schemas.event import EventCreate, EventResponse

router = APIRouter(tags=["Events"])


@router.get("/events")
def public_events(db: Session = Depends(get_db)):
    events = db.execute(
        select(Event)
        .where(Event.status == "Approved")
        .order_by(Event.event_date.asc(), Event.start_time.asc())
    ).scalars().all()

    return {
        "success": True,
        "data": [EventResponse.model_validate(e).model_dump(mode="json") for e in events],
    }


@router.get("/events/{event_id}")
def public_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event or event.status != "Approved":
        raise HTTPException(status_code=404, detail="Event not found")

    return {
        "success": True,
        "data": EventResponse.model_validate(event).model_dump(mode="json"),
    }


@router.post("/events")
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
):
    if payload.registration_deadline:
        event_day_end = datetime.combine(
            payload.event_date,
            datetime.max.time()
        )
        if payload.registration_deadline > event_day_end:
            raise HTTPException(
                status_code=400,
                detail="Registration deadline cannot be after the event date.",
            )

    if payload.start_time and payload.end_time and payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time.")

    if payload.registration_fee is not None and payload.registration_fee < 0:
        raise HTTPException(status_code=400, detail="Registration fee cannot be negative.")

    event = Event(
        **payload.model_dump(),
        status="Pending",
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "success": True,
        "message": "Event submitted for admin approval.",
        "data": EventResponse.model_validate(event).model_dump(mode="json"),
    }
