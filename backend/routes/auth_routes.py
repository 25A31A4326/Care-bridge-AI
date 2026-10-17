import hashlib
from flask import Blueprint, request, jsonify, session
from backend.database.db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
        
    pw_hash = hash_pw(password)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, pw_hash))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401
            
        user_dict = dict(user)
        # Fetch profile if patient
        profile = None
        if user_dict['role'] == 'patient':
            cursor.execute("SELECT * FROM patient_profiles WHERE user_id = ?", (user_dict['id'],))
            p = cursor.fetchone()
            if p:
                profile = dict(p)
                
        user_dict.pop('password_hash', None)
        return jsonify({
            "message": "Login successful",
            "user": user_dict,
            "profile": profile
        })

@auth_bp.route('/switch_demo_user', methods=['POST'])
def switch_demo_user():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        user_dict = dict(user)
        profile = None
        if user_dict['role'] == 'patient':
            cursor.execute("SELECT * FROM patient_profiles WHERE user_id = ?", (user_dict['id'],))
            p = cursor.fetchone()
            if p:
                profile = dict(p)
                
        user_dict.pop('password_hash', None)
        return jsonify({
            "message": "Switched demo user",
            "user": user_dict,
            "profile": profile
        })

@auth_bp.route('/demo_users', methods=['GET'])
def get_demo_users():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.role, u.language_preference,
                   p.full_name, p.age, p.emergency_contact, p.medical_notes
            FROM users u
            LEFT JOIN patient_profiles p ON u.id = p.user_id
        """)
        users = [dict(r) for r in cursor.fetchall()]
        return jsonify({"users": users})

@auth_bp.route('/language', methods=['POST'])
def set_language():
    data = request.get_json() or {}
    user_id = data.get('user_id', 1)
    lang = data.get('language', 'te')
    
    if lang not in ['te', 'en']:
        return jsonify({"error": "Supported languages are 'te' and 'en'"}), 400
        
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET language_preference = ? WHERE id = ?", (lang, user_id))
        
    return jsonify({"message": "Language updated", "language": lang})
