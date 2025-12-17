"""
In-memory storage for documents
"""
from typing import Dict, Optional, List
from models import Document
import threading


class DocumentStorage:
    """Thread-safe in-memory storage for documents"""
    
    def __init__(self):
        self._documents: Dict[str, Document] = {}
        self._lock = threading.RLock()  # Use reentrant lock to avoid deadlock
        self._next_id = 1  # Incremental ID counter
    
    def _get_next_id(self) -> int:
        """Get next incremental document ID (must be called while holding lock)"""
        # Don't acquire lock here - caller should already have it
        current_id = self._next_id
        self._next_id += 1
        return current_id
    
    def create_document(self, document: Document) -> Document:
        """Create a new document"""
        with self._lock:
            # Assign incremental ID if not set
            if not document.id or document.id == '0':
                document.id = str(self._get_next_id())
            self._documents[document.id] = document
            return document
    
    def get_document(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        with self._lock:
            return self._documents.get(document_id)
    
    def update_document(self, document_id: str, updates: Dict) -> Optional[Document]:
        """Update document fields"""
        with self._lock:
            if document_id not in self._documents:
                return None
            doc = self._documents[document_id]
            for key, value in updates.items():
                if hasattr(doc, key):
                    setattr(doc, key, value)
            return doc
    
    def list_documents(self) -> List[Document]:
        """List all documents"""
        with self._lock:
            return list(self._documents.values())
    
    def get_document_by_sales_order_id(self, sales_order_header_id: str) -> Optional[Document]:
        """Get document by sales order header ID"""
        with self._lock:
            for doc in self._documents.values():
                if doc.sales_order_header_id == sales_order_header_id:
                    return doc
            return None


# Global storage instance
storage = DocumentStorage()
