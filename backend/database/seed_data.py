import json
import os
import hashlib
from datetime import datetime, date, timedelta
from backend.database.db import get_db, init_db
from backend.config import Config

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def seed_database():
    init_db()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding synthetic healthcare demo data...")
        
        # 1. Create Users
        # Patient 1: Lakshmi Devi (Bilingual / Telugu preference)
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, role, language_preference)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (1, 'lakshmi', 'lakshmi@demo.carebridge.ai', hash_password('lakshmi123'), 'patient', 'te'))
        
        # Patient 2: Ramana Rao (Ambiguous/Blurry scenario)
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, role, language_preference)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (2, 'ramana', 'ramana@demo.carebridge.ai', hash_password('ramana123'), 'patient', 'en'))
        
        # Patient 3: Sunitha Reddy (Conflicting instructions scenario)
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, role, language_preference)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (3, 'sunitha', 'sunitha@demo.carebridge.ai', hash_password('sunitha123'), 'patient', 'te'))
        
        # Caregiver 1: Ramesh (Son of Lakshmi)
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, role, language_preference)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (4, 'ramesh_caregiver', 'ramesh@demo.carebridge.ai', hash_password('caregiver123'), 'caregiver', 'en'))

        # Caregiver 2: Swathi (Daughter of Ramana)
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, role, language_preference)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (5, 'swathi_caregiver', 'swathi@demo.carebridge.ai', hash_password('caregiver123'), 'caregiver', 'te'))

        # 2. Patient Profiles
        cursor.execute("""
            INSERT INTO patient_profiles (user_id, full_name, age, primary_language, emergency_contact, medical_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (1, 'Lakshmi Devi (లక్ష్మీ దేవి)', 68, 'te', '+91 98480 12345 (Son Ramesh)', 'Type 2 Diabetes Mellitus, Essential Hypertension. Fictional demo patient.'))

        cursor.execute("""
            INSERT INTO patient_profiles (user_id, full_name, age, primary_language, emergency_contact, medical_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (2, 'Ramana Rao (రమణ రావు)', 72, 'en', '+91 98480 54321 (Daughter Swathi)', 'Mild acid reflux, borderline blood sugar. Handwriting validation demo.'))

        cursor.execute("""
            INSERT INTO patient_profiles (user_id, full_name, age, primary_language, emergency_contact, medical_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (3, 'Sunitha Reddy (సునీత రెడ్డి)', 64, 'te', '+91 98480 99999 (Sister Anitha)', 'Post-operative right knee arthroscopy. Instruction conflict demo.'))

        # 3. Caregiver Relationships
        cursor.execute("""
            INSERT INTO caregiver_relationships (patient_id, caregiver_id, relationship_type, status, permissions)
            VALUES (?, ?, ?, ?, ?)
        """, (1, 4, 'Son (కుమారుడు)', 'active', json.dumps(["view_schedules", "view_documents", "view_careplan", "view_status"])))

        cursor.execute("""
            INSERT INTO caregiver_relationships (patient_id, caregiver_id, relationship_type, status, permissions)
            VALUES (?, ?, ?, ?, ?)
        """, (2, 5, 'Daughter (కుమార్తె)', 'active', json.dumps(["view_schedules", "view_documents", "view_status"])))

        # 4. Synthetic Documents
        # Doc 1: Lakshmi's Discharge Summary (Clean & Verified)
        doc1_filename = 'synthetic_discharge_lakshmi_devi.txt'
        doc1_path = os.path.join(Config.UPLOAD_FOLDER, doc1_filename)
        doc1_text = """CAREBRIDGE MEMORIAL HOSPITAL - DISCHARGE SUMMARY
PATIENT NAME: Smt. Lakshmi Devi | AGE: 68 Yrs | GENDER: Female
ADMISSION DATE: 10-Oct-2026 | DISCHARGE DATE: 15-Oct-2026
PRIMARY DIAGNOSIS: Type 2 Diabetes Mellitus with Essential Hypertension

PRESCRIBED MEDICATIONS:
1. Tab Metformin 500mg - 1 tablet twice daily after meals (08:30 AM, 08:30 PM) for 30 days.
2. Tab Telmisartan 40mg - 1 tablet once daily in the morning after breakfast (08:30 AM) for 30 days.
3. Tab Atorvastatin 10mg - 1 tablet once daily at bedtime (09:30 PM) for 30 days.

DIET & LIFESTYLE ADVICE:
- Diabetic diet: Strictly avoid refined white sugar, sweets, and carbonated beverages.
- Hypertensive diet: Low sodium salt (< 2 grams daily).
- Hydration: 2 liters of boiled and cooled water daily.
- Exercise: 20 minutes gentle walk every morning. No heavy lifting.

WARNING SIGNS (SEEK IMMEDIATE EMERGENCY CARE):
- Severe dizziness, lightheadedness, or sudden loss of balance.
- Chest pain radiating to left shoulder or sudden shortness of breath.
- Fasting blood sugar above 250 mg/dL or below 70 mg/dL.

FOLLOW-UP APPOINTMENT:
- Dr. K. S. Rao, MD (Internal Medicine) on 02-Nov-2026 at 10:30 AM, OPD Block B, Room 104."""

        with open(doc1_path, 'w', encoding='utf-8') as f:
            f.write(doc1_text)

        cursor.execute("""
            INSERT INTO documents (id, patient_id, original_filename, stored_filename, file_type, file_size, upload_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, 1, 'Hospital_Discharge_Summary_Lakshmi.txt', doc1_filename, 'text/plain', len(doc1_text), 'discharge_summary', 'extracted'))

        cursor.execute("""
            INSERT INTO extracted_texts (document_id, raw_text, extraction_method, confidence_score, quality_assessment)
            VALUES (?, ?, ?, ?, ?)
        """, (1, doc1_text, 'pdf_native', 0.98, 'clear'))

        # Doc 2: Ramana Rao's Blurry / Ambiguous Prescription
        doc2_filename = 'synthetic_blurry_rx_ramana.txt'
        doc2_path = os.path.join(Config.UPLOAD_FOLDER, doc2_filename)
        doc2_text = """CITY CLINIC - OUTPATIENT PRESCRIPTION
PATIENT: Sri Ramana Rao | AGE: 72 | DATE: 14-Oct-2026

Rx:
1. Tab Pantoprazole 40mg - 1 tab daily before breakfast (07:30 AM) x 14 days.
2. Tab Glycomet [strength smudged/unclear] - 1 tab twice daily - [exact clock time not stated].
3. Tab Ecospirin [dose missing] - daily - [unclear schedule].

NOTE: Handwriting on lines 2 and 3 has low legibility. Doses smudged."""

        with open(doc2_path, 'w', encoding='utf-8') as f:
            f.write(doc2_text)

        cursor.execute("""
            INSERT INTO documents (id, patient_id, original_filename, stored_filename, file_type, file_size, upload_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (2, 2, 'Prescription_RamanaRao_Handwritten.txt', doc2_filename, 'text/plain', len(doc2_text), 'prescription', 'needs_verification'))

        cursor.execute("""
            INSERT INTO extracted_texts (document_id, raw_text, extraction_method, confidence_score, quality_assessment)
            VALUES (?, ?, ?, ?, ?)
        """, (2, doc2_text, 'vision_heuristic', 0.65, 'blurry'))

        # Doc 3: Sunitha Reddy's Conflicting Instructions
        doc3_filename = 'synthetic_conflicting_rx_sunitha.txt'
        doc3_path = os.path.join(Config.UPLOAD_FOLDER, doc3_filename)
        doc3_text = """ORTHO SPECIALTY CARE - POST-OPERATIVE ORDERS
PATIENT: Smt. Sunitha Reddy | AGE: 64 | SURGERY: Right Knee Arthroscopy
DATE: 12-Oct-2026

SECTION 1 (Discharge Order):
1. Tab Amoxicillin-Clavulanate 625mg - 1 tablet twice daily for 5 days after food.
2. Tab Paracetamol 650mg - 1 tablet thrice daily for 3 days for joint pain.

SECTION 2 (Nurse Handover Sheet - Conflict):
1. Tab Amoxicillin-Clavulanate 625mg - Discontinue after 3 days if surgical wound is dry and no fever.

CONFLICT DETECTED: Antibiotic treatment duration is stated as 5 days in Section 1 and 3 days in Section 2."""

        with open(doc3_path, 'w', encoding='utf-8') as f:
            f.write(doc3_text)

        cursor.execute("""
            INSERT INTO documents (id, patient_id, original_filename, stored_filename, file_type, file_size, upload_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (3, 3, 'PostOp_Orders_SunithaReddy.txt', doc3_filename, 'text/plain', len(doc3_text), 'discharge_summary', 'needs_verification'))

        cursor.execute("""
            INSERT INTO extracted_texts (document_id, raw_text, extraction_method, confidence_score, quality_assessment)
            VALUES (?, ?, ?, ?, ?)
        """, (3, doc3_text, 'pdf_native', 0.95, 'conflicting'))

        # 5. Structured Instructions for Lakshmi Devi (Doc 1)
        cursor.execute("""
            INSERT INTO structured_instructions (
                document_id, medicine_name, strength, prescribed_dose, frequency,
                exact_time, duration, food_instruction, doctor_notes, diet_advice,
                activity_restrictions, follow_up_date, warning_signs, status, raw_source_snippet, readability_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 'Metformin', '500mg', '1 tablet', 'Twice daily',
            '08:30 AM, 08:30 PM', '30 days', 'After meals (భోజనం తర్వాత)',
            'Take regularly for blood sugar control.', 'Diabetic diet: Avoid white sugar and sweets.',
            'Gentle walk 20 min morning. No heavy lifting.', '2026-11-02',
            'Dizziness, chest pain, sugar > 250 mg/dL', 'verified',
            'Tab Metformin 500mg - 1 tablet twice daily after meals (08:30 AM, 08:30 PM) for 30 days.', 78.4
        ))

        cursor.execute("""
            INSERT INTO structured_instructions (
                document_id, medicine_name, strength, prescribed_dose, frequency,
                exact_time, duration, food_instruction, doctor_notes, diet_advice,
                activity_restrictions, follow_up_date, warning_signs, status, raw_source_snippet, readability_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 'Telmisartan', '40mg', '1 tablet', 'Once daily',
            '08:30 AM', '30 days', 'After breakfast (అల్పాహారం తర్వాత)',
            'Blood pressure management.', 'Low salt (< 2g daily).',
            'Avoid sudden standing to prevent lightheadedness.', '2026-11-02',
            'Chest pain, shortness of breath', 'verified',
            'Tab Telmisartan 40mg - 1 tablet once daily in the morning after breakfast (08:30 AM) for 30 days.', 82.1
        ))

        cursor.execute("""
            INSERT INTO structured_instructions (
                document_id, medicine_name, strength, prescribed_dose, frequency,
                exact_time, duration, food_instruction, doctor_notes, diet_advice,
                activity_restrictions, follow_up_date, warning_signs, status, raw_source_snippet, readability_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 'Atorvastatin', '10mg', '1 tablet', 'Once daily',
            '09:30 PM', '30 days', 'Bedtime (రాత్రి నిద్రపోయే ముందు)',
            'Cholesterol management.', 'Low oil and low saturated fat.',
            'Rest well at night.', '2026-11-02',
            'Unexplained muscle weakness', 'verified',
            'Tab Atorvastatin 10mg - 1 tablet once daily at bedtime (09:30 PM) for 30 days.', 79.5
        ))

        # 6. Structured Instructions for Ramana Rao (Doc 2 - Ambiguous)
        cursor.execute("""
            INSERT INTO structured_instructions (
                document_id, medicine_name, strength, prescribed_dose, frequency,
                exact_time, duration, food_instruction, doctor_notes, diet_advice,
                activity_restrictions, follow_up_date, warning_signs, status, raw_source_snippet, readability_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            2, 'Pantoprazole', '40mg', '1 tablet', 'Once daily',
            '07:30 AM', '14 days', 'Before breakfast (అల్పాహారానికి ముందు)',
            'For acid reflux.', 'Not mentioned in document',
            'Not mentioned in document', 'Not mentioned in document',
            'Not mentioned in document', 'verified',
            'Tab Pantoprazole 40mg - 1 tab daily before breakfast (07:30 AM) x 14 days.', 80.0
        ))

        cursor.execute("""
            INSERT INTO structured_instructions (
                document_id, medicine_name, strength, prescribed_dose, frequency,
                exact_time, duration, food_instruction, doctor_notes, diet_advice,
                activity_restrictions, follow_up_date, warning_signs, status, raw_source_snippet, readability_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            2, 'Glycomet', 'Needs verification', '1 tablet', 'Twice daily',
            'Needs verification', 'Not mentioned in document', 'Needs verification',
            'Strength and exact times are smudged in handwriting.', 'Not mentioned',
            'Not mentioned', 'Not mentioned',
            'Severe hypoglycemia signs', 'needs_verification',
            'Tab Glycomet [strength smudged/unclear] - 1 tab twice daily - [exact clock time not stated].', 55.0
        ))

        # 7. Structured Instructions for Sunitha Reddy (Doc 3 - Conflicting)
        cursor.execute("""
            INSERT INTO structured_instructions (
                document_id, medicine_name, strength, prescribed_dose, frequency,
                exact_time, duration, food_instruction, doctor_notes, diet_advice,
                activity_restrictions, follow_up_date, warning_signs, status, raw_source_snippet, readability_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            3, 'Amoxicillin-Clavulanate', '625mg', '1 tablet', 'Twice daily',
            'Needs confirmation', 'Conflicting: 5 days vs 3 days', 'After food',
            'Section 1 specifies 5 days course, Section 2 specifies 3 days stop if wound dry. Verify with surgeon before scheduling.', 'Regular soft diet',
            'Keep dressing clean and dry.', 'Not mentioned in document',
            'Fever > 101F, redness or pus at wound site', 'conflicting',
            'Section 1: 5 days vs Section 2: Discontinue after 3 days if surgical wound is dry.', 62.0
        ))

        # 8. Verified Medicine Schedules for Lakshmi Devi
        today_str = date.today().isoformat()
        
        cursor.execute("""
            INSERT INTO medicine_schedules (
                patient_id, document_id, medicine_name, strength, dose, frequency,
                exact_times, food_relation, duration_days, start_date, is_verified, verification_notes, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 1, 'Metformin', '500mg', '1 tablet', 'Twice daily',
            json.dumps(["08:30", "20:30"]), 'after_food', 30, today_str, 1, 'Verified from Discharge Summary Page 1', 1
        ))
        metformin_sched_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO medicine_schedules (
                patient_id, document_id, medicine_name, strength, dose, frequency,
                exact_times, food_relation, duration_days, start_date, is_verified, verification_notes, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 1, 'Telmisartan', '40mg', '1 tablet', 'Once daily',
            json.dumps(["08:30"]), 'after_food', 30, today_str, 1, 'Verified blood pressure prescription', 1
        ))
        telmisartan_sched_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO medicine_schedules (
                patient_id, document_id, medicine_name, strength, dose, frequency,
                exact_times, food_relation, duration_days, start_date, is_verified, verification_notes, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 1, 'Atorvastatin', '10mg', '1 tablet', 'Once daily',
            json.dumps(["21:30"]), 'after_food', 30, today_str, 1, 'Verified bedtime lipid medication', 1
        ))
        atorvastatin_sched_id = cursor.lastrowid

        # 9. Dose Events for Lakshmi Devi (Today & Past 2 Days)
        for offset in [-2, -1, 0]:
            day = (date.today() + timedelta(days=offset)).isoformat()
            
            # Morning Telmisartan 08:30
            status = 'taken' if offset < 0 else 'taken'
            cursor.execute("""
                INSERT INTO dose_events (schedule_id, patient_id, scheduled_time, status, taken_at, notes, recorded_by_user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (telmisartan_sched_id, 1, f"{day} 08:30", status, f"{day} 08:35:00", 'Taken with breakfast', 1))

            # Morning Metformin 08:30
            cursor.execute("""
                INSERT INTO dose_events (schedule_id, patient_id, scheduled_time, status, taken_at, notes, recorded_by_user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (metformin_sched_id, 1, f"{day} 08:30", status, f"{day} 08:35:00", 'Taken with breakfast', 1))

            # Evening Metformin 20:30
            status_eve = 'taken' if offset < 0 else 'pending'
            taken_at = f"{day} 20:40:00" if status_eve == 'taken' else None
            cursor.execute("""
                INSERT INTO dose_events (schedule_id, patient_id, scheduled_time, status, taken_at, notes, recorded_by_user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (metformin_sched_id, 1, f"{day} 20:30", status_eve, taken_at, None, 1 if status_eve == 'taken' else None))

            # Night Atorvastatin 21:30
            status_night = 'taken' if offset < 0 else 'pending'
            taken_at_night = f"{day} 21:35:00" if status_night == 'taken' else None
            cursor.execute("""
                INSERT INTO dose_events (schedule_id, patient_id, scheduled_time, status, taken_at, notes, recorded_by_user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (atorvastatin_sched_id, 1, f"{day} 21:30", status_night, taken_at_night, None, 1 if status_night == 'taken' else None))

        # 10. Care Plan for Lakshmi Devi
        cursor.execute("""
            INSERT INTO care_plans (
                patient_id, document_id, title_en, title_te, summary_en, summary_te,
                medicines_json, diet_en, diet_te, activity_en, activity_te,
                follow_up_date, warning_signs_en, warning_signs_te, validation_status, discrepancy_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 1,
            'Discharge Care Plan - Smt. Lakshmi Devi',
            'డిశ్చార్జ్ సంరక్షణ ప్రణాళిక - శ్రీమతి లక్ష్మీ దేవి',
            'Patient has been stabilized for Type 2 Diabetes and Hypertension. Daily adherence to blood pressure and glucose medications with low-salt diet is critical.',
            'టైప్ 2 మధుమేహం మరియు రక్తపోటు కోసం చికిత్స అందించబడింది. రోజూ వేళకు బీపీ మరియు షుగర్ మందులు వేసుకోవడం, తక్కువ ఉప్పు ఆహారం తీసుకోవడం ఎంతో ముఖ్యం.',
            json.dumps([
                {"name": "Metformin 500mg", "dose": "1 tab", "time": "08:30 AM, 08:30 PM", "telugu": "ఉదయం మరియు రాత్రి భోజనం తర్వాత"},
                {"name": "Telmisartan 40mg", "dose": "1 tab", "time": "08:30 AM", "telugu": "ఉదయం అల్పాహారం తర్వాత"},
                {"name": "Atorvastatin 10mg", "dose": "1 tab", "time": "09:30 PM", "telugu": "రాత్రి నిద్రపోయే ముందు"}
            ]),
            'Diabetic diet: Avoid sweets and sugar. Low sodium: Under 2 grams salt daily. Drink 2 liters of warm boiled water.',
            'మధుమేహ ఆహారం: చక్కెర, స్వీట్లు మానేయండి. ఉప్పు చాలా తక్కువగా (రోజుకు 2 గ్రాముల లోపు) వాడండి. రోజూ 2 లీటర్ల కాచి చల్లార్చిన నీరు త్రాగండి.',
            '20 minutes slow morning walk. Avoid heavy lifting or strain. Rest when feeling tired.',
            'ఉదయం 20 నిమిషాలు నిదానంగా నడవండి. బరువైన పనులు చేయవద్దు. అలసటగా అనిపిస్తే విశ్రాంతి తీసుకోండి.',
            '02-Nov-2026',
            'Severe dizziness, chest pain radiating to arm, blood sugar over 250 mg/dL or under 70 mg/dL.',
            'తీవ్రమైన తలతిరగడం, గుండెల్లో నొప్పి లేదా శ్వాస తీసుకోవడంలో ఇబ్బంది, షుగర్ 250 దాటినా లేదా 70 కి పడిపోయినా వెంటనే ఆసుపత్రికి వెళ్ళండి.',
            'verified',
            'All items cross-checked with Hospital Discharge Summary page 1. No conflicting instructions.'
        ))

        # 11. Follow-up Appointments
        cursor.execute("""
            INSERT INTO follow_up_appointments (patient_id, doctor_or_dept, appointment_date, appointment_time, location, instructions, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 'Dr. K. S. Rao, MD (Internal Medicine)', '2026-11-02', '10:30 AM',
            'OPD Block B, Room 104, CareBridge Memorial Hospital',
            'Bring fasting blood sugar and HbA1c lab report. Bring all current medicine strips.',
            'scheduled'
        ))

        # 12. Conversation History for Lakshmi Devi
        cursor.execute("""
            INSERT INTO conversations (id, patient_id, title)
            VALUES (?, ?, ?)
        """, (1, 1, 'Lakshmi Devi - Medicine Consultation'))

        # Messages
        cursor.execute("""
            INSERT INTO messages (conversation_id, sender_role, message_type, content_en, content_te, source_document_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            1, 'assistant', 'text',
            'Hello! How can I help you with your medicines or care today? You can ask me what your prescription says, when to take your medicines, or upload any medical document.',
            'నమస్కారం! మీ మందులు లేదా ఆరోగ్య సూచనల గురించి నేను ఎలా సహాయం చేయగలను? మీ ప్రిస్క్రిప్షన్ లేదా డిశ్చార్జ్ సమ్మరీ గురించి నన్ను అడగవచ్చు.',
            None
        ))

        cursor.execute("""
            INSERT INTO messages (conversation_id, sender_role, message_type, content_en, content_te, source_document_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            1, 'user', 'text',
            'What medicines should I take in the morning?',
            'నేను ఉదయం ఏ మందులు తీసుకోవాలి?',
            None
        ))

        cursor.execute("""
            INSERT INTO messages (conversation_id, sender_role, message_type, content_en, content_te, source_document_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            1, 'assistant', 'text',
            'According to your verified discharge summary, you have two medicines scheduled for the morning at 08:30 AM after breakfast:\n\n1. **Metformin 500mg** — 1 tablet (for diabetes / blood sugar control)\n2. **Telmisartan 40mg** — 1 tablet (for blood pressure control)\n\nPlease take both after your morning meal with a glass of water.',
            'మీ నిర్ధారిత డిశ్చార్జ్ సమ్మరీ ప్రకారం, మీరు ఉదయం 08:30 గంటలకు అల్పాహారం (టిఫిన్) తిన్న తర్వాత రెండు మందులు తీసుకోవాలి:\n\n1. **మెట్‌ఫార్మిన్ (Metformin 500mg)** — 1 మాత్ర (షుగర్ నియంత్రణ కోసం)\n2. **టెల్మిసార్టన్ (Telmisartan 40mg)** — 1 మాత్ర (బీపీ నియంత్రణ కోసం)\n\nదయచేసి ఈ రెండు మాత్రలను టిఫిన్ తిన్న తర్వాత ఒక గ్లాసు నీటితో వేసుకోండి.',
            1
        ))

        print("Synthetic demo data seeded successfully!")

if __name__ == '__main__':
    seed_database()
