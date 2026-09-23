
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership_application import MembershipApplication
from app.models.membership_payment import MembershipPayment


def validate_payment_reference(
    db: Session,
    transaction_id: str | None,
    application_id: int | None,
):
    if transaction_id:
        existing = db.execute(
            select(MembershipPayment).where(
                MembershipPayment.transaction_id == transaction_id
            )
        ).scalar_one_or_none()
        if existing:
            raise ValueError("Transaction already exists.")

    if application_id:
        application = db.get(MembershipApplication, application_id)
        if not application:
            raise ValueError("Application does not exist.")
