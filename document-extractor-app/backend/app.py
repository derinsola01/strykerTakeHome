"""
Flask Application Entry Point
"""
from flask import Flask
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, origins=cors_origins)

# App configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')
app.config['MAX_FILE_SIZE'] = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB
app.config['ALLOWED_EXTENSIONS'] = os.getenv('ALLOWED_EXTENSIONS', 'pdf,png,jpg,jpeg,txt').split(',')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register blueprints
from routes.health import bp as health_bp
from routes.documents import bp as documents_bp

app.register_blueprint(health_bp, url_prefix='/api')
app.register_blueprint(documents_bp, url_prefix='/api/documents')

# Register document file serving route at /documents/<id>
from storage import storage
from flask import send_from_directory, jsonify

@app.route('/documents/<id>', methods=['GET'])
def serve_document_file(id: str):
    """Serve the document file at /documents/<id> - accepts document ID or sales order ID"""
    try:
        # Find document by sales order ID or document ID
        document = storage.get_document_by_sales_order_id(id) or storage.get_document(id)
        
        if not document:
            logger.warning(f"Document not found for ID: {id}")
            return jsonify({'error': 'Document not found'}), 404
        
        if not document.file_path or not os.path.exists(document.file_path):
            logger.warning(f"File not found for document {document.id}: {document.file_path}")
            return jsonify({'error': 'File not found'}), 404
        
        upload_folder = os.path.dirname(document.file_path)
        filename = os.path.basename(document.file_path)
        
        logger.info(f"Serving file {filename} for document {document.id} (sales_order_id: {document.sales_order_header_id})")
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        logger.error(f"Error serving file for ID {id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
