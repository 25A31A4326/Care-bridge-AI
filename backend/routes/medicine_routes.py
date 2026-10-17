import json
from datetime import datetime, date, timedelta
from flask import Blueprint, request, jsonify
from backend.database.db import get_db

medicine_bp = Blueprint('medicines', __name__, url_prefix='/api/medicines')

@medicine_bp.route('/schedule', methods=['GET'])
def get_schedules():
    patient_id = request.args.get('patient_id', default=1, type=int)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM medicine_schedules
            WHERE patient_id = ? AND is_active = 1
            ORDER BY is_verified DESC, id ASC
        """, (patient_id,))
        schedules = [dict(r) for r in cursor.fetchall()]
        
        # Parse exact_times JSON
        for s in schedules:
            try:
                s['exact_times_list'] = json.loads(s['exact_times'])
            except:
                s['exact_times_list'] = [s['exact_times']]
                
        return jsonify({"schedules": schedules})

@medicine_bp.route('/schedule', methods=['POST'])
def create_schedule():
    data = request.get_json() or {}
    patient_id = data.get('patient_id', 1)
    medicine_name = data.get('medicine_name', '').strip()
    strength = data.get('strength', '').strip()
    dose = data.get('dose', '').strip()
    frequency = data.get('frequency', '').strip()
    exact_times = data.get('exact_times', [])
    food_relation = data.get('food_relation', 'after_food')
    duration_days = data.get('duration_days', 30)
    is_verified = data.get('is_verified', 0)
    verification_notes = data.get('verification_notes', '')

    if not medicine_name or not dose or not exact_times:
        return jsonify({"error": "Medicine name, dose, and exact times are required"}), 400

    # Rule: "Only enable automatic reminders when the medication schedule and exact times are sufficiently verified."
    if not is_verified:
        return jsonify({
            "error": "Cannot enable automatic reminders. Medication schedule and exact clock times must be verified by doctor or caregiver first.",
            "error_te": "డాక్టర్ లేదా సంరక్షకులు సమయాలను ధృవీకరించిన తర్వాతే రిమైండర్లు అమర్చవచ్చు."
        }), 400

    if isinstance(exact_times, list):
        exact_times_str = json.dumps(exact_times)
    else:
        exact_times_str = json.dumps([str(exact_times)])

    today_str = date.today().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO medicine_schedules (
                patient_id, medicine_name, strength, dose, frequency,
                exact_times, food_relation, duration_days, start_date, is_verified, verification_notes, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (patient_id, medicine_name, strength, dose, frequency, exact_times_str, food_relation, duration_days, today_str, 1, verification_notes))
        sched_id = cursor.lastrowid
        
        # Automatically generate dose events for today
        for t in (exact_times if isinstance(exact_times, list) else [exact_times]):
            cursor.execute("""
                INSERT INTO dose_events (schedule_id, patient_id, scheduled_time, status)
                VALUES (?, ?, ?, 'pending')
            """, (sched_id, patient_id, f"{today_str} {t}"))

    return jsonify({"message": "Medicine schedule created and verified", "schedule_id": sched_id})

@medicine_bp.route('/doses/today', methods=['GET'])
def get_today_doses():
    patient_id = request.args.get('patient_id', default=1, type=int)
    today_str = date.today().isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if today's dose events exist, if not create them from verified schedules
        cursor.execute("SELECT COUNT(*) FROM dose_events WHERE patient_id = ? AND scheduled_time LIKE ?", (patient_id, f"{today_str}%"))
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("SELECT * FROM medicine_schedules WHERE patient_id = ? AND is_active = 1 AND is_verified = 1", (patient_id,))
            active_scheds = [dict(r) for r in cursor.fetchall()]
            for s in active_scheds:
                try:
                    times = json.loads(s['exact_times'])
                except:
                    times = [s['exact_times']]
                for t in times:
                    cursor.execute("""
                        INSERT INTO dose_events (schedule_id, patient_id, scheduled_time, status)
                        VALUES (?, ?, ?, 'pending')
                    """, (s['id'], patient_id, f"{today_str} {t}"))

        cursor.execute("""
            SELECT de.*, ms.medicine_name, ms.strength, ms.dose, ms.food_relation, ms.frequency
            FROM dose_events de
            JOIN medicine_schedules ms ON de.schedule_id = ms.id
            WHERE de.patient_id = ? AND de.scheduled_time LIKE ?
            ORDER BY de.scheduled_time ASC
        """, (patient_id, f"{today_str}%"))
        
        doses = [dict(r) for r in cursor.fetchall()]
        
        # Compute summary
        total = len(doses)
        taken = len([d for d in doses if d['status'] == 'taken'])
        pending = len([d for d in doses if d['status'] == 'pending'])
        missed = len([d for d in doses if d['status'] == 'missed'])
        
        return jsonify({
            "date": today_str,
            "doses": doses,
            "summary": {
                "total": total,
                "taken": taken,
                "pending": pending,
                "missed": missed
            }
        })

@medicine_bp.route('/doses/calendar', methods=['GET'])
def get_seven_day_calendar():
    patient_id = request.args.get('patient_id', default=1, type=int)
    today = date.today()
    days_data = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Generate 7-day range: 3 days past, today, 3 days ahead
        for offset in range(-3, 4):
            day_date = today + timedelta(days=offset)
            day_str = day_date.isoformat()
            
            cursor.execute("""
                SELECT de.*, ms.medicine_name, ms.strength, ms.food_relation
                FROM dose_events de
                JOIN medicine_schedules ms ON de.schedule_id = ms.id
                WHERE de.patient_id = ? AND de.scheduled_time LIKE ?
                ORDER BY de.scheduled_time ASC
            """, (patient_id, f"{day_str}%"))
            
            day_doses = [dict(r) for r in cursor.fetchall()]
            days_data.append({
                "date": day_str,
                "day_name": day_date.strftime("%a"),
                "is_today": offset == 0,
                "doses": day_doses,
                "total": len(day_doses),
                "taken": len([d for d in day_doses if d['status'] == 'taken']),
                "pending": len([d for d in day_doses if d['status'] == 'pending']),
                "missed": len([d for d in day_doses if d['status'] == 'missed'])
            })
            
        return jsonify({"calendar": days_data})

@medicine_bp.route('/doses/<int:dose_id>/status', methods=['POST'])
def update_dose_status(dose_id: int):
    data = request.get_json() or {}
    status = data.get('status') # 'taken', 'missed', 'snoozed'
    notes = data.get('notes', '')
    user_id = data.get('user_id', 1)
    
    if status not in ['taken', 'missed', 'snoozed', 'pending']:
        return jsonify({"error": "Invalid status"}), 400
        
    taken_at = datetime.now().isoformat() if status == 'taken' else None
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE dose_events
            SET status = ?, taken_at = ?, notes = ?, recorded_by_user_id = ?
            WHERE id = ?
        """, (status, taken_at, notes, user_id, dose_id))
        
    # Safety notice for missed dose
    missed_advice_en = "If you missed a dose, take it as soon as remembered unless it is almost time for your next scheduled dose. Never take two doses at once to make up for a missed dose."
    missed_advice_te = "ఒకవేళ మీరు మందు వేసుకోవడం మరిచిపోతే, తర్వాతి సమయం దగ్గరపడేంతవరకు వెంటనే వేసుకోవచ్చు. అయితే ఎట్టి పరిస్థితుల్లోనూ రెండు మాత్రలు కలిపి ఒకేసారి వేసుకోకూడదు."

    return jsonify({
        "message": f"Dose marked as {status}",
        "dose_id": dose_id,
        "status": status,
        "missed_dose_safety": {
            "en": missed_advice_en,
            "te": missed_advice_te
        } if status == 'missed' else None
    })
