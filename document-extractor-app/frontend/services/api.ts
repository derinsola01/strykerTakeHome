/**
 * API Service Layer
 * Handles all API calls to the backend
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4200/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Document upload (one or more files)
  uploadDocuments: async (files: File[]) => {
    if (files.length === 0) {
      throw new Error('No files provided');
    }
    
    const formData = new FormData();
    // Always use 'files' array for consistency
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    const response = await apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000, // 5 minutes timeout for LLM processing
    });
    return response.data;
  },

  // List all documents
  listDocuments: async () => {
    const response = await apiClient.get('/documents');
    return response.data;
  },

  // Get document status - accepts either document ID or sales order ID
  getDocumentStatus: async (id: string) => {
    try {
      const response = await apiClient.get(`/documents/${id}/status`);
      return response.data;
    } catch (error: any) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        throw new Error('Document not found');
      }
      throw error;
    }
  },

  // Get document data - accepts either document ID or sales order ID
  getDocumentData: async (id: string) => {
    try {
      const response = await apiClient.get(`/documents/${id}/data`);
      return response.data;
    } catch (error: any) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        throw new Error('Document not found');
      }
      throw error;
    }
  },
};

export default api;
