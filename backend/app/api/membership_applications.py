
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.member import Member
from app.models.membership_application import MembershipApplication
from app.schemas.membership_application import MembershipApplicationResponse
from app.services.member_service import find_existing_member

router = APIRouter(tags=["Membership Applications"])


async def save_application_photo(upload: UploadFile | None) -> str | None:
    if not upload:
        return None

    if upload.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Photo must be JPG, PNG, or WEBP.")

    content = await upload.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Photo must be 5 MB or smaller.")

    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"

    filename = f"{uuid4().hex}{suffix}"
    folder = Path(settings.upload_dir) / "member_photos"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / filename).write_bytes(content)

    return f"/uploads/member_photos/{filename}"


@router.post("/membership-applications")
async def submit_membership_application(
    membership_category: str = Form(...),
    academic_title: str | None = Form(None),
    full_name: str = Form(...),
    date_of_birth: date | None = Form(None),
    personal_email: str | None = Form(None),
    professional_email: str | None = Form(None),
    mobile: str | None = Form(None),
    whatsapp: str | None = Form(None),
    whatsapp_secondary: str | None = Form(None),
    highest_qualification: str | None = Form(None),
    designation: str | None = Form(None),
    department: str | None = Form(None),
    institution: str | None = Form(None),
    college_address: str | None = Form(None),
    pin_code: str | None = Form(None),
    state_province: str | None = Form(None),
    country: str | None = Form(None),
    google_scholar: str | None = Form(None),
    linkedin: str | None = Form(None),
    orcid: str | None = Form(None),
    expertise: str | None = Form(None),
    research_guideship: str | None = Form(None),
    member_id: str | None = Form(None),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    if not full_name.strip():
        raise HTTPException(status_code=400, detail="Full name is required.")
    if date_of_birth and date_of_birth > date.today():
        raise HTTPException(status_code=400, detail="Date of birth cannot be in the future.")

    existing_member = None
    if member_id:
        existing_member = db.get(Member, member_id.strip())
        if not existing_member:
            raise HTTPException(status_code=400, detail="Existing member ID was not found.")

    email = professional_email.strip().lower() if professional_email else None

    # If no explicit member ID was supplied, identify an existing member by
    # professional email or mobile. This preserves the same member_id during
    # approval instead of accidentally creating a duplicate member.
    if existing_member is None:
        existing_member = find_existing_member(
            db,
            member_id=None,
            professional_email=email,
            mobile=mobile,
        )
    if email:
        duplicate_application = db.execute(
            select(MembershipApplication).where(
                MembershipApplication.professional_email == email,
                MembershipApplication.approval_status.in_(["Pending", "Approved"]),
            )
        ).scalar_one_or_none()
        if duplicate_application:
            raise HTTPException(
                status_code=409,
                detail="An active application already exists for this professional email.",
            )

    photo_url = await save_application_photo(photo)

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    application = MembershipApplication(
        member_id=existing_member.member_id if existing_member else None,
        membership_category=membership_category.strip(),
        academic_title=academic_title,
        full_name=full_name.strip(),
        date_of_birth=date_of_birth,
        personal_email=personal_email.strip().lower() if personal_email else None,
        professional_email=email,
        mobile=mobile,
        whatsapp=whatsapp,
        whatsapp_secondary=whatsapp_secondary,
        photo_url=photo_url,
        highest_qualification=highest_qualification,
        designation=designation,
        department=department,
        institution=institution,
        college_address=college_address,
        pin_code=pin_code,
        state_province=state_province,
        country=country,
        google_scholar=google_scholar,
        linkedin=linkedin,
        orcid=orcid,
        expertise=expertise,
        research_guideship=research_guideship,
        approval_status="Pending",
        created_at=now,
        updated_at=now,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "success": True,
        "message": "Application submitted and is awaiting admin review.",
        "data": MembershipApplicationResponse.model_validate(application).model_dump(mode="json"),
    }


@router.get("/membership-applications/{application_id}")
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
):
    application = db.get(MembershipApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return {
        "success": True,
        "data": MembershipApplicationResponse.model_validate(application).model_dump(mode="json"),
    }
