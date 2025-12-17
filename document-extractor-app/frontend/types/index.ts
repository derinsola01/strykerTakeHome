/**
 * Shared TypeScript type definitions
 */

export interface Document {
  id: string;
  filename: string;
  uploaded_at: string;
  status: string;
  sales_order_header_id?: string;
  invoice_number?: string;  // Extracted invoice number for fallback display
  file_type?: string;
  file_size?: number;
  processed_at?: string;
  error_message?: string;
}

export interface DocumentStatus {
  document_id: string;
  status: string;
  filename: string;
  file_path?: string;
  file_type?: string;
  extracted_data?: ExtractedData;
  error?: string;
  error_message?: string;
  sales_order_header_id?: string;
}

export interface ExtractedData {
  sales_order_header?: SalesOrderHeader;
  sales_order_details?: SalesOrderDetail[];
}

export interface SalesOrderHeader {
  invoice_number?: string;
  invoice_date?: string;
  vendor_name?: string;
  vendor_address?: string;
  customer_name?: string;
  customer_address?: string;
  subtotal?: number;
  tax_amount?: number;
  total_amount?: number;
  currency?: string;
  payment_terms?: string;
  due_date?: string;
}

export interface SalesOrderDetail {
  line_number?: number;
  product_name?: string;
  product_description?: string;
  quantity?: number;
  unit_price?: number;
  line_total?: number;
  unit_of_measure?: string;
}

export interface FileWithMetadata {
  file: File;
  metadata: {
    id: string;
    status: 'pending' | 'uploading' | 'uploaded' | 'error';
    error?: string;
  };
}

export type UploadStatus = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
