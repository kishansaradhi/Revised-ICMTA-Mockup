
from datetime import datetime
from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MemberImage(Base):
    __tablename__ = "member_images"

    image_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    member_id: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("members.member_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    image_type: Mapped[str | None] = mapped_column(String(50))
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
