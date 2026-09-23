ICMTA Faculty Directory — Professional Automation Prototype

Files:
- index.html        = UI / HTML structure and application shell
- css/style.css     = Responsive CSS styling
- js/member-data.js = Master data block with all 343 member records
- js/app.js         = Core application logic & photo auto-matching engine
- sync_photos.js    = Auto-sync CLI tool to scan images/ and link photos automatically

-------------------------------------------------------------
AUTOMATIC PHOTO LINKING & BULK UPLOAD:
-------------------------------------------------------------

Method 1: From the Web UI (No coding required)
1. Open index.html in your browser and log in as Administrator.
2. Go to "Member Management".
3. Click "Auto-Link / Upload Photos".
4. Select or drag & drop any number of photo files.
5. The system automatically detects and matches each photo to its member
   by Member ID (e.g. ICMTA107.jpg) or Faculty Name (e.g. Dr_Shilpa_Tandon.png).
6. Click "Apply Photos" — all records are instantly updated across the
   Dashboard, Directory, Profiles, and Management.
7. Click "Download Updated member-data.js" to save the changes permanently.

Method 2: Automatic Background Sync via Terminal
1. Drop new photo files into images/new/ or images/existing/.
2. File naming conventions supported:
   - Member ID: ICMTA107.jpg, ICMTA001.png, 045_name.png
   - Faculty Name: Shilpa_Tandon.png, Dr_Ankit_Katiyar.jpg
3. Run in your terminal:
   node sync_photos.js
4. All matching photos are automatically linked in js/member-data.js
   and the data version in js/app.js is refreshed automatically.
