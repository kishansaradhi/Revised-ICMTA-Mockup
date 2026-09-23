
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.membership_payment import MembershipPayment
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import validate_payment_reference

router = APIRouter(tags=["Payments"])


@router.post("/payments")
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than zero.")

    if payload.currency.upper() != "INR":
        raise HTTPException(status_code=400, detail="Current payment flow supports INR.")

    if payload.payment_status not in {"Pending", "Paid", "Failed", "Refunded"}:
        raise HTTPException(status_code=400, detail="Invalid payment status.")

    if payload.payment_status == "Paid" and payload.paid_at is None:
        raise HTTPException(status_code=400, detail="paid_at is required for Paid payments.")

    try:
        validate_payment_reference(
            db,
            payload.transaction_id,
            payload.application_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    payment = MembershipPayment(
        application_id=payload.application_id,
        member_id=payload.member_id,
        membership_category=payload.membership_category,
        amount=payload.amount,
        currency=payload.currency.upper(),
        payment_method=payload.payment_method,
        payment_gateway=payload.payment_gateway,
        transaction_id=payload.transaction_id,
        payment_status=payload.payment_status,
        paid_at=payload.paid_at,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "success": True,
        "data": PaymentResponse.model_validate(payment).model_dump(mode="json"),
    }


@router.get("/payments/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(MembershipPayment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return {
        "success": True,
        "data": PaymentResponse.model_validate(payment).model_dump(mode="json"),
    }
