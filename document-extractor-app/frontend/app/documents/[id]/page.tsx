'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { DocumentStatus, ExtractedData } from '@/types';

export default function DocumentDetailPage() {
  const params = useParams();
  const documentId = params.id as string;

  // Fetch document status
  const { data: status, isLoading: statusLoading, error: statusError } = useQuery<DocumentStatus>({
    queryKey: ['document-status', documentId],
    queryFn: async () => {
      const response = await api.getDocumentStatus(documentId);
      return response;
    },
    retry: 1,
  });

  // Fetch document data if status is completed
  const { data: documentData, isLoading: dataLoading } = useQuery<{ extracted_data: ExtractedData }>({
    queryKey: ['document-data', documentId],
    queryFn: async () => {
      try {
        // Try to get data from status first
        if (status?.extracted_data) {
          return { extracted_data: status.extracted_data };
        }
        // Otherwise fetch from data endpoint
        const response = await api.getDocumentData(documentId);
        return response;
      } catch (error: any) {
        throw error;
      }
    },
    enabled: status?.status === 'completed' && !!status,
    retry: 1,
  });

  const extractedData = documentData?.extracted_data || status?.extracted_data;
  const header = extractedData?.sales_order_header;
  const details = extractedData?.sales_order_details || [];

  if (statusLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2">Loading document...</span>
          </div>
        </div>
      </div>
    );
  }

  if (statusError || !status) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <h2 className="text-xl font-bold text-red-800 mb-2">Document Not Found</h2>
            <p className="text-red-700 mb-4">
              The requested document could not be found. It may have been deleted or the ID is incorrect.
            </p>
            <Link href="/documents">
              <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                ← Back to Documents
              </button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Document Details</h1>
            <p className="text-gray-600">{status.filename}</p>
          </div>
          <Link href="/documents">
            <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
              ← Back to Documents
            </button>
          </Link>
        </div>

        {/* Status Badge */}
        <div className="mb-6">
          <span
            className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
              status.status === 'completed'
                ? 'bg-green-100 text-green-800'
                : status.status === 'error'
                ? 'bg-red-100 text-red-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}
          >
            {status.status}
          </span>
        </div>

        {/* Error Message */}
        {status.status === 'error' && status.error_message && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 font-semibold">Error:</p>
            <p className="text-red-700">{status.error_message}</p>
          </div>
        )}

        {/* Two Column Layout: Data on Left, Image on Right */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Extracted Data */}
          <div className="bg-white border rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-bold mb-4">Extracted Data</h2>
            
            {status.status === 'completed' && header ? (
              <div className="space-y-6">
                {/* Header Information */}
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-gray-800">Invoice Header</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Invoice Number:</span>
                      <span className="font-medium">{header.invoice_number || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Invoice Date:</span>
                      <span className="font-medium">{header.invoice_date || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Vendor Name:</span>
                      <span className="font-medium">{header.vendor_name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Customer Name:</span>
                      <span className="font-medium">{header.customer_name || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Subtotal:</span>
                      <span className="font-medium">
                        {header.currency || 'USD'} {header.subtotal?.toFixed(2) || '0.00'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tax Amount:</span>
                      <span className="font-medium">
                        {header.currency || 'USD'} {header.tax_amount?.toFixed(2) || '0.00'}
                      </span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="text-gray-600 font-semibold">Total Amount:</span>
                      <span className="font-bold text-lg">
                        {header.currency || 'USD'} {header.total_amount?.toFixed(2) || '0.00'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Line Items */}
                {details && details.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-gray-800">Line Items</h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-3 py-2 text-left">Line</th>
                            <th className="px-3 py-2 text-left">Product</th>
                            <th className="px-3 py-2 text-right">Qty</th>
                            <th className="px-3 py-2 text-right">Unit Price</th>
                            <th className="px-3 py-2 text-right">Total</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y">
                          {details.map((detail: any, idx: number) => (
                            <tr key={idx}>
                              <td className="px-3 py-2">{detail.line_number || idx + 1}</td>
                              <td className="px-3 py-2">{detail.product_name || 'N/A'}</td>
                              <td className="px-3 py-2 text-right">{detail.quantity || '0'}</td>
                              <td className="px-3 py-2 text-right">
                                {header.currency || 'USD'} {detail.unit_price?.toFixed(2) || '0.00'}
                              </td>
                              <td className="px-3 py-2 text-right">
                                {header.currency || 'USD'} {detail.line_total?.toFixed(2) || '0.00'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            ) : status.status === 'completed' && dataLoading ? (
              <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span className="ml-2">Loading extracted data...</span>
              </div>
            ) : (
              <div className="text-gray-500 text-center p-8">
                <p>No extracted data available.</p>
                <p className="text-sm mt-2">Status: {status.status}</p>
              </div>
            )}
          </div>

          {/* Right Column: Document Image */}
          <div className="bg-white border rounded-lg p-6 shadow-sm flex flex-col">
            <h2 className="text-xl font-bold mb-4">Document Image</h2>
            {status.file_path && status.file_type && ['png', 'jpg', 'jpeg'].includes(status.file_type.toLowerCase()) ? (
              <div className="flex-1 flex items-center justify-center">
                <img
                  src={`${process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'http://localhost:4200'}/documents/${documentId}`}
                  alt={`Document: ${status.filename}`}
                  className="max-w-full h-auto rounded-lg shadow-md"
                  style={{ maxHeight: '80vh' }}
                  onError={(e: any) => {
                    // Prevent infinite loop by setting a flag
                    if (e.currentTarget.dataset.error === 'true') {
                      e.currentTarget.style.display = 'none';
                      return;
                    }
                    e.currentTarget.dataset.error = 'true';
                    e.currentTarget.onerror = null;
                  }}
                />
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-500 text-center p-8">
                <div>
                  <p>No image available for this document.</p>
                  <p className="text-sm mt-2">File type: {status.file_type || 'N/A'}</p>
                  {status.file_path && (
                    <p className="text-xs mt-1 text-gray-400">Path: {status.file_path}</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
