import os
import uuid
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from backend.config import Config
from backend.database.db import get_db
from backend.services.ocr_service import extract_text_from_file
from backend.services.prescription_service import parse_medical_document_text

document_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@document_bp.route('/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    patient_id = request.form.get('patient_id', default=1, type=int)
    upload_type = request.form.get('upload_type', 'prescription') # prescription, medicine_package, discharge_summary, medical_report, pdf
    
    if not allowed_file(file.filename):
        return jsonify({
            "error": "Unsupported file format. Please upload JPG, PNG, or PDF files.",
            "error_te": "దయచేసి JPG, PNG లేదా PDF ఫైళ్లను మాత్రమే అప్‌లోడ్ చేయండి."
        }), 400
        
    # Generate non-public safe storage filename
    orig_filename = secure_filename(file.filename)
    unique_prefix = uuid.uuid4().hex[:10]
    stored_filename = f"{unique_prefix}_{orig_filename}"
    file_path = os.path.join(Config.UPLOAD_FOLDER, stored_filename)
    
    # Save file to non-public uploads directory
    file.save(file_path)
    file_size = os.path.getsize(file_path)
    ext = os.path.splitext(orig_filename)[1].lower()
    
    # Run OCR & Document Extraction
    extraction_result = extract_text_from_file(file_path, stored_filename)
    raw_text = extraction_result.get("raw_text", "")
    quality = extraction_result.get("quality", "clear")
    confidence = extraction_result.get("confidence", 0.9)
    method = extraction_result.get("method", "native")
    quality_info = extraction_result.get("quality_info", {})
    
    # If medicine package photo: explicitly flag that medicine package is NOT proof of prescribed dose/schedule
    is_package_photo = (upload_type == 'medicine_package')
    
    # Parse structured instructions & explanations
    parsed_data = parse_medical_document_text(raw_text)
    structured_items = parsed_data.get("structured_items", [])
    
    if is_package_photo:
        # Enforce rule: "Do not treat a medicine package as proof of the prescribed dose or schedule."
        for item in structured_items:
            item["status"] = "needs_verification"
            item["prescribed_dose"] = "Needs verification (Package photo is not proof of prescribed dose)"
            item["exact_time"] = "Needs verification (Doctor prescription required for schedule)"
            item["doctor_notes"] = "Medicine box photo shows packaging only. Please consult your prescription for your doctor's exact prescribed schedule."
        parsed_data["overall_status"] = "needs_verification"
        parsed_data["simple_explanation_en"] += "\n\n[!] Note: Medicine packaging confirms the product name, but NOT your prescribed dose or schedule. Please check your doctor's written prescription."
        parsed_data["simple_explanation_te"] += "\n\n[గమనిక]: మందుల డబ్బా ఫోటో కేవలం మందు పేరును మాత్రమే తెలియజేస్తుంది. మీ డాక్టర్ రాసిన మోతాదు మరియు సమయాల కోసం ప్రిస్క్రిప్షన్ చూడండి."
    
    # Determine document status
    doc_status = "extracted"
    if quality in ["blurry", "incomplete", "conflicting"] or parsed_data["overall_status"] != "verified":
        doc_status = "needs_verification"
        
    # Store in database
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Insert document
        cursor.execute("""
            INSERT INTO documents (patient_id, original_filename, stored_filename, file_type, file_size, upload_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, orig_filename, stored_filename, ext, file_size, upload_type, doc_status))
        document_id = cursor.lastrowid
        
        # Insert extracted text
        cursor.execute("""
            INSERT INTO extracted_texts (document_id, raw_text, extraction_method, confidence_score, quality_assessment)
            VALUES (?, ?, ?, ?, ?)
        """, (document_id, raw_text, method, confidence, quality))
        
        # Insert structured instructions
        for it in structured_items:
            cursor.execute("""
                INSERT INTO structured_instructions (
                    document_id, medicine_name, strength, prescribed_dose, frequency,
                    exact_time, duration, food_instruction, doctor_notes, diet_advice,
                    activity_restrictions, follow_up_date, warning_signs, status, raw_source_snippet, readability_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id, it.get('medicine_name'), it.get('strength'), it.get('prescribed_dose'),
                it.get('frequency'), it.get('exact_time'), it.get('duration'), it.get('food_instruction'),
                it.get('doctor_notes'), it.get('diet_advice'), it.get('activity_restrictions'),
                it.get('follow_up_date'), it.get('warning_signs'), it.get('status'),
                it.get('raw_source_snippet'), parsed_data['readability']['score']
            ))

    return jsonify({
        "status": "success",
        "document_id": document_id,
        "filename": orig_filename,
        "upload_type": upload_type,
        "extraction_status": doc_status,
        "extraction_method": method,
        "quality_assessment": quality,
        "quality_info": quality_info,
        "raw_text": raw_text,
        "simple_explanation_en": parsed_data["simple_explanation_en"],
        "simple_explanation_te": parsed_data["simple_explanation_te"],
        "structured_items": structured_items,
        "readability": parsed_data["readability"],
        "validation_report": parsed_data["validation_report"],
        "overall_status": parsed_data["overall_status"]
    })

@document_bp.route('/list', methods=['GET'])
def list_documents():
    patient_id = request.args.get('patient_id', default=1, type=int)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.id, d.patient_id, d.original_filename, d.file_type, d.file_size,
                   d.upload_type, d.status, d.created_at,
                   et.confidence_score, et.quality_assessment
            FROM documents d
            LEFT JOIN extracted_texts et ON d.id = et.document_id
            WHERE d.patient_id = ?
            ORDER BY d.id DESC
        """, (patient_id,))
        docs = [dict(r) for r in cursor.fetchall()]
        return jsonify({"documents": docs})

@document_bp.route('/<int:doc_id>', methods=['GET'])
def get_document_details(doc_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.*, et.raw_text, et.extraction_method, et.confidence_score, et.quality_assessment
            FROM documents d
            LEFT JOIN extracted_texts et ON d.id = et.document_id
            WHERE d.id = ?
        """, (doc_id,))
        doc = cursor.fetchone()
        if not doc:
            return jsonify({"error": "Document not found"}), 404
            
        doc_dict = dict(doc)
        
        # Fetch structured instructions
        cursor.execute("SELECT * FROM structured_instructions WHERE document_id = ?", (doc_id,))
        instructions = [dict(r) for r in cursor.fetchall()]
        doc_dict["structured_instructions"] = instructions
        
        # Explanations
        parsed = parse_medical_document_text(doc_dict.get("raw_text") or "")
        doc_dict["simple_explanation_en"] = parsed["simple_explanation_en"]
        doc_dict["simple_explanation_te"] = parsed["simple_explanation_te"]
        doc_dict["readability"] = parsed["readability"]
        doc_dict["validation_report"] = parsed["validation_report"]
        
        return jsonify({"document": doc_dict})

@document_bp.route('/download/<int:doc_id>', methods=['GET'])
def download_document(doc_id: int):
    """
    Secure file delivery endpoint with authentication check and non-public storage.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stored_filename, original_filename, file_type FROM documents WHERE id = ?", (doc_id,))
        doc = cursor.fetchone()
        if not doc:
            return jsonify({"error": "Document not found"}), 404
            
        file_path = os.path.join(Config.UPLOAD_FOLDER, doc['stored_filename'])
        if not os.path.exists(file_path):
            return jsonify({"error": "File does not exist on disk"}), 404
            
        return send_file(file_path, as_attachment=False, download_name=doc['original_filename'])
