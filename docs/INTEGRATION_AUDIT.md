# ICMTA Frontend ↔ FastAPI Integration Audit

Reviewed against the supplied frontend ZIP and FastAPI backend ZIP.

## Confirmed working alignment

### Members directory
- Frontend `js/api.js` uses `http://localhost:5000`.
- Backend exposes `GET /api/members`.
- Frontend expects `{ success, data }`, which matches the backend.
- Member field mapping was corrected for:
  - `research_guideship`
  - `address`
  - `professional_email`
  - `personal_email`
  - `photo_url`
- Relative upload URLs are converted to absolute backend URLs.

### Membership application
- `pages/membership.html` originally used a demo-only success handler.
- It now calls `js/membership-submit.js`.
- The adapter sends `multipart/form-data` to:
  `POST /api/membership-applications`
- The adapter's field names match the backend application model, including:
  `college_address` (not `address`).
- Photo upload is sent as `photo`.
- Success is shown only after a successful backend response.
- The submit button is re-enabled in `finally`.
- The backend now attempts existing-member detection by professional email/mobile when no member ID is supplied.

### Admin authentication
- Frontend and backend use the same `ICMTAdminToken` localStorage key.
- Backend uses JWT with the configured `.env` secret.
- Admin requests send `Authorization: Bearer <token>`.

### Membership approval
- Backend approval retains an existing `member_id`.
- New applications receive a server-generated `ICMT###` ID on approval.
- Approval is committed explicitly after the approval service runs.
- The response reports whether the application started with an existing member ID.

## Remaining integration limitations

### Events
The frontend event form contains `endDate` and an event-poster file upload. The supplied backend `Event` model currently has `event_date` and `poster_url`, but no `end_date` column and no multipart event-poster upload endpoint.

The integrated event service therefore:
- sends event data to `POST /api/events`;
- normalizes backend status/data for the existing frontend;
- currently treats `event_date` as the event end date when no backend `end_date` exists;
- does not upload the poster file.

If multi-day events and event poster storage are required, the MySQL `events` schema and FastAPI event endpoint should be extended together rather than silently dropping those fields.

### Payments
`pages/payment.html` is currently informational/static. The backend has `POST /api/payments`, but there is no matching payment submission form in the supplied frontend. Manual QR/bank payment proof workflow is therefore not end-to-end integrated yet.

### Member accounts
The supplied database/backend does not contain a member-user/account table. Admin JWT authentication is implemented, but member login/profile account activation is not.

## Recommended test order

1. `GET /api/health`
2. `GET /api/members`
3. Frontend directory → `/api/members`
4. Membership form → `/api/membership-applications`
5. Verify `membership_applications` in MySQL
6. Admin login
7. Admin application list
8. Approve application
9. Verify new/existing member behavior in `members`
10. Event flow
11. Payment flow
