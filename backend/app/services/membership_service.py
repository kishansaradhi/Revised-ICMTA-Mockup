
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member import Member
from app.models.membership_application import MembershipApplication
from app.services.member_service import next_member_id


def _set_if_missing(member, column, value):
    if value is None:
        return
    current = getattr(member, column)
    if current is None or (isinstance(current, str) and not current.strip()):
        setattr(member, column, value)


def approve_application(
    db: Session,
    application: MembershipApplication,
    admin_id: int,
):
    if application.approval_status != "Pending":
        raise ValueError("Only pending applications can be approved.")

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Existing member: retain the exact existing member_id.
    if application.member_id:
        member = db.get(Member, application.member_id)
        if not member:
            raise ValueError(
                f"Application references member {application.member_id}, "
                "but that member does not exist."
            )
        created_new = False
    else:
        # New member: allocate a new ID inside the same DB transaction.
        new_id = next_member_id(db)
        member = Member(
            member_id=new_id,
            name=application.full_name.strip(),
            is_active=True,
            my_status="Active",
            created_at=now,
            updated_at=now,
        )
        db.add(member)
        db.flush()
        application.member_id = new_id
        created_new = True

    mapping = {
        "academic_title": "academic_title",
        "date_of_birth": "date_of_birth",
        "qualification": "highest_qualification",
        "designation": "designation",
        "department": "department",
        "institution": "institution",
        "address": "college_address",
        "pin_code": "pin_code",
        "state_province": "state_province",
        "country": "country",
        "research_guideship": "research_guideship",
        "expertise": "expertise",
        "mobile": "mobile",
        "whatsapp": "whatsapp",
        "whatsapp_secondary": "whatsapp_secondary",
        "professional_email": "professional_email",
        "personal_email": "personal_email",
        "linkedin": "linkedin",
        "orcid": "orcid",
        "google_scholar": "google_scholar",
        "photo_url": "photo_url",
        "membership_category": "membership_category",
    }

    # Preserve the existing workflow from 04_approval_workflow.sql:
    # fill missing member fields rather than blindly overwriting them.
    for member_column, application_column in mapping.items():
        _set_if_missing(
            member,
            member_column,
            getattr(application, application_column),
        )

    # Keep the application name as the member name when it is a new member.
    if created_new:
        member.name = application.full_name.strip()

    member.is_active = True
    member.my_status = "Active"
    member.updated_at = now

    application.approval_status = "Approved"
    application.reviewed_by = admin_id
    application.reviewed_at = now
    db.flush()

    return member
