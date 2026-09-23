
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_id: str
    academic_title: str | None = None
    name: str
    date_of_birth: date | None = None
    qualification: str | None = None
    designation: str | None = None
    department: str | None = None
    institution: str | None = None
    address: str | None = None
    city: str | None = None
    state_province: str | None = None
    pin_code: str | None = None
    country: str | None = None
    research_guideship: str | None = None
    expertise: str | None = None
    mobile: str | None = None
    whatsapp: str | None = None
    whatsapp_secondary: str | None = None
    professional_email: str | None = None
    personal_email: str | None = None
    linkedin: str | None = None
    orcid: str | None = None
    google_scholar: str | None = None
    photo_url: str | None = None
    membership_category: str | None = None
    is_active: bool
    source_record: str | None = None
    my_status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
