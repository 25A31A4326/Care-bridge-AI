# CareBridge AI

> **"Your Medicine, Your Language, Your Care"**  
> *మీ మందులు, మీ భాష, మీ ఆరోగ్యం*

CareBridge AI is a bilingual (Telugu & English) healthcare conversational application purpose-built for elderly patients, users with limited digital literacy, and authorized family caregivers. It translates complex prescription handwriting, discharge summaries, and medical instructions into simple, compassionate language with voice-first assistance, deterministic source verification, medication scheduling, and printable A4 fridge sheets.

---

## 🌟 Key Features

1. **ChatGPT/Claude-Style Conversational Interface**:
   - Single unified conversational canvas.
   - Welcoming bilingual greeting in Telugu and English.
   - Persistent bottom composer with:
     - **Plus (+)** button with 5 upload options (Prescription photo, Medicine package photo, Discharge summary, Medical report, PDF).
     - Text input with instant suggestion pills.
     - **Microphone** button with Web Speech recognition (`te-IN` and `en-US`), listening indicator, and transcription review.
     - **Send** button.

2. **Bilingual Telugu & English Experience**:
   - First-visit language selector persisted in `localStorage` and SQLite user preference.
   - High-fidelity medical translations preserving exact drug names, doses, and dates.
   - Web Speech Synthesis reading explanations aloud in natural cadence.

3. **Source-Grounded Prescription Explanation**:
   - Prominent **"Simple Explanation"** (*సులభమైన వివరణ*).
   - Expandable **"What the document says"** (*డాక్యుమెంట్లో ఏమి రాశారు*) comparing OCR/PDF text directly against structured instructions.
   - Flesch Reading Ease score (validated strictly for English).

4. **Clinical Safety Gates**:
   - **Blurry / Ambiguous Handwriting**: Flagged as `Needs verification`; automatic reminder scheduling is blocked until confirmed with doctor.
   - **Conflicting Orders**: Flagged as `Conflicting Instructions` (e.g. 5-day vs 3-day antibiotic duration).
   - **Medicine Package Safety**: Package boxes confirm product identity only, not prescribed doses.
   - **Missed-Dose Safety**: Enforces warning against taking double doses.

5. **Medicine Management & Reminders**:
   - Daily checklist with *Mark as Taken*, *Remind Later (Snooze)*, and *Missed*.
   - 7-day calendar history and upcoming doses.
   - In-app Web Audio chime alarm and browser Notification API integration.

6. **Family Caregiver Portal**:
   - Patient authorizes up to 2 trusted caregivers.
   - Role-Based Access Control (RBAC) enforced on backend (rejects unauthorized caregivers with 403).
   - Monitors adherence, verified schedules, and follow-up appointments.

7. **Printable Fridge Sheet PDF**:
   - One-page A4 patient instruction sheet generated dynamically via ReportLab.
   - Direct download and browser print preview.

---

## 🏗️ Project Architecture

```
carebridge-ai/
├── backend/
│   ├── app.py                      # Flask REST API entry point & static SPA server
│   ├── config.py                   # App configuration & environment variables
│   ├── database/
│   │   ├── db.py                   # SQLite connection context & foreign key enforcement
│   │   ├── schema.sql              # Relational schema (12 tables)
│   │   └── seed_data.py            # Fictional synthetic patient records & documents
│   ├── routes/
│   │   ├── auth_routes.py          # Auth & synthetic demo user switching
│   │   ├── chat_routes.py          # Conversation history & grounded query engine
│   │   ├── document_routes.py      # Secure file upload, OCR, & text comparison
│   │   ├── medicine_routes.py      # Schedules, checklist, & 7-day calendar
│   │   ├── caregiver_routes.py     # Caregiver authorization (max 2) & RBAC portal
│   │   └── careplan_routes.py      # Discharge care plan & A4 Fridge Sheet PDF
│   └── services/
│       ├── ai_service.py           # Grounded assistant (local demo + Gemini/OpenAI API)
│       ├── ocr_service.py          # Native PDF & OCR engine with quality assessment
│       ├── prescription_service.py # Structured instruction parser & bilingual generator
│       ├── readability_service.py  # Flesch Reading Ease & deterministic validation
│       └── pdf_service.py          # ReportLab A4 printable fridge sheet builder
├── frontend/
│   ├── index.html                  # HTML entry point with Noto Sans Telugu & Inter fonts
│   ├── package.json                # React 18, Vite 5, Tailwind CSS, Lucide React
│   ├── vite.config.js              # Vite server & API proxy
│   ├── tailwind.config.js          # Healthcare color palette & responsive typography
│   └── src/
│       ├── App.jsx                 # Root coordinator & persistent language handling
│       ├── index.css               # Tailwind directives & @media print styles
│       ├── translations/
│       │   ├── en.json             # English language dictionary
│       │   └── te.json             # Telugu language dictionary
│       ├── services/
│       │   ├── api.js              # REST client for all backend endpoints
│       │   ├── speech.js           # Web Speech Recognition & Synthesis service
│       │   └── notifications.js    # Web Audio chime & browser notifications
│       └── components/
│           ├── Common/             # Navbar, FirstVisitLanguageModal
│           ├── Chat/               # ChatInterface, MessageBubble, PlusMenu, VoiceInputModal
│           ├── Prescription/       # PrescriptionExplanation, SourceComparison
│           ├── Medicine/           # MedicineManagement, Checklist, Calendar
│           ├── Caregiver/          # CaregiverPortal, Authorization Form
│           ├── CarePlan/           # CarePlanView, Printable Fridge Sheet
│           └── Documents/          # DocumentManager, Secure File Delivery
├── uploads/                        # Non-public directory for uploaded medical files
├── tests/
│   └── test_backend.py             # 10 comprehensive unittest test cases
├── evaluate.py                     # Deterministic clinical & system evaluation script
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md
```

---

## 🚀 Installation & Running Instructions

### Prerequisites
- Python 3.10+ (Installed on system)
- Node.js v18+ & npm (Installed or portable)

### 1. Backend Setup & Run (Windows PowerShell)

```powershell
# Open Windows PowerShell in project root directory
cd "c:\Users\SRI SATYA SAI\OneDrive\Desktop\care bridge ai"

# Install Python requirements
python -m pip install -r requirements.txt

# Start the CareBridge AI Full-Stack Server
python -m backend.app
```

The application will start on: **`http://127.0.0.1:5000`**  
*(Flask automatically serves the built React frontend application, database, and REST APIs together).*

### 2. Frontend Development Server (Optional for Hot-Reload Development)

If you wish to make live UI changes with Vite hot module replacement:

```powershell
cd "c:\Users\SRI SATYA SAI\OneDrive\Desktop\care bridge ai\frontend"
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 🧪 Testing & Verification

Run the automated backend test suite:
```powershell
python -m unittest tests/test_backend.py
```
*Expected: 10/10 tests pass (OK)*

Run the deterministic clinical & technical benchmark evaluation:
```powershell
python evaluate.py
```

### Benchmark Results:
```text
=================================================================
CAREBRIDGE AI — SYSTEM & CLINICAL EVALUATION SUITE
=================================================================
[PASS] 1. Backend Health Check & Engine Verification    | Status: 200
[PASS] 2. Grounded Chat Assistant (English)             | Answer contains verified meds: True
[PASS] 3. Grounded Chat Assistant (Telugu)              | Telugu response generated: True
[PASS] 4. Blurry Handwriting Safety Flagging            | Quality: blurry, Status: needs_verification
[PASS] 5. Conflicting Medical Orders Flagging           | Detected Conflict: True
[PASS] 6. Unverified Automatic Reminder Prevention      | Blocked Unverified: True
[PASS] 7. Missed Dose Double-Up Warning                 | Contains safety warning: True
[PASS] 8. Caregiver RBAC & Max-2 Enforced               | Active count: 1, 403 on unauth: True
[PASS] 9. Printable A4 Fridge Sheet PDF Generation      | PDF bytes: 4280
[PASS] 10. English Readability Score Evaluation         | Score: 56.7 / 100 (Fairly Complex)
-----------------------------------------------------------------
ALL 10 EVALUATION BENCHMARKS PASSED SUCCESSFULLY (100% PASS RATE)
```

---

## 👥 Pre-Configured Synthetic Demo Profiles

Switch between pre-configured patient profiles anytime using the top-bar dropdown:

1. **Smt. Lakshmi Devi (Age 68)**:
   - *Scenario*: Clean, verified hospital discharge summary for Type 2 Diabetes and Hypertension.
   - *Medications*: Metformin 500mg, Telmisartan 40mg, Atorvastatin 10mg.
   - *Status*: All instructions verified. Schedule and A4 Fridge Sheet ready.
   - *Caregiver*: Ramesh (Son, Account: `ramesh_caregiver` / `caregiver123`).

2. **Sri Ramana Rao (Age 72)**:
   - *Scenario*: Blurry, smudged outpatient handwritten prescription.
   - *Status*: Detected as `blurry`. Missing exact timings and doses flagged as `Needs verification`. Automatic reminder scheduling is strictly blocked.

3. **Smt. Sunitha Reddy (Age 64)**:
   - *Scenario*: Post-operative orders with conflicting antibiotic duration (5 days vs 3 days).
   - *Status*: Detected as `conflicting`. Flagged for doctor verification before scheduling.

---

## ⚠️ Prototype Limitations & Roadmap

1. **OCR Scope**: Native PDF text extraction is fully functional. Image OCR utilizes `pytesseract` when installed on the host OS; fallback heuristic analysis is provided when Tesseract is absent.
2. **Background Alarms**: In-browser audio chimes operate when the tab is active. Operating system background waking on mobile requires Progressive Web App (PWA) service workers or native mobile wrappers.
3. **Clinical Advice Disclaimer**: CareBridge AI provides source-grounded translation and scheduling assistance. It does not replace certified physician consultations.
