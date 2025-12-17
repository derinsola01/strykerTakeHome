# Test Data Directory

This directory contains test invoice images for testing the document extraction endpoints.

## Files

### Total Collection: 100 Invoices

**Original Template:**
- `Sales_Invoice.png` - Original invoice template

**Initial Test Invoices (001-005):**
- `invoice_001_INV-001.png` - Acme Corporation invoice
- `invoice_002_INV-002.png` - Tech Solutions Inc invoice
- `invoice_003_INV-003.png` - Global Supplies Co invoice
- `invoice_004_INV-004.png` - Digital Services LLC invoice
- `invoice_005_INV-005.png` - Retail Partners Group invoice

**Phase 6 Sample Invoices (006-100):**
- `invoice_006_INV-006.png` through `invoice_100_INV-100.png` - 95 diverse sample invoices
- See `SAMPLE_INVOICES.md` for detailed documentation

## Test Invoice Details

### Invoice 001 (INV-001)
- **Company**: Acme Corporation
- **Date**: 2024-01-15
- **Items**: 2 line items
- **Subtotal**: $500.00
- **Tax**: $42.50 (8.5%)
- **Total**: $542.50

### Invoice 002 (INV-002)
- **Company**: Tech Solutions Inc
- **Date**: 2024-02-20
- **Items**: 2 line items (services)
- **Subtotal**: $10,000.00
- **Tax**: $725.00 (7.25%)
- **Total**: $10,725.00

### Invoice 003 (INV-003)
- **Company**: Global Supplies Co
- **Date**: 2024-03-10
- **Items**: 3 line items (materials)
- **Subtotal**: $2,137.50
- **Tax**: $146.95 (6.875%)
- **Total**: $2,284.45

### Invoice 004 (INV-004)
- **Company**: Digital Services LLC
- **Date**: 2024-04-05
- **Items**: 3 line items (design services)
- **Subtotal**: $2,750.00
- **Tax**: $0.00 (0%)
- **Total**: $2,750.00

### Invoice 005 (INV-005)
- **Company**: Retail Partners Group
- **Date**: 2024-05-12
- **Items**: 3 line items (retail products)
- **Subtotal**: $2,650.00
- **Tax**: $159.00 (6.0%)
- **Total**: $2,809.00

## Usage

These files can be used to test:

1. **Single File Upload**: Upload one invoice at a time
   ```bash
   curl -X POST http://localhost:4200/api/documents/upload \
     -F "file=@request-data/invoice_001_INV-001.png"
   ```

2. **Batch Upload**: Upload multiple invoices at once
   ```bash
   curl -X POST http://localhost:4200/api/documents/upload/batch \
     -F "files=@request-data/invoice_001_INV-001.png" \
     -F "files=@request-data/invoice_002_INV-002.png" \
     -F "files=@request-data/invoice_003_INV-003.png"
   ```

3. **Frontend Testing**: Use the web interface at http://localhost:3000 to upload these files

## Collection Statistics

- **Total Invoices**: 100 (001-100)
- **File Format**: PNG
- **Average Size**: ~65-75 KB per invoice
- **Total Size**: ~6.5-7.5 MB
- **Date Range**: January 1, 2024 - December 31, 2024
- **Currencies**: 8 different (USD, EUR, GBP, CAD, AUD, JPY, CHF, CNY)
- **Tax Rates**: 13 different rates (0% to 20%)
- **Line Items**: 1-8 items per invoice

For detailed information about invoice diversity and testing scenarios, see `SAMPLE_INVOICES.md`.

