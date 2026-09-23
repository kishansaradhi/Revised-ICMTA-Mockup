
from datetime import date, datetime, time
from decimal import Decimal
from sqlalchemy import BigInteger, Date, DateTime, Numeric, String, Text, Time, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_title: Mapped[str] = mapped_column(String(255), nullable=False)
    event_category: Mapped[str | None] = mapped_column(String(100))
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    registration_deadline: Mapped[datetime | None] = mapped_column(DateTime)
    start_time: Mapped[time | None] = mapped_column(Time)
    end_time: Mapped[time | None] = mapped_column(Time)
    event_mode: Mapped[str | None] = mapped_column(String(50))
    poster_url: Mapped[str | None] = mapped_column(Text)
    speaker_name: Mapped[str | None] = mapped_column(String(200))
    speaker_designation: Mapped[str | None] = mapped_column(String(150))
    speaker_institution: Mapped[str | None] = mapped_column(String(255))
    short_description: Mapped[str | None] = mapped_column(String(500))
    full_description: Mapped[str | None] = mapped_column(Text)
    organized_by: Mapped[str | None] = mapped_column(String(255))
    registration_fee: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), default=0)
    in_association_with: Mapped[str | None] = mapped_column(String(255))
    registration_link: Mapped[str | None] = mapped_column(Text)
    coordinator_name: Mapped[str | None] = mapped_column(String(200))
    contact_number: Mapped[str | None] = mapped_column(String(40))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Pending")
    reviewed_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("admin_users.admin_id", onupdate="CASCADE", ondelete="SET NULL"),
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
