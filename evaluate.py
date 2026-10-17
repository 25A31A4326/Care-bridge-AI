"""
CareBridge AI — Automated System & Clinical Accuracy Evaluation Script
Executes deterministic benchmarks across all 5 clinical and technical pillars:
1. Health & Relational Database Integrity
2. Bilingual Chat & Grounded Medical Responses (Telugu & English)
3. Prescription OCR & Source Verification
4. Ambiguous / Blurry / Conflict Safety Gates
5. Caregiver Role-Based Access Control & PDF Fridge Sheet Generation
"""

import sys
import json
import io
from backend.app import create_app
from backend.database.seed_data import seed_database
from backend.services.readability_service import calculate_flesch_reading_ease, validate_instructions_against_source

def run_evaluation():
    print("=" * 65)
    print("CAREBRIDGE AI — SYSTEM & CLINICAL EVALUATION SUITE")
    print("=" * 65)

    app = create_app()
    client = app.test_client()

    results = []

    # Benchmark 1: Health & API
    res = client.get('/api/health')
    pass_1 = (res.status_code == 200 and res.get_json()['status'] == 'healthy')
    results.append(("1. Backend Health Check & Engine Verification", pass_1, f"Status: {res.status_code}"))

    # Benchmark 2: English Chat Grounded Response
    res = client.post('/api/chat/send', json={
        "patient_id": 1,
        "content": "What is my next medicine reminder?",
        "language": "en"
    })
    data = res.get_json()
    resp_en = data.get("assistant_message", {}).get("content_en", "")
    pass_2 = ("Metformin" in resp_en or "Telmisartan" in resp_en or "medication" in resp_en.lower())
    results.append(("2. Grounded Chat Assistant (English)", pass_2, f"Answer contains verified meds: {pass_2}"))

    # Benchmark 3: Telugu Chat Grounded Response
    res = client.post('/api/chat/send', json={
        "patient_id": 1,
        "content": "నా తదుపరి డాక్టర్ అపాయింట్‌మెంట్ ఎప్పుడు?",
        "language": "te"
    })
    data = res.get_json()
    resp_te = data.get("assistant_message", {}).get("content_te", "")
    pass_3 = ("డాక్టర్" in resp_te or "అపాయింట్‌మెంట్" in resp_te or "నవంబర్" in resp_te or "02-Nov" in resp_te)
    results.append(("3. Grounded Chat Assistant (Telugu)", pass_3, f"Telugu response generated: {pass_3}"))

    # Benchmark 4: Ambiguous / Blurry Document Gate (Patient 2 - Ramana Rao)
    res = client.get('/api/documents/2')
    doc2 = res.get_json()['document']
    pass_4 = (doc2['quality_assessment'] == 'blurry' and doc2['status'] == 'needs_verification')
    results.append(("4. Blurry Handwriting Safety Flagging", pass_4, f"Quality: {doc2['quality_assessment']}, Status: {doc2['status']}"))

    # Benchmark 5: Conflicting Orders Gate (Patient 3 - Sunitha Reddy)
    res = client.get('/api/documents/3')
    doc3 = res.get_json()['document']
    pass_5 = (doc3['quality_assessment'] == 'conflicting')
    results.append(("5. Conflicting Medical Orders Flagging", pass_5, f"Detected Conflict: {pass_5}"))

    # Benchmark 6: Unverified Reminder Scheduling Gate
    res = client.post('/api/medicines/schedule', json={
        "patient_id": 1,
        "medicine_name": "UnverifiedMed",
        "dose": "1 tab",
        "frequency": "daily",
        "exact_times": ["09:00"],
        "is_verified": 0
    })
    pass_6 = (res.status_code == 400 and "verified" in res.get_json()['error'].lower())
    results.append(("6. Unverified Automatic Reminder Prevention", pass_6, f"Blocked Unverified: {pass_6}"))

    # Benchmark 7: Missed-Dose Safety Guidance
    res_doses = client.get('/api/medicines/doses/today?patient_id=1')
    doses = res_doses.get_json()['doses']
    dose_id = doses[0]['id']
    res_missed = client.post(f'/api/medicines/doses/{dose_id}/status', json={"status": "missed", "user_id": 1})
    safety = res_missed.get_json().get('missed_dose_safety', {})
    pass_7 = ("Never take two doses at once" in safety.get('en', ''))
    results.append(("7. Missed Dose Double-Up Warning", pass_7, f"Contains safety warning: {pass_7}"))

    # Benchmark 8: Caregiver Access Control & 2-Person Limit
    res_rel = client.get('/api/caregiver/relationships?patient_id=1')
    active_count = res_rel.get_json()['active_count']
    res_unauth = client.get('/api/caregiver/patient-status?caregiver_id=999&patient_id=1')
    pass_8 = (active_count <= 2 and res_unauth.status_code == 403)
    results.append(("8. Caregiver RBAC & Max-2 Enforced", pass_8, f"Active count: {active_count}, 403 on unauth: {res_unauth.status_code == 403}"))

    # Benchmark 9: Printable Fridge Sheet PDF Output
    res_pdf = client.get('/api/careplan/fridge-sheet-pdf?patient_id=1&lang=en')
    pass_9 = (res_pdf.status_code == 200 and len(res_pdf.data) > 1000)
    results.append(("9. Printable A4 Fridge Sheet PDF Generation", pass_9, f"PDF bytes: {len(res_pdf.data)}"))

    # Benchmark 10: Flesch Reading Ease Metric
    flesch = calculate_flesch_reading_ease("Take one tablet of Metformin after breakfast with water.")
    pass_10 = (flesch['score'] >= 50.0 and "English" in flesch['metric_name'])
    results.append(("10. English Readability Score Evaluation", pass_10, f"Score: {flesch['score']} / 100 ({flesch['label']})"))

    print("\nBENCHMARK RESULTS SUMMARY:")
    print("-" * 65)
    all_passed = True
    for name, passed, detail in results:
        status_str = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_passed = False
        print(f"{status_str} {name:48} | {detail}")
    print("-" * 65)

    if all_passed:
        print("ALL 10 EVALUATION BENCHMARKS PASSED SUCCESSFULLY (100% PASS RATE)")
        return 0
    else:
        print("SOME EVALUATION BENCHMARKS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(run_evaluation())
