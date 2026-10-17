import json
from flask import Blueprint, request, jsonify, send_file
from backend.database.db import get_db
from backend.services.pdf_service import generate_fridge_sheet_pdf

careplan_bp = Blueprint('careplan', __name__, url_prefix='/api/careplan')

@careplan_bp.route('/current', methods=['GET'])
def get_current_careplan():
    patient_id = request.args.get('patient_id', default=1, type=int)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM care_plans WHERE patient_id = ? ORDER BY id DESC LIMIT 1", (patient_id,))
        cp_row = cursor.fetchone()
        
        if not cp_row:
            return jsonify({"care_plan": None, "message": "No care plan generated yet"})
            
        cp = dict(cp_row)
        try:
            cp['medicines_list'] = json.loads(cp['medicines_json'])
        except:
            cp['medicines_list'] = []

        # Fetch patient profile and follow up
        cursor.execute("SELECT full_name, age, emergency_contact FROM patient_profiles WHERE user_id = ?", (patient_id,))
        patient = dict(cursor.fetchone() or {})

        cursor.execute("SELECT * FROM follow_up_appointments WHERE patient_id = ? AND status = 'scheduled' LIMIT 1", (patient_id,))
        appt = cursor.fetchone()

        return jsonify({
            "care_plan": cp,
            "patient": patient,
            "appointment": dict(appt) if appt else None
        })

@careplan_bp.route('/fridge-sheet-pdf', methods=['GET'])
def download_fridge_sheet():
    patient_id = request.args.get('patient_id', default=1, type=int)
    lang = request.args.get('lang', 'en')
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Patient info
        cursor.execute("SELECT full_name, age, emergency_contact FROM patient_profiles WHERE user_id = ?", (patient_id,))
        patient_row = cursor.fetchone()
        patient_info = dict(patient_row) if patient_row else {"full_name": "Lakshmi Devi", "age": 68, "emergency_contact": "+91 98480 12345"}
        
        # Verified schedules
        cursor.execute("SELECT * FROM medicine_schedules WHERE patient_id = ? AND is_active = 1", (patient_id,))
        schedules = [dict(r) for r in cursor.fetchall()]
        
        # Care plan
        cursor.execute("SELECT * FROM care_plans WHERE patient_id = ? ORDER BY id DESC LIMIT 1", (patient_id,))
        cp_row = cursor.fetchone()
        careplan = dict(cp_row) if cp_row else {}
        
        # Appointment
        cursor.execute("SELECT * FROM follow_up_appointments WHERE patient_id = ? AND status = 'scheduled' LIMIT 1", (patient_id,))
        appt_row = cursor.fetchone()
        appt = dict(appt_row) if appt_row else {}

    pdf_buffer = generate_fridge_sheet_pdf(patient_info, schedules, careplan, appt, lang=lang)
    filename = f"CareBridge_Fridge_Sheet_{patient_info.get('full_name', 'Patient').replace(' ', '_')}_{lang}.pdf"
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
