# Sample Invoices Collection

This directory contains 100 sample invoices for testing the document extraction application.

## Invoice Collection

### Total Invoices: 100
- **Invoices 001-005**: Initial test invoices (Phase 2)
- **Invoices 006-100**: Diverse sample invoices (Phase 6)

## Invoice Naming Convention

All invoices follow the pattern: `invoice_{number}_INV-{number}.png`

Examples:
- `invoice_001_INV-001.png`
- `invoice_050_INV-050.png`
- `invoice_100_INV-100.png`

## Invoice Diversity

The sample invoices (006-100) include variations in:

### Layouts & Formats
- Standard invoice layout
- Consistent header structure
- Varied line item counts (1-8 items per invoice)

### Data Variations
- **Dates**: Spread across 2024 (January 1 - December 31)
- **Due Dates**: 15-60 days after invoice date
- **Invoice Numbers**: INV-006 through INV-100
- **Customer IDs**: Random CUST-### format

### Company & Customer Data
- **30+ Company Names**: Various industries (Tech, Manufacturing, Services, etc.)
- **30+ Cities**: Major US cities with zip codes
- **Random Names**: Diverse vendor and customer names
- **Addresses**: Varied street names and numbers

### Financial Variations
- **Currencies**: USD, EUR, GBP, CAD, AUD, JPY, CHF, CNY
- **Tax Rates**: 0%, 5%, 6%, 6.875%, 7%, 7.25%, 8%, 8.5%, 9%, 10%, 12%, 15%, 20%
- **Subtotals**: Range from $50 to $50,000+
- **Line Items**: 1-8 items per invoice
- **Quantities**: 1 to 200+ units
- **Unit Prices**: $5 to $500
- **Shipping**: Sometimes included (0-50)
- **Other Charges**: Sometimes included (0-100)

### Product Variations
- **Product Categories**: Widget, Component, Service, Material, Product, Item, Part, Unit, License, Subscription, Consulting, Implementation, Support, Training, Design, Development, Maintenance, Repair, Installation, Custom
- **Product Types**: Standard, Premium, Professional, Enterprise, Basic, Advanced, Deluxe, Express, Rush, Custom, Bulk, Wholesale, Retail, OEM
- **Units of Measure**: each, unit, piece, box, case, kg, lb, oz, g, hours, days, months, year

### Payment Terms
- Net 30, Net 15, Net 45, Net 60
- Due on receipt
- 2/10 Net 30
- Cash on delivery
- Prepaid
- Monthly, Quarterly
- Sometimes empty

## Testing Scenarios

These invoices can be used to test:

1. **Single File Upload**: Upload individual invoices
2. **Batch Upload**: Upload multiple invoices simultaneously
3. **Extraction Accuracy**: Test LLM extraction with diverse formats
4. **Data Validation**: Test form validation with various data types
5. **Duplicate Handling**: Test with invoices that have same invoice numbers (manually create duplicates)
6. **Currency Handling**: Test with different currencies
7. **Tax Calculations**: Test with various tax rates
8. **Line Item Variations**: Test with different numbers of line items

## Usage Examples

### Single Upload
```bash
curl -X POST http://localhost:4200/api/documents/upload \
  -F "file=@request-data/invoice_050_INV-050.png"
```

### Batch Upload (5 invoices)
```bash
curl -X POST http://localhost:4200/api/documents/upload/batch \
  -F "files=@request-data/invoice_010_INV-010.png" \
  -F "files=@request-data/invoice_020_INV-020.png" \
  -F "files=@request-data/invoice_030_INV-030.png" \
  -F "files=@request-data/invoice_040_INV-040.png" \
  -F "files=@request-data/invoice_050_INV-050.png"
```

### Frontend Testing
Use the web interface at http://localhost:3000 to upload these invoices through the UI.

## File Sizes

Each invoice PNG file is approximately 60-75 KB, resulting in:
- Total size for 100 invoices: ~6-7.5 MB
- Suitable for batch testing and development

## Notes

- All invoices use the same visual template but with varied data
- Dates are randomly distributed across 2024
- Financial amounts are realistic but randomly generated
- Product names and descriptions are varied for testing extraction accuracy
- Some fields may be empty (due_date, payment_terms) to test optional field handling


