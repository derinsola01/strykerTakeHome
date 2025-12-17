"""
Data Models for Document Extraction Application
"""
from datetime import datetime
from typing import Optional, Dict


class Document:
    """Model for tracking uploaded documents"""
    
    def __init__(self, data: Optional[Dict] = None):
        self.id = data.get('id', '0') if data else '0'  # Will be set by storage
        self.filename = data.get('filename', '') if data else ''
        self.file_path = data.get('file_path', '') if data else ''
        self.file_type = data.get('file_type', '') if data else ''
        self.file_size = data.get('file_size', 0) if data else 0
        self.status = data.get('status', 'uploaded') if data else 'uploaded'
        self.uploaded_at = data.get('uploaded_at', datetime.utcnow().isoformat()) if data else datetime.utcnow().isoformat()
        self.processed_at = data.get('processed_at', None) if data else None
        self.error_message = data.get('error_message', None) if data else None
        self.extracted_data = data.get('extracted_data', None) if data else None
        self.sales_order_header_id = data.get('sales_order_header_id', None) if data else None
    
