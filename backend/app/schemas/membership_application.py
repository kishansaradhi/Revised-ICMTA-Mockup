
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class MembershipApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: int
    member_id: str | None = None
    membership_category: str
    academic_title: str | None = None
    full_name: str
    date_of_birth: date | None = None
    personal_email: str | None = None
    professional_email: str | None = None
    mobile: str | None = None
    whatsapp: str | None = None
    whatsapp_secondary: str | None = None
    photo_url: str | None = None
    highest_qualification: str | None = None
    designation: str | None = None
    department: str | None = None
    institution: str | None = None
    college_address: str | None = None
    pin_code: str | None = None
    state_province: str | None = None
    country: str | None = None
    google_scholar: str | None = None
    linkedin: str | None = None
    orcid: str | None = None
    expertise: str | None = None
    research_guideship: str | None = None
    approval_status: str
    admin_notes: str | None = None
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
