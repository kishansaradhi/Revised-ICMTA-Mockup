
# ICMTA FastAPI + MySQL Backend

This backend is built around the supplied ICMTA MySQL schema. It does NOT create or alter database tables automatically.

## Existing MySQL schema expected

- members
- member_images
- membership_applications
- admin_users
- membership_payments
- events

The supplied database schema uses `ICMT001`, `ICMT002`, ... style member IDs. The backend therefore preserves existing IDs and generates the next ID using the existing prefix.

## 1. Create the Python environment

Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Configure environment

Copy:

```text
.env.example -> .env
```

and set the real MySQL password and a strong JWT secret.

Example:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/icmt_faculty_directory
```

Use the actual database name you have in MySQL. The supplied SQL files use `icmt_faculty_directory`; if your local Workbench schema is `icmtadb`, use `icmtadb`.

## 3. Start FastAPI

```powershell
uvicorn app.main:app --reload --port 5000
```

Open:

- http://127.0.0.1:5000/
- http://127.0.0.1:5000/api/health
- http://127.0.0.1:5000/docs

## 4. Important

Do NOT run `Base.metadata.create_all()` against the existing database. The backend is designed to use the existing schema.

## Main API endpoints

### Public
- GET `/api/members`
- GET `/api/members/{member_id}`
- POST `/api/membership-applications`
- GET `/api/membership-applications/{application_id}`
- POST `/api/payments`
- GET `/api/payments/{payment_id}`
- GET `/api/events`
- GET `/api/events/{event_id}`
- POST `/api/events`

### Admin
- POST `/api/admin/login`
- GET `/api/admin/me`
- GET `/api/admin/members`
- POST `/api/admin/members`
- PUT `/api/admin/members/{member_id}`
- GET `/api/admin/applications`
- POST `/api/admin/applications/{application_id}/approve`
- POST `/api/admin/applications/{application_id}/reject`
- GET `/api/admin/events`
- PUT `/api/admin/events/{event_id}/review`

## Current membership approval behavior

1. Applicant submits application.
2. Application is stored with `Pending`.
3. Existing member: existing `member_id` is retained.
4. New member: backend generates the next ID using the existing `ICMT###` format.
5. Admin approval runs the member merge and application approval in one transaction.
6. Existing member data is only filled where the member field is currently empty, matching the supplied approval workflow.
7. Member becomes Active after approval.

## Current payment behavior

The existing schema stores payment records and supports Pending/Paid/Failed/Refunded. The backend does not treat a payment record alone as membership approval.

Gateway/webhook integration can be added later.

## Frontend integration

The integrated frontend in `../frontend` uses port 5000 and includes the backend-backed membership submission and event data service. Payment UI remains manual/static until a payment submission form is added.
