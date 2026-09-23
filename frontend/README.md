# ICMTA — Indian Commerce and Management Teachers

Official website and centralized academic faculty directory for the **Indian Commerce and Management Teachers (ICMTA)** platform.

## Project Structure

```text
ICMTA_FACULTY_DIRECTORY/
├── index.html              # Main ICMTA Website Homepage
├── about-us.html           # About ICMTA, Vision, Mission & Leadership
├── initiatives.html        # Our Key Academic & Research Initiatives
├── events.html             # National Conferences, Seminars & Workshops
├── resources.html          # Academic Guidelines, Teaching Repositories & Tools
├── contact.html            # Secretariat Contact Information & Inquiry Form
├── faculty.html            # Public Faculty Information & Mentors Page
├── public-directory.html   # Public Faculty Directory (Search, Filter, Grid/Table & Modal)
├── member-profile.html     # Dedicated Standalone Public Member Profile (?id=ICMTAxxx)
├── admin.html              # Administrator Portal (Login, Dashboard, Member Management, Users, Logout)
├── README.md               # Documentation & Navigation Architecture
│
├── css/
│   └── style.css           # Central Stylesheet (Lato typography, ICMTA theme tokens & UI layout)
│
├── js/
│   ├── app.js              # Admin Management & Dashboard Logic
│   └── member-data.js      # Single Source of Truth (All 343 records + embedded portraits)
│
└── images/
    └── new/                # Clean Faculty Portrait Photos
```

## Navigation Flows

1. **Public Flow**:
   **Home** (`index.html`) &rarr; **Faculty** &rarr; **Faculty Information** (`faculty.html`) &rarr; **Faculty Directory** (`public-directory.html`) &rarr; **Member Profile** (`member-profile.html`)

2. **Admin Flow**:
   **Admin Login** &rarr; **Dashboard** &rarr; **Member Management** &rarr; **User Management** &rarr; **Logout** (`admin.html`)

## Key Features & Design System

- **Design Reference**: Inspired by the structure and branding of ICMTA (`https://sites.google.com/view/ICMTAmembers/home`), built as a 100% native frontend implementation.
- **Typography & Theme**: Google Font `Lato` (300, 400, 700) with deep teal (`#1e6c93`), dark navy (`#004d66`), and light accent (`#eaf5fb`).
- **Data Integrity**: Preserves all 343 verified member records and embedded portraits without modification.
- **Live Sync**: Edits made in the Admin Member Management workspace automatically sync to public directory pages in real time via reactive `localStorage`.
- **GitHub Pages Ready**: Structured with root relative links for immediate zero-config deployment.
