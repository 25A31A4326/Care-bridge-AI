from flask import Blueprint, request, jsonify
from backend.database.db import get_db
from backend.services.ai_service import ask_ai_assistant

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    patient_id = request.args.get('patient_id', default=1, type=int)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Ensure conversation exists
        cursor.execute("SELECT id FROM conversations WHERE patient_id = ? ORDER BY id DESC LIMIT 1", (patient_id,))
        conv = cursor.fetchone()
        if not conv:
            cursor.execute("INSERT INTO conversations (patient_id, title) VALUES (?, ?)", (patient_id, f"Patient {patient_id} Chat"))
            conv_id = cursor.lastrowid
        else:
            conv_id = conv['id']
            
        cursor.execute("""
            SELECT id, sender_role, message_type, content_en, content_te, source_document_id, metadata_json, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """, (conv_id,))
        
        messages = [dict(r) for r in cursor.fetchall()]
        return jsonify({"conversation_id": conv_id, "messages": messages})

@chat_bp.route('/send', methods=['POST'])
def send_message():
    data = request.get_json() or {}
    patient_id = data.get('patient_id', 1)
    content = data.get('content', '').strip()
    lang = data.get('language', 'te')
    is_voice = data.get('is_voice', False)
    
    if not content:
        return jsonify({"error": "Message content cannot be empty"}), 400
        
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM conversations WHERE patient_id = ? ORDER BY id DESC LIMIT 1", (patient_id,))
        conv = cursor.fetchone()
        if not conv:
            cursor.execute("INSERT INTO conversations (patient_id, title) VALUES (?, ?)", (patient_id, f"Patient {patient_id} Chat"))
            conv_id = cursor.lastrowid
        else:
            conv_id = conv['id']
            
        # Store user message
        content_en = content if lang == 'en' else ""
        content_te = content if lang == 'te' else ""
        meta_json = '{"voice_input": true}' if is_voice else None
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, sender_role, message_type, content_en, content_te, metadata_json)
            VALUES (?, 'user', 'text', ?, ?, ?)
        """, (conv_id, content_en or content, content_te or content, meta_json))
        user_msg_id = cursor.lastrowid

    # Call AI Assistant
    ai_response = ask_ai_assistant(content, patient_id, lang)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (conversation_id, sender_role, message_type, content_en, content_te)
            VALUES (?, 'assistant', 'text', ?, ?)
        """, (conv_id, ai_response.get('en', ''), ai_response.get('te', '')))
        bot_msg_id = cursor.lastrowid
        
    return jsonify({
        "status": "success",
        "user_message": {
            "id": user_msg_id,
            "sender_role": "user",
            "content_en": content_en or content,
            "content_te": content_te or content
        },
        "assistant_message": {
            "id": bot_msg_id,
            "sender_role": "assistant",
            "content_en": ai_response.get('en', ''),
            "content_te": ai_response.get('te', '')
        }
    })

@chat_bp.route('/clear', methods=['POST'])
def clear_chat():
    data = request.get_json() or {}
    patient_id = data.get('patient_id', 1)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM conversations WHERE patient_id = ?", (patient_id,))
        convs = cursor.fetchall()
        for c in convs:
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (c['id'],))
            
    return jsonify({"message": "Conversation history cleared"})
