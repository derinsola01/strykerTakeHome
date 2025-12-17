# Document Extractor Application

## Quick Start

To run the application, use Docker Compose:

```bash
docker-compose up -d
```

This command will:
- Build both backend and frontend Docker images
- Start all services in detached mode
- Set up all required dependencies automatically

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:4200/api

To stop the application:
```bash
docker-compose down
```

To view logs:
```bash
docker-compose logs -f
```

---

## Overview

This is a full-stack document extraction application that uses AI (OpenAI GPT-4o-mini) to extract structured data from invoice documents. The application supports multiple file formats (PDF, PNG, JPG, JPEG, TXT) and provides a web interface for uploading documents and viewing extracted data.

## Features

- **Document Upload**: Upload single or multiple documents via drag-and-drop or file selection
- **AI-Powered Extraction**: Automatically extracts structured data (invoice numbers, dates, vendor/customer info, line items, totals) using OpenAI's vision API
- **Real-time Status Updates**: View document processing status with automatic refresh
- **Document Management**: Browse all uploaded documents with status tracking
- **Data Visualization**: View extracted data alongside the original document image

## Architecture

### Backend (`/backend`)
- **Framework**: Flask (Python 3.11)
- **LLM Provider**: OpenAI GPT-4o-mini
- **Storage**: In-memory storage (documents stored in `/uploads` folder)
- **API**: RESTful API with endpoints for document upload, status, and data retrieval

### Frontend (`/frontend`)
- **Framework**: Next.js 14 with React 18
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Type Safety**: TypeScript

## Project Structure

```
document-extractor-app/
├── backend/                 # Flask backend application
│   ├── app.py             # Flask app entry point
│   ├── extractor.py       # Document extraction logic using OpenAI
│   ├── models.py          # Data models
│   ├── storage.py         # In-memory document storage
│   ├── routes/            # API route handlers
│   │   ├── documents.py   # Document endpoints
│   │   └── health.py      # Health check endpoint
│   └── requirements.txt   # Python dependencies
├── frontend/              # Next.js frontend application
│   ├── app/              # Next.js app router pages
│   │   ├── home/         # Upload page
│   │   └── documents/    # Documents list and detail pages
│   ├── components/       # React components
│   ├── services/         # API service layer
│   ├── types/            # TypeScript type definitions
│   └── utils/            # Utility functions
├── request-data/          # Test invoice files (see Testing section)
├── uploads/              # Uploaded documents storage
└── docker-compose.yml     # Docker Compose configuration
```

## API Endpoints

### Health Check
- `GET /api/health` - Check backend health status

### Documents
- `POST /api/documents/upload` - Upload one or more documents
- `GET /api/documents` - List all documents
- `GET /api/documents/<id>/status` - Get document processing status
- `GET /api/documents/<id>/data` - Get extracted data for a document
- `GET /documents/<id>` - Serve document file (image/PDF)

## Environment Variables

### Backend
- `OPENAI_API_KEY` - OpenAI API key (required)
- `OPENAI_MODEL` - OpenAI model to use (default: `gpt-4o-mini`)
- `UPLOAD_FOLDER` - Path to upload directory (default: `./uploads`)
- `MAX_FILE_SIZE` - Maximum file size in bytes (default: `10485760` = 10MB)
- `ALLOWED_EXTENSIONS` - Comma-separated list of allowed file extensions
- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: `http://localhost:4200/api`)

## Testing

The `request-data/` folder contains sample invoice files (PNG images) that can be used to test the application. These files include:
- 100 sample invoice images (`invoice_001_INV-001.png` through `invoice_100_INV-100.png`)
- A sample sales invoice (`Sales_Invoice.png`)

To test the application:
1. Start the application using `docker-compose up -d`
2. Navigate to http://localhost:3000/home
3. Upload files from the `request-data/` folder
4. View extracted data on the documents page

## Development

### Prerequisites
- Docker and Docker Compose
- (Optional) Node.js 20+ and Python 3.11+ for local development

### Running Locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY=your_api_key_here
python app.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Building Docker Images

```bash
# Build backend
docker-compose build backend

# Build frontend
docker-compose build frontend

# Build all
docker-compose build
```

## Data Flow

1. **Upload**: User uploads document(s) via the web interface
2. **Storage**: Files are saved to the `/uploads` directory
3. **Processing**: Backend sends file to OpenAI API for extraction
4. **Extraction**: AI extracts structured data (invoice header and line items)
5. **Storage**: Extracted data is stored in memory with the document record
6. **Display**: Frontend displays extracted data and document image

## Extracted Data Structure

The application extracts the following structured data:

**Sales Order Header:**
- Invoice number
- Invoice date
- Vendor name and address
- Customer name and address
- Subtotal, tax amount, total amount
- Currency
- Payment terms
- Due date

**Sales Order Details (Line Items):**
- Line number
- Product name and description
- Quantity
- Unit price
- Line total
- Unit of measure

## Notes

- Documents are stored in memory and persist only while the backend is running
- Uploaded files are saved to the `/uploads` directory
- The application uses incremental numerical IDs for documents and sales orders
- Processing is synchronous - the upload endpoint waits for extraction to complete
- The Sales Order ID displayed in the documents list is the extracted invoice number

## Troubleshooting

**Backend not starting:**
- Check that `OPENAI_API_KEY` is set in `docker-compose.yml`
- Verify Docker containers are running: `docker-compose ps`
- Check logs: `docker-compose logs backend`

**Frontend not connecting to backend:**
- Verify `NEXT_PUBLIC_API_URL` matches backend URL
- Check CORS settings in backend
- Ensure backend health check passes: `curl http://localhost:4200/api/health`

**File upload fails:**
- Check file size (max 10MB)
- Verify file type is allowed (PDF, PNG, JPG, JPEG, TXT)
- Check backend logs for extraction errors

## Additional Documentation

For detailed information on scaling the application for production use, handling higher volumes, and supporting additional document types, see [SCALING_STRATEGIES.md](./document-extractor-app/SCALING_STRATEGIES.md).

This document covers:
- Asynchronous processing and queue-based architectures
- Horizontal scaling strategies
- Database integration and persistence
- Additional document type support
- Production deployment strategies
- Performance optimizations
- Cost optimization techniques
- Monitoring and observability
- Security enhancements

## License

This project is for demonstration purposes.
