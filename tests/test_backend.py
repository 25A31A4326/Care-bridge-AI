import unittest
import json
import io
from backend.app import create_app
from backend.database.db import init_db
from backend.database.seed_data import seed_database
from backend.services.readability_service import calculate_flesch_reading_ease, validate_instructions_against_source

class CareBridgeBackendTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_01_health_check(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('CareBridge AI', data['app_name'])

    def test_02_bilingual_chat_assistant(self):
        # Test English question about next medicine
        res_en = self.client.post('/api/chat/send', json={
            "patient_id": 1,
            "content": "What is my next medicine reminder?",
            "language": "en"
        })
        self.assertEqual(res_en.status_code, 200)
        data_en = res_en.get_json()
        self.assertIn("assistant_message", data_en)
        self.assertTrue(len(data_en["assistant_message"]["content_en"]) > 0)

        # Test Telugu question about appointment
        res_te = self.client.post('/api/chat/send', json={
            "patient_id": 1,
            "content": "నా తదుపరి డాక్టర్ అపాయింట్‌మెంట్ ఎప్పుడు?",
            "language": "te"
        })
        self.assertEqual(res_te.status_code, 200)
        data_te = res_te.get_json()
        self.assertIn("assistant_message", data_te)
        self.assertTrue(len(data_te["assistant_message"]["content_te"]) > 0)

    def test_03_prescription_upload_and_extraction(self):
        sample_rx = """CITY CARE HOSPITAL
Rx:
1. Tab Metformin 500mg - 1 tablet twice daily after meals (08:30 AM, 08:30 PM) for 30 days.
2. Tab Telmisartan 40mg - 1 tablet once daily in the morning (08:30 AM) for 30 days.
Diet: Low salt and low sugar.
Follow-up: 02-Nov-2026."""
        
        data = {
            'file': (io.BytesIO(sample_rx.encode('utf-8')), 'test_prescription.txt'),
            'patient_id': 1,
            'upload_type': 'prescription'
        }
        res = self.client.post('/api/documents/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 200)
        resp_data = res.get_json()
        self.assertEqual(resp_data['status'], 'success')
        self.assertTrue(len(resp_data['structured_items']) >= 2)
        self.assertIn('simple_explanation_en', resp_data)
        self.assertIn('simple_explanation_te', resp_data)

    def test_04_blurry_and_missing_dose_handling(self):
        # Patient 2 (Ramana Rao) has a blurry handwritten prescription
        res = self.client.get('/api/documents/2')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()['document']
        self.assertEqual(data['status'], 'needs_verification')
        self.assertEqual(data['quality_assessment'], 'blurry')
        
        # Check structured instructions flag needs_verification
        unverified_items = [it for it in data['structured_instructions'] if it['status'] == 'needs_verification']
        self.assertTrue(len(unverified_items) > 0)

    def test_05_conflicting_instructions_handling(self):
        # Patient 3 (Sunitha Reddy) has conflicting antibiotic duration
        res = self.client.get('/api/documents/3')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()['document']
        self.assertEqual(data['quality_assessment'], 'conflicting')
        conflicts = [it for it in data['structured_instructions'] if it['status'] == 'conflicting']
        self.assertTrue(len(conflicts) > 0)

    def test_06_unverified_schedule_prevention(self):
        # Attempting to schedule without verification must be rejected
        res = self.client.post('/api/medicines/schedule', json={
            "patient_id": 1,
            "medicine_name": "UnverifiedMed",
            "dose": "1 tab",
            "frequency": "daily",
            "exact_times": ["09:00"],
            "is_verified": 0
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("verified", res.get_json()['error'].lower())

    def test_07_dose_tracking_and_missed_safety(self):
        # Get today's doses
        res = self.client.get('/api/medicines/doses/today?patient_id=1')
        self.assertEqual(res.status_code, 200)
        doses = res.get_json()['doses']
        self.assertTrue(len(doses) > 0)
        
        dose_id = doses[0]['id']
        # Mark as taken
        res_taken = self.client.post(f'/api/medicines/doses/{dose_id}/status', json={"status": "taken", "user_id": 1})
        self.assertEqual(res_taken.status_code, 200)
        
        # Mark as missed - verify safety advice is returned (never double dose!)
        res_missed = self.client.post(f'/api/medicines/doses/{dose_id}/status', json={"status": "missed", "user_id": 1})
        self.assertEqual(res_missed.status_code, 200)
        safety = res_missed.get_json()['missed_dose_safety']
        self.assertIn("Never take two doses at once", safety['en'])
        self.assertIn("రెండు మాత్రలు కలిపి", safety['te'])

    def test_08_caregiver_access_and_limit(self):
        # Check caregiver authorization limits (max 2)
        res_rel = self.client.get('/api/caregiver/relationships?patient_id=1')
        self.assertEqual(res_rel.status_code, 200)
        self.assertLessEqual(res_rel.get_json()['active_count'], 2)
        
        # Unauthorized caregiver access test
        res_unauth = self.client.get('/api/caregiver/patient-status?caregiver_id=999&patient_id=1')
        self.assertEqual(res_unauth.status_code, 403)

        # Authorized caregiver access test (Ramesh caregiver_id=4)
        res_auth = self.client.get('/api/caregiver/patient-status?caregiver_id=4&patient_id=1')
        self.assertEqual(res_auth.status_code, 200)
        self.assertIn('schedules', res_auth.get_json())

    def test_09_fridge_sheet_pdf(self):
        res = self.client.get('/api/careplan/fridge-sheet-pdf?patient_id=1&lang=en')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('Content-Type'), 'application/pdf')
        self.assertGreater(len(res.data), 1000)

    def test_10_readability_metric(self):
        simple_text = "Take one tablet of Metformin after your morning meal. Drink one glass of water."
        score_info = calculate_flesch_reading_ease(simple_text)
        self.assertGreater(score_info['score'], 60.0)
        self.assertIn("Flesch Reading Ease", score_info['metric_name'])

if __name__ == '__main__':
    unittest.main()
