
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.member import Member
from app.schemas.member import MemberResponse

router = APIRouter(tags=["Members"])


@router.get("/members", response_model=dict)
def list_members(
    q: str | None = Query(default=None),
    state: str | None = Query(default=None),
    department: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Member).where(
        Member.is_active.is_(True),
        Member.my_status == "Active",
    )

    if q:
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Member.name.ilike(term),
                Member.member_id.ilike(term),
                Member.institution.ilike(term),
                Member.designation.ilike(term),
                Member.expertise.ilike(term),
            )
        )

    if state:
        stmt = stmt.where(Member.state_province == state)

    if department:
        stmt = stmt.where(Member.department == department)

    members = db.execute(
        stmt.order_by(Member.member_id.asc())
    ).scalars().all()

    return {
        "success": True,
        "data": [MemberResponse.model_validate(m).model_dump(mode="json") for m in members],
        "count": len(members),
    }


@router.get("/members/{member_id}", response_model=dict)
def get_member(member_id: str, db: Session = Depends(get_db)):
    member = db.get(Member, member_id)
    if not member or not member.is_active or member.my_status != "Active":
        raise HTTPException(status_code=404, detail="Member not found")

    return {
        "success": True,
        "data": MemberResponse.model_validate(member).model_dump(mode="json"),
    }
