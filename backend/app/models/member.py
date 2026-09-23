
from datetime import date, datetime
from sqlalchemy import Boolean, Date, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Member(Base):
    __tablename__ = "members"

    member_id: Mapped[str] = mapped_column(String(20), primary_key=True)
    academic_title: Mapped[str | None] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    qualification: Mapped[str | None] = mapped_column(Text)
    designation: Mapped[str | None] = mapped_column(String(150))
    department: Mapped[str | None] = mapped_column(String(200))
    institution: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    state_province: Mapped[str | None] = mapped_column(String(100))
    pin_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str | None] = mapped_column(String(100))
    research_guideship: Mapped[str | None] = mapped_column(Text)
    expertise: Mapped[str | None] = mapped_column(Text)
    mobile: Mapped[str | None] = mapped_column(String(40))
    whatsapp: Mapped[str | None] = mapped_column(String(40))
    whatsapp_secondary: Mapped[str | None] = mapped_column(String(40))
    professional_email: Mapped[str | None] = mapped_column(String(255))
    personal_email: Mapped[str | None] = mapped_column(String(255))
    linkedin: Mapped[str | None] = mapped_column(Text)
    orcid: Mapped[str | None] = mapped_column(String(120))
    google_scholar: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(Text)
    membership_category: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source_record: Mapped[str | None] = mapped_column(Text)
    my_status: Mapped[str] = mapped_column(
        Enum("Active", "Inactive", "Pending", name="member_status"),
        nullable=False,
        default="Active",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
