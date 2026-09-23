
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_admin,
    verify_password,
)
from app.models.admin_user import AdminUser
from app.models.member import Member
from app.models.membership_application import MembershipApplication
from app.models.event import Event
from app.schemas.auth import AdminLoginRequest
from app.schemas.member import MemberResponse
from app.services.member_service import next_member_id, normalize_email
from app.services.membership_service import approve_application
from app.services.event_service import approve_event, reject_event

router = APIRouter(tags=["Admin"])


@router.post("/admin/login")
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = db.execute(
        select(AdminUser).where(
            AdminUser.user_id == payload.user_id.strip()
        )
    ).scalar_one_or_none()

    if not admin or not admin.is_active or not verify_password(
        payload.password,
        admin.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(admin.admin_id, admin.user_id)

    return {
        "success": True,
        "token": token,
        "data": {
            "admin_id": admin.admin_id,
            "user_id": admin.user_id,
        },
    }


@router.get("/admin/me")
def admin_me(admin: AdminUser = Depends(get_current_admin)):
    return {
        "success": True,
        "data": {
            "admin_id": admin.admin_id,
            "user_id": admin.user_id,
            "is_active": admin.is_active,
        },
    }


@router.get("/admin/members")
def admin_members(
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    members = db.execute(
        select(Member).order_by(Member.member_id.asc())
    ).scalars().all()

    return {
        "success": True,
        "data": [MemberResponse.model_validate(m).model_dump(mode="json") for m in members],
        "count": len(members),
    }


async def _save_upload(
    upload: UploadFile,
    subdir: str,
    allowed=("image/jpeg", "image/png", "image/webp"),
) -> str:
    if upload.content_type not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, and WEBP images are allowed.",
        )

    content = await upload.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Image size must be 5 MB or smaller.",
        )

    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"

    filename = f"{uuid4().hex}{suffix}"
    folder = Path(settings.upload_dir) / subdir
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    path.write_bytes(content)

    return f"/uploads/{subdir}/{filename}"


@router.post("/admin/members")
async def create_member(
    name: str = Form(...),
    qualification: str | None = Form(None),
    designation: str | None = Form(None),
    department: str | None = Form(None),
    institution: str | None = Form(None),
    city: str | None = Form(None),
    state_province: str | None = Form(None),
    country: str | None = Form(None),
    expertise: str | None = Form(None),
    mobile: str | None = Form(None),
    professional_email: str | None = Form(None),
    personal_email: str | None = Form(None),
    research_guideship: str | None = Form(None),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required.")

    if professional_email:
        email = normalize_email(professional_email)
        duplicate = db.execute(
            select(Member).where(Member.professional_email == email)
        ).scalar_one_or_none()
        if duplicate:
            raise HTTPException(status_code=409, detail="Professional email already exists.")

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    member_id = next_member_id(db)

    photo_url = None
    if photo:
        photo_url = await _save_upload(photo, "member_photos")

    member = Member(
        member_id=member_id,
        name=name,
        qualification=qualification,
        designation=designation,
        department=department,
        institution=institution,
        city=city,
        state_province=state_province,
        country=country,
        expertise=expertise,
        mobile=mobile,
        professional_email=normalize_email(professional_email),
        personal_email=normalize_email(personal_email),
        research_guideship=research_guideship,
        photo_url=photo_url,
        is_active=True,
        my_status="Active",
        created_at=now,
        updated_at=now,
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return {
        "success": True,
        "data": MemberResponse.model_validate(member).model_dump(mode="json"),
    }


@router.put("/admin/members/{member_id}")
async def update_member(
    member_id: str,
    name: str | None = Form(None),
    qualification: str | None = Form(None),
    designation: str | None = Form(None),
    department: str | None = Form(None),
    institution: str | None = Form(None),
    city: str | None = Form(None),
    state_province: str | None = Form(None),
    country: str | None = Form(None),
    expertise: str | None = Form(None),
    mobile: str | None = Form(None),
    professional_email: str | None = Form(None),
    personal_email: str | None = Form(None),
    research_guideship: str | None = Form(None),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if professional_email:
        email = normalize_email(professional_email)
        duplicate = db.execute(
            select(Member).where(
                Member.professional_email == email,
                Member.member_id != member_id,
            )
        ).scalar_one_or_none()
        if duplicate:
            raise HTTPException(status_code=409, detail="Professional email already exists.")
        member.professional_email = email

    for field, value in {
        "name": name,
        "qualification": qualification,
        "designation": designation,
        "department": department,
        "institution": institution,
        "city": city,
        "state_province": state_province,
        "country": country,
        "expertise": expertise,
        "mobile": mobile,
        "personal_email": normalize_email(personal_email),
        "research_guideship": research_guideship,
    }.items():
        if value is not None:
            setattr(member, field, value.strip() if isinstance(value, str) else value)

    if photo:
        member.photo_url = await _save_upload(photo, "member_photos")

    member.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(member)

    return {
        "success": True,
        "data": MemberResponse.model_validate(member).model_dump(mode="json"),
    }


@router.get("/admin/applications")
def admin_applications(
    status: str | None = None,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    stmt = select(MembershipApplication).order_by(
        MembershipApplication.created_at.asc()
    )
    if status:
        stmt = stmt.where(MembershipApplication.approval_status == status)

    rows = db.execute(stmt).scalars().all()

    return {
        "success": True,
        "data": [
            {
                "application_id": r.application_id,
                "member_id": r.member_id,
                "membership_category": r.membership_category,
                "full_name": r.full_name,
                "professional_email": r.professional_email,
                "mobile": r.mobile,
                "approval_status": r.approval_status,
                "created_at": r.created_at,
                "reviewed_at": r.reviewed_at,
                "admin_notes": r.admin_notes,
            }
            for r in rows
        ],
        "count": len(rows),
    }


@router.post("/admin/applications/{application_id}/approve")
def approve_membership_application(
    application_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    application = db.get(MembershipApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    created_new_member = application.member_id is None

    try:
        member = approve_application(db, application, admin.admin_id)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        db.rollback()
        raise

    return {
        "success": True,
        "message": "Application approved.",
        "data": {
            "application_id": application.application_id,
            "member_id": member.member_id,
            "created_new_member": created_new_member,
            "status": application.approval_status,
        },
    }


@router.post("/admin/applications/{application_id}/reject")
def reject_membership_application(
    application_id: int,
    reason: str | None = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    application = db.get(MembershipApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if application.approval_status != "Pending":
        raise HTTPException(status_code=400, detail="Only pending applications can be rejected.")

    application.approval_status = "Rejected"
    application.reviewed_by = admin.admin_id
    application.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    application.admin_notes = reason
    db.commit()

    return {
        "success": True,
        "message": "Application rejected.",
        "data": {
            "application_id": application.application_id,
            "status": application.approval_status,
        },
    }


@router.get("/admin/events")
def admin_events(
    status: str | None = None,
    db: Session = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    stmt = select(Event).order_by(Event.created_at.desc())
    if status:
        # Accept both the database spelling and the old frontend spelling.
        db_status = {
            "PENDING_APPROVAL": "Pending",
            "APPROVED": "Approved",
            "REJECTED": "Rejected",
        }.get(status, status)
        stmt = stmt.where(Event.status == db_status)

    events = db.execute(stmt).scalars().all()
    return {"success": True, "data": events, "count": len(events)}


@router.put("/admin/events/{event_id}/review")
def review_event(
    event_id: int,
    status: str,
    rejection_reason: str | None = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    normalized = status.upper()
    try:
        with db.begin():
            if normalized == "APPROVED":
                approve_event(db, event, admin.admin_id)
            elif normalized == "REJECTED":
                reject_event(db, event, admin.admin_id, rejection_reason)
            else:
                raise ValueError("Status must be APPROVED or REJECTED.")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"success": True, "data": {"event_id": event_id, "status": event.status}}
