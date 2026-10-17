import json
from flask import Blueprint, request, jsonify
from backend.database.db import get_db

caregiver_bp = Blueprint('caregiver', __name__, url_prefix='/api/caregiver')

@caregiver_bp.route('/relationships', methods=['GET'])
def get_relationships():
    patient_id = request.args.get('patient_id', default=1, type=int)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cr.id, cr.patient_id, cr.caregiver_id, cr.relationship_type,
                   cr.status, cr.permissions, cr.created_at,
                   u.username, u.email
            FROM caregiver_relationships cr
            JOIN users u ON cr.caregiver_id = u.id
            WHERE cr.patient_id = ?
        """, (patient_id,))
        relationships = [dict(r) for r in cursor.fetchall()]
        for r in relationships:
            try:
                r['permissions_list'] = json.loads(r['permissions'])
            except:
                r['permissions_list'] = []
                
        return jsonify({
            "relationships": relationships,
            "active_count": len([r for r in relationships if r['status'] == 'active']),
            "max_allowed": 2
        })

@caregiver_bp.route('/authorize', methods=['POST'])
def authorize_caregiver():
    data = request.get_json() or {}
    patient_id = data.get('patient_id', 1)
    email = data.get('email', '').strip()
    relationship_type = data.get('relationship_type', 'Family Member')
    permissions = data.get('permissions', ["view_schedules", "view_documents", "view_careplan", "view_status"])

    if not email:
        return jsonify({"error": "Caregiver email is required"}), 400

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Enforce Requirement 10: "Allow a patient to authorize up to two trusted caregivers."
        cursor.execute("SELECT COUNT(*) FROM caregiver_relationships WHERE patient_id = ? AND status = 'active'", (patient_id,))
        active_count = cursor.fetchone()[0]
        if active_count >= 2:
            return jsonify({
                "error": "Maximum of 2 active authorized caregivers reached. Please revoke an existing caregiver first.",
                "error_te": "గరిష్టంగా ఇద్దరు సంరక్షకులను మాత్రమే అనుమతించవచ్చు. కొత్తవారిని చేర్చడానికి ముందున్న వారిని రద్దు చేయండి."
            }), 400

        # Find or create caregiver user account
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        caregiver_user = cursor.fetchone()
        
        if not caregiver_user:
            # Create a caregiver account with temporary hashed password
            import hashlib
            temp_hash = hashlib.sha256("caregiver123".encode('utf-8')).hexdigest()
            username = email.split('@')[0] + "_caregiver"
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, role, language_preference)
                VALUES (?, ?, ?, 'caregiver', 'te')
            """, (username, email, temp_hash))
            caregiver_id = cursor.lastrowid
        else:
            caregiver_id = caregiver_user['id']

        # Insert relationship
        cursor.execute("""
            INSERT INTO caregiver_relationships (patient_id, caregiver_id, relationship_type, status, permissions)
            VALUES (?, ?, ?, 'active', ?)
        """, (patient_id, caregiver_id, relationship_type, json.dumps(permissions)))
        rel_id = cursor.lastrowid

    return jsonify({"message": "Caregiver authorized successfully", "relationship_id": rel_id})

@caregiver_bp.route('/revoke/<int:rel_id>', methods=['POST'])
def revoke_caregiver(rel_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE caregiver_relationships SET status = 'revoked' WHERE id = ?", (rel_id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Caregiver relationship not found"}), 404
            
    return jsonify({"message": "Caregiver access revoked successfully"})

@caregiver_bp.route('/patient-status', methods=['GET'])
def get_patient_status_for_caregiver():
    caregiver_id = request.args.get('caregiver_id', type=int)
    patient_id = request.args.get('patient_id', default=1, type=int)

    if not caregiver_id:
        return jsonify({"error": "Caregiver ID is required for verification"}), 401

    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verify active authorization on backend
        cursor.execute("""
            SELECT status, permissions FROM caregiver_relationships
            WHERE caregiver_id = ? AND patient_id = ?
        """, (caregiver_id, patient_id))
        rel = cursor.fetchone()
        
        if not rel or rel['status'] != 'active':
            return jsonify({
                "error": "Unauthorized. You do not have active caregiver permissions for this patient.",
                "error_te": "అనుమతి నిరాకరించబడింది. ఈ రోగి వివరాలను చూసే హక్కు మీకు లేదు."
            }), 403

        permissions = json.loads(rel['permissions'])
        
        # Fetch Patient Demographics
        cursor.execute("SELECT full_name, age, emergency_contact, primary_language FROM patient_profiles WHERE user_id = ?", (patient_id,))
        patient = dict(cursor.fetchone() or {})
        
        # Dose Status Today
        doses_today = []
        if "view_status" in permissions:
            from datetime import date
            today_str = date.today().isoformat()
            cursor.execute("""
                SELECT de.*, ms.medicine_name, ms.strength, ms.food_relation
                FROM dose_events de
                JOIN medicine_schedules ms ON de.schedule_id = ms.id
                WHERE de.patient_id = ? AND de.scheduled_time LIKE ?
                ORDER BY de.scheduled_time ASC
            """, (patient_id, f"{today_str}%"))
            doses_today = [dict(r) for r in cursor.fetchall()]

        # Verified Schedules
        schedules = []
        if "view_schedules" in permissions:
            cursor.execute("""
                SELECT * FROM medicine_schedules
                WHERE patient_id = ? AND is_active = 1
                ORDER BY is_verified DESC
            """, (patient_id,))
            schedules = [dict(r) for r in cursor.fetchall()]

        # Care Plan
        care_plan = None
        if "view_careplan" in permissions:
            cursor.execute("""
                SELECT * FROM care_plans
                WHERE patient_id = ?
                ORDER BY id DESC LIMIT 1
            """, (patient_id,))
            cp = cursor.fetchone()
            if cp:
                care_plan = dict(cp)

        # Follow-up Appointments
        cursor.execute("""
            SELECT * FROM follow_up_appointments
            WHERE patient_id = ? AND status = 'scheduled'
            ORDER BY appointment_date ASC LIMIT 1
        """, (patient_id,))
        appt = cursor.fetchone()
        appointment = dict(appt) if appt else None

        return jsonify({
            "patient": patient,
            "permissions": permissions,
            "doses_today": doses_today,
            "schedules": schedules,
            "care_plan": care_plan,
            "appointment": appointment
        })
