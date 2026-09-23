# ICMTA Full-Stack Project

This folder combines the supplied ICMTA frontend and the FastAPI/MySQL backend into one working project.

## Structure

```text
ICMTA-FULLSTACK/
├── frontend/                 # Existing HTML/CSS/JS website
│   ├── pages/
│   ├── js/
│   ├── css/
│   └── assets/
├── backend/                  # FastAPI + SQLAlchemy + MySQL
│   ├── app/
│   ├── uploads/
│   ├── requirements.txt
│   └── .env.example
└── docs/
    └── INTEGRATION_AUDIT.md
```

## Run backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create `backend/.env` from `.env.example`, then:

```powershell
uvicorn app.main:app --reload --port 5000
```

Open:

- `http://localhost:5000/api/health`
- `http://localhost:5000/docs`

## Run frontend

Serve `frontend/` with VS Code Live Server (the existing project uses port 5500).

The frontend API base URL is:

```javascript
const API_BASE_URL = "http://localhost:5000";
```

## First end-to-end test

1. Start MySQL and confirm `icmt_faculty_directory` exists.
2. Start FastAPI on port 5000.
3. Open the frontend membership page.
4. Submit a test membership application.
5. In browser DevTools → Network, verify:
   `POST http://localhost:5000/api/membership-applications`
6. In MySQL Workbench:
   ```sql
   SELECT * FROM icmt_faculty_directory.membership_applications
   ORDER BY application_id DESC;
   ```

A submitted application remains `Pending` and does not create/activate a member until admin approval.
