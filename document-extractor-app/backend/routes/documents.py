"""
Document management routes
"""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from storage import storage
from models import Document
from extractor import DocumentExtractor
import os
import logging
from datetime import datetime

bp = Blueprint('documents', __name__, url_prefix='/api/documents')

# Set up logger
logger = logging.getLogger(__name__)


def allowed_file(filename: str, allowed_extensions: list) -> bool:
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in [e.lower() for e in allowed_extensions]


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def secure_file_path(filename: str, upload_folder: str) -> str:
    """Create secure file path"""
    return os.path.join(upload_folder, filename)


def ensure_upload_folder(upload_folder: str):
    """Ensure upload folder exists"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)


def process_document(document_id: str, file_path: str, file_type: str) -> Document:
    """
    Process a document: extract data using LLM and store in memory
    Returns the updated document
    """
    try:
        logger.info(f"Starting processing for document {document_id}")
        
        # Update status to processing
        storage.update_document(document_id, {
            'status': 'processing'
        })
        
        # Initialize extractor with OpenAI
        openai_api_key = os.getenv('OPENAI_API_KEY')
        openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        if not openai_api_key:
            raise Exception("OPENAI_API_KEY environment variable is not set")
        extractor = DocumentExtractor(openai_api_key, openai_model)
        
        # Extract data from document
        extracted_data = extractor.extract_document_data(file_path, file_type)
        logger.info(f"Extracted data for document {document_id}")
        
        # Generate a simple sales order ID based on invoice number or document ID
        invoice_number = extracted_data.get('sales_order_header', {}).get('invoice_number', '')
        sales_order_id = invoice_number if invoice_number else f"SO-{document_id}"
        
        # Store extracted data in memory only
        storage.update_document(document_id, {
            'sales_order_header_id': sales_order_id,
            'extracted_data': extracted_data,
            'status': 'completed',
            'processed_at': datetime.utcnow().isoformat()
        })
        
        logger.info(f"Processing completed for document {document_id}, sales_order_id: {sales_order_id}")
        
        # Get updated document
        updated_doc = storage.get_document(document_id)
        return updated_doc
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
        # Update document status to error
        storage.update_document(document_id, {
            'status': 'error',
            'error_message': str(e),
            'processed_at': datetime.utcnow().isoformat()
        })
        return storage.get_document(document_id)


@bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process one or more documents"""
    try:
        # Check if files are present (support both 'file' and 'files' for backward compatibility)
        files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
        elif 'file' in request.files:
            files = [request.files['file']]
        else:
            return jsonify({'error': 'No files provided'}), 400
        
        # Filter out empty files
        files = [f for f in files if f.filename != '']
        
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        
        # Validate and process all files
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', [])
        max_size = current_app.config.get('MAX_FILE_SIZE', 10485760)  # 10MB default
        upload_folder = current_app.config.get('UPLOAD_FOLDER', './uploads')
        ensure_upload_folder(upload_folder)
        
        documents = []
        
        for file in files:
            # Validate file
            if not allowed_file(file.filename, allowed_extensions):
                error_doc = _create_error_document(
                    file.filename,
                    f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
                )
                documents.append(error_doc)
                continue
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > max_size:
                error_doc = _create_error_document(
                    file.filename,
                    f'File too large. Maximum size: {max_size / 1024 / 1024:.1f}MB'
                )
                documents.append(error_doc)
                continue
            
            # Save file
            file_extension = get_file_extension(file.filename)
            secure_name = secure_filename(file.filename)
            file_path = secure_file_path(secure_name, upload_folder)
            
            # Ensure unique filename
            base_name = os.path.splitext(secure_name)[0]
            counter = 1
            while os.path.exists(file_path):
                secure_name = f"{base_name}_{counter}.{file_extension}"
                file_path = secure_file_path(secure_name, upload_folder)
                counter += 1
            
            file.save(file_path)
            logger.info(f"File saved to {file_path}")
            
            # Create document record with 'uploaded' status initially
            document = Document({
                'id': '0',  # Will be set by storage to incremental ID
                'filename': file.filename,
                'file_path': file_path,
                'file_type': file_extension,
                'file_size': file_size,
                'status': 'uploaded',
                'uploaded_at': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Creating document record for file: {file.filename}")
            created_doc = storage.create_document(document)
            logger.info(f"Document {created_doc.id} created successfully. Starting synchronous processing.")
            
            try:
                # Synchronous processing
                logger.info(f"Calling process_document for document {created_doc.id}, file_path: {file_path}, file_type: {file_extension}")
                processed_doc = process_document(created_doc.id, file_path, file_extension)
                logger.info(f"Processing completed for document {processed_doc.id}, status: {processed_doc.status}")
            except Exception as proc_error:
                logger.error(f"Exception during processing for document {created_doc.id}: {str(proc_error)}", exc_info=True)
                # Update document with error status
                storage.update_document(created_doc.id, {
                    'status': 'error',
                    'error_message': str(proc_error),
                    'processed_at': datetime.utcnow().isoformat()
                })
                processed_doc = storage.get_document(created_doc.id)
            
            logger.info(f"Appending result for document {processed_doc.id}: status={processed_doc.status}, sales_order_id={processed_doc.sales_order_header_id}")
            documents.append({
                'document_id': processed_doc.id,
                'filename': processed_doc.filename,
                'status': processed_doc.status,
                'error': processed_doc.error_message,
                'sales_order_header_id': processed_doc.sales_order_header_id
            })
        
        # Return response - if single file, return single document format for backward compatibility
        if len(documents) == 1:
            result = {
                'document_id': documents[0]['document_id'],
                'status': documents[0]['status'],
                'sales_order_header_id': documents[0].get('sales_order_header_id')
            }
            if documents[0].get('error'):
                result['error'] = documents[0]['error']
            return jsonify(result), 200
        else:
            return jsonify({
                'documents': documents,
                'total_files': len(documents)
            }), 200
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['GET'])
def list_documents():
    """List all documents"""
    try:
        documents = storage.list_documents()
        
        result_docs = []
        for doc in documents:
            # Extract invoice_number from extracted_data if sales_order_header_id is not set
            invoice_number = None
            if not doc.sales_order_header_id and doc.extracted_data:
                invoice_number = doc.extracted_data.get('sales_order_header', {}).get('invoice_number')
            
            # Use invoice_number as sales_order_header_id if available
            sales_order_id = doc.sales_order_header_id or invoice_number
            
            result_docs.append({
                'id': doc.id,
                'filename': doc.filename,
                'uploaded_at': doc.uploaded_at,
                'status': doc.status,
                'sales_order_header_id': sales_order_id,
                'invoice_number': invoice_number,  # Include for frontend fallback
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'processed_at': doc.processed_at,
                'error_message': doc.error_message
            })
        
        return jsonify({
            'documents': result_docs
        }), 200
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/<document_id>/status', methods=['GET'])
def get_document_status(document_id: str):
    """Get document processing status - accepts either document ID or sales order ID"""
    try:
        logger.info(f"Getting status for ID: {document_id}")
        
        document = _find_document_by_id(document_id)
        
        if not document:
            logger.warning(f"Document not found for ID: {document_id}")
            return jsonify({'error': 'Document not found'}), 404
        
        logger.info(f"Document {document.id} status: {document.status}, Sales Order ID: {document.sales_order_header_id}")
        return jsonify({
            'document_id': document.id,
            'status': document.status,
            'filename': document.filename,
            'file_path': document.file_path,
            'file_type': document.file_type,
            'extracted_data': document.extracted_data if document.status == 'completed' else None,
            'error': document.error_message if document.status == 'error' else None,
            'error_message': document.error_message if document.status == 'error' else None,
            'sales_order_header_id': document.sales_order_header_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting document status for {document_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/<document_id>/data', methods=['GET'])
def get_document_data(document_id: str):
    """Get extracted data for a document - accepts either document ID or sales order ID"""
    try:
        logger.info(f"Getting data for ID: {document_id}")
        
        document = _find_document_by_id(document_id)
        
        if not document:
            logger.warning(f"Document not found for ID: {document_id}")
            return jsonify({'error': 'Document not found'}), 404
        
        if document.status != 'completed':
            return jsonify({
                'document_id': document.id,
                'status': document.status,
                'error': document.error_message if document.status == 'error' else 'Document processing not completed'
            }), 200
        
        # Return extracted_data if available
        if document.extracted_data:
            return jsonify({
                'document_id': document.id,
                'sales_order_header_id': document.sales_order_header_id,
                'extracted_data': document.extracted_data
            }), 200
        
        # If no extracted data available
        return jsonify({
            'document_id': document.id,
            'status': document.status,
            'error': 'No extracted data available'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting document data for {document_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def _find_document_by_id(document_id: str):
    """Helper function to find document by sales order ID or document ID"""
    # First try to find by sales order ID
    document = storage.get_document_by_sales_order_id(document_id)
    # If not found, try document ID
    if not document:
        document = storage.get_document(document_id)
    return document


def _create_error_document(filename: str, error_message: str) -> dict:
    """Helper function to create an error document response"""
    doc = Document({
        'id': '0',
        'filename': filename,
        'status': 'error',
        'error_message': error_message,
        'uploaded_at': datetime.utcnow().isoformat()
    })
    storage.create_document(doc)
    return {
        'document_id': doc.id,
        'filename': doc.filename,
        'status': doc.status,
        'error': doc.error_message
    }
