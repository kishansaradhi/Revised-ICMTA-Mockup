
from datetime import date, datetime, time
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):
    event_title: str
    event_category: str | None = None
    event_date: date
    registration_deadline: datetime | None = None
    start_time: time | None = None
    end_time: time | None = None
    event_mode: str | None = None
    poster_url: str | None = None
    speaker_name: str | None = None
    speaker_designation: str | None = None
    speaker_institution: str | None = None
    short_description: str | None = None
    full_description: str | None = None
    organized_by: str | None = None
    registration_fee: Decimal | None = 0
    in_association_with: str | None = None
    registration_link: str | None = None
    coordinator_name: str | None = None
    contact_number: str | None = None
    contact_email: str | None = None


class EventResponse(EventCreate):
    model_config = ConfigDict(from_attributes=True)

    event_id: int
    status: str
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None
    rejection_reason: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
