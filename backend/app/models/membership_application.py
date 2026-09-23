
from datetime import date, datetime
from sqlalchemy import BigInteger, Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MembershipApplication(Base):
    __tablename__ = "membership_applications"

    application_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    member_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    membership_category: Mapped[str] = mapped_column(String(100), nullable=False)
    academic_title: Mapped[str | None] = mapped_column(String(30))
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    personal_email: Mapped[str | None] = mapped_column(String(255))
    professional_email: Mapped[str | None] = mapped_column(String(255))
    mobile: Mapped[str | None] = mapped_column(String(40))
    whatsapp: Mapped[str | None] = mapped_column(String(40))
    whatsapp_secondary: Mapped[str | None] = mapped_column(String(40))
    photo_url: Mapped[str | None] = mapped_column(Text)
    highest_qualification: Mapped[str | None] = mapped_column(Text)
    designation: Mapped[str | None] = mapped_column(String(150))
    department: Mapped[str | None] = mapped_column(String(200))
    institution: Mapped[str | None] = mapped_column(Text)
    college_address: Mapped[str | None] = mapped_column(Text)
    pin_code: Mapped[str | None] = mapped_column(String(20))
    state_province: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))
    google_scholar: Mapped[str | None] = mapped_column(Text)
    linkedin: Mapped[str | None] = mapped_column(Text)
    orcid: Mapped[str | None] = mapped_column(String(120))
    expertise: Mapped[str | None] = mapped_column(Text)
    research_guideship: Mapped[str | None] = mapped_column(Text)
    approval_status: Mapped[str] = mapped_column(
        Enum("Pending", "Approved", "Rejected", name="application_status"),
        nullable=False,
        default="Pending",
    )
    admin_notes: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.admin_id", onupdate="CASCADE", ondelete="SET NULL"),
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
