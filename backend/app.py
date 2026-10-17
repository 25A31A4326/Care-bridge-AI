import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.config import Config
from backend.database.db import init_db
from backend.database.seed_data import seed_database
from backend.routes.auth_routes import auth_bp
from backend.routes.chat_routes import chat_bp
from backend.routes.document_routes import document_bp
from backend.routes.medicine_routes import medicine_bp
from backend.routes.caregiver_routes import caregiver_bp
from backend.routes.careplan_routes import careplan_bp

def create_app():
    frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))
    app = Flask(__name__, static_folder=frontend_dist, static_url_path='')
    app.config.from_object(Config)
    
    # Ensure upload directory exists
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    # Initialize and seed database if necessary
    try:
        seed_database()
    except Exception as e:
        print("Note on DB initialization:", e)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(medicine_bp)
    app.register_blueprint(caregiver_bp)
    app.register_blueprint(careplan_bp)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "app_name": "CareBridge AI API",
            "tagline": "Your Medicine, Your Language, Your Care",
            "version": "1.0.0",
            "bilingual_support": ["en", "te"],
            "ai_mode": "local-demo (verified safe)" if not Config.GEMINI_API_KEY else "cloud-ai-enabled"
        })

    # Serve React Frontend single-page app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        elif os.path.exists(os.path.join(app.static_folder, 'index.html')):
            return send_from_directory(app.static_folder, 'index.html')
        else:
            return jsonify({
                "message": "CareBridge AI API is active. Frontend build folder not found. Run 'npm run build' in frontend directory.",
                "health": "/api/health"
            })

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "detail": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting CareBridge AI on http://127.0.0.1:{port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
