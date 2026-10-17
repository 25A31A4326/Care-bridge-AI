-- CareBridge AI SQLite Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('patient', 'caregiver', 'doctor')),
    language_preference TEXT DEFAULT 'te',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patient_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    age INTEGER,
    primary_language TEXT DEFAULT 'te',
    emergency_contact TEXT,
    medical_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS caregiver_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    caregiver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    relationship_type TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'revoked', 'pending')),
    permissions TEXT DEFAULT '["view_schedules", "view_documents", "view_careplan", "view_status"]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    upload_type TEXT NOT NULL CHECK(upload_type IN ('prescription', 'medicine_package', 'discharge_summary', 'medical_report', 'pdf')),
    status TEXT DEFAULT 'uploaded' CHECK(status IN ('uploaded', 'extracted', 'needs_verification', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS extracted_texts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    extraction_method TEXT NOT NULL,
    confidence_score REAL DEFAULT 1.0,
    quality_assessment TEXT DEFAULT 'clear' CHECK(quality_assessment IN ('clear', 'blurry', 'incomplete', 'conflicting', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS structured_instructions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    medicine_name TEXT NOT NULL,
    strength TEXT,
    prescribed_dose TEXT,
    frequency TEXT,
    exact_time TEXT,
    duration TEXT,
    food_instruction TEXT,
    doctor_notes TEXT,
    diet_advice TEXT,
    activity_restrictions TEXT,
    follow_up_date TEXT,
    warning_signs TEXT,
    status TEXT DEFAULT 'verified' CHECK(status IN ('verified', 'needs_verification', 'conflicting')),
    raw_source_snippet TEXT,
    readability_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medicine_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    medicine_name TEXT NOT NULL,
    strength TEXT,
    dose TEXT NOT NULL,
    frequency TEXT NOT NULL,
    exact_times TEXT NOT NULL, -- JSON array string e.g. ["08:00", "20:00"]
    food_relation TEXT DEFAULT 'after_food',
    duration_days INTEGER,
    start_date TEXT,
    is_verified INTEGER DEFAULT 0,
    verification_notes TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dose_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL REFERENCES medicine_schedules(id) ON DELETE CASCADE,
    patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scheduled_time TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'taken', 'missed', 'snoozed')),
    taken_at TIMESTAMP,
    notes TEXT,
    recorded_by_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS care_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    title_en TEXT NOT NULL,
    title_te TEXT NOT NULL,
    summary_en TEXT,
    summary_te TEXT,
    medicines_json TEXT,
    diet_en TEXT,
    diet_te TEXT,
    activity_en TEXT,
    activity_te TEXT,
    follow_up_date TEXT,
    warning_signs_en TEXT,
    warning_signs_te TEXT,
    validation_status TEXT DEFAULT 'verified',
    discrepancy_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS follow_up_appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_or_dept TEXT NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT,
    location TEXT,
    instructions TEXT,
    status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_role TEXT NOT NULL CHECK(sender_role IN ('user', 'assistant', 'system')),
    message_type TEXT DEFAULT 'text',
    content_en TEXT,
    content_te TEXT,
    source_document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL,
    metadata_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
