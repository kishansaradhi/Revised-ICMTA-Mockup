
from datetime import datetime
from decimal import Decimal
from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MembershipPayment(Base):
    __tablename__ = "membership_payments"

    payment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    application_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "membership_applications.application_id",
            onupdate="CASCADE",
            ondelete="SET NULL",
        ),
    )
    member_id: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("members.member_id", onupdate="CASCADE", ondelete="SET NULL"),
    )
    membership_category: Mapped[str | None] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    payment_method: Mapped[str | None] = mapped_column(String(50))
    payment_gateway: Mapped[str | None] = mapped_column(String(100))
    transaction_id: Mapped[str | None] = mapped_column(String(150), unique=True)
    payment_status: Mapped[str] = mapped_column(
        Enum("Pending", "Paid", "Failed", "Refunded", name="payment_status"),
        nullable=False,
        default="Pending",
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
