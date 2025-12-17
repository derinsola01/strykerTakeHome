"""
Document Data Extractor using OpenAI API
Direct file processing with vision capabilities
"""
import os
import base64
import json
import re
import logging
from typing import Dict, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

# Extraction prompt for LLM
EXTRACTION_PROMPT = """
You are an expert at extracting structured data from invoice documents. 

Look carefully at the invoice image provided and extract the ACTUAL values shown in the document. Do NOT use placeholder or example values. Extract the REAL data from the image.

Extract the following information from this invoice document and return it as JSON:

SalesOrderHeader:
- invoice_number: The ACTUAL invoice number or ID shown in the document (e.g., "INV-001", "INV-002", etc.)
- invoice_date: The ACTUAL date shown in YYYY-MM-DD format (extract from the document, not a placeholder)
- vendor_name: The ACTUAL name of the vendor/supplier shown in the document
- vendor_address: The ACTUAL full address of vendor shown in the document
- customer_name: The ACTUAL name of the customer/buyer shown in the document
- customer_address: The ACTUAL full address of customer shown in the document
- subtotal: The ACTUAL subtotal amount before tax shown in the document (as a number, not a string)
- tax_amount: The ACTUAL tax amount shown in the document (as a number, not a string)
- total_amount: The ACTUAL total amount due shown in the document (as a number, not a string)
- currency: Currency code shown (e.g., USD, EUR) or default to USD if not specified
- payment_terms: Payment terms if mentioned in the document
- due_date: Due date in YYYY-MM-DD format if available in the document

SalesOrderDetail (array of line items):
- line_number: Sequential line number (1, 2, 3, etc.)
- product_name: The ACTUAL name or description of the product/service shown in the document
- product_description: Detailed description if available in the document
- quantity: The ACTUAL quantity shown in the document (as a number)
- unit_price: The ACTUAL price per unit shown in the document (as a number)
- line_total: The ACTUAL total for this line item shown in the document (as a number)
- unit_of_measure: Unit of measure shown (e.g., "each", "kg", "hours") or leave empty if not specified

IMPORTANT: 
- Read the ACTUAL values from the invoice image. Do NOT make up or use placeholder values.
- Extract EXACTLY what is shown in the document.
- If a field is not visible in the document, use null or empty string, NOT a placeholder value.
- All monetary amounts should be numbers (not strings with currency symbols).

Return ONLY complete and valid JSON in this exact format, ensuring all braces and brackets are properly closed:
{
  "sales_order_header": { ... },
  "sales_order_details": [ ... ]
}
"""


class DocumentExtractor:
    """Extract structured data from documents using OpenAI API"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        # Initialize OpenAI client with explicit configuration
        self.client = OpenAI(
            api_key=api_key,
            timeout=300.0,  # 5 minutes timeout
            max_retries=2
        )
        self.model = model
    
    def extract_document_data(self, file_path: str, file_type: str) -> Dict:
        """
        Extract data from document file
        Directly processes file with OpenAI Vision API
        """
        try:
            logger.info(f"Extracting data from {file_path} (type: {file_type})")
            logger.info(f"Using OpenAI model: {self.model}")
            
            # Prepare file content for OpenAI
            if file_type.lower() in ['png', 'jpg', 'jpeg']:
                # For images, read and encode as base64
                logger.info(f"Reading image file: {file_path}")
                with open(file_path, 'rb') as f:
                    image_bytes = f.read()
                    logger.info(f"Image file size: {len(image_bytes)} bytes")
                    image_data = base64.b64encode(image_bytes).decode('utf-8')
                    logger.info(f"Base64 encoded size: {len(image_data)} characters")
                
                # Use OpenAI Vision API
                extracted_data = self._extract_openai_vision(image_data, file_type)
                logger.info(f"Received response from OpenAI, length: {len(extracted_data) if extracted_data else 0}")
            elif file_type.lower() == 'pdf':
                # For PDFs, read content and pass to OpenAI
                # Note: OpenAI can handle PDFs directly
                with open(file_path, 'rb') as f:
                    pdf_bytes = f.read()
                    pdf_data = base64.b64encode(pdf_bytes).decode('utf-8')
                extracted_data = self._extract_openai_vision(pdf_data, 'pdf')
            elif file_type.lower() == 'txt':
                # For text files, read content directly
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
                extracted_data = self._extract_openai_text(text_content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Parse and validate extracted data
            parsed_data = self.parse_llm_response(extracted_data)
            logger.info(f"Successfully extracted data from {file_path}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error extracting data from {file_path}: {str(e)}", exc_info=True)
            raise
    
    def _extract_openai_vision(self, image_data: str, file_type: str) -> str:
        """Extract data using OpenAI Vision API"""
        try:
            logger.info(f"Calling OpenAI Vision API with model {self.model}")
            
            # Determine MIME type
            mime_type_map = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'pdf': 'application/pdf'
            }
            mime_type = mime_type_map.get(file_type.lower(), 'image/png')
            
            # Prepare the prompt
            full_prompt = f"{EXTRACTION_PROMPT}\n\nLook at the invoice image carefully and extract the ACTUAL values shown. Read the invoice number, dates, names, addresses, and amounts directly from the image. Do not use example or placeholder values."
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": full_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.0  # Low temperature for accurate extraction
            )
            
            logger.info(f"OpenAI API response received")
            extracted_text = response.choices[0].message.content
            logger.info(f"OpenAI response preview (first 500 chars): {extracted_text[:500]}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _extract_openai_text(self, text_content: str) -> str:
        """Extract data using OpenAI text API"""
        try:
            logger.info(f"Calling OpenAI text API with model {self.model}")
            
            prompt = f"{EXTRACTION_PROMPT}\n\nExtract invoice data from the following text:\n\n{text_content}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4096,
                temperature=0.0
            )
            
            logger.info(f"OpenAI API response received")
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}", exc_info=True)
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def parse_llm_response(self, response_text: str) -> Dict:
        """
        Parse JSON from LLM response
        Handles cases where LLM wraps JSON in markdown code blocks or adds extra text
        Also handles truncated/incomplete JSON responses
        """
        if not response_text or not response_text.strip():
            raise ValueError("Empty LLM response")

        # Clean up the response text
        response_text = response_text.strip()

        try:
            # Try direct JSON parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object in the text (non-greedy to avoid matching too much)
        json_match = re.search(r'\{.*?\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Try to find the start of JSON and attempt to fix incomplete JSON
        json_start = response_text.find('{')
        if json_start != -1:
            json_candidate = response_text[json_start:]

            # Try to fix common truncation issues
            if json_candidate.count('{') > json_candidate.count('}'):
                # Missing closing braces
                missing_braces = json_candidate.count('{') - json_candidate.count('}')
                # Try to find the last complete object/array and close it
                for attempt in range(missing_braces):
                    try:
                        fixed_json = json_candidate + '}' * (missing_braces - attempt)
                        return json.loads(fixed_json)
                    except json.JSONDecodeError:
                        continue

            # Try parsing what we have
            try:
                return json.loads(json_candidate)
            except json.JSONDecodeError as e:
                # If it's a truncation error, try to extract what we can
                if 'Expecting' in str(e) or 'Unterminated' in str(e):
                    # Try to extract a valid partial structure
                    brace_count = 0
                    last_valid_pos = -1
                    for i, char in enumerate(json_candidate):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                last_valid_pos = i
                                break

                    if last_valid_pos > 0:
                        partial_json = json_candidate[:last_valid_pos + 1]
                        try:
                            parsed = json.loads(partial_json)
                            # Ensure we have the required structure
                            if 'sales_order_header' in parsed:
                                if 'sales_order_details' not in parsed:
                                    parsed['sales_order_details'] = []
                                return parsed
                        except json.JSONDecodeError:
                            pass

        # Last resort: try to extract and fix the JSON manually
        header_match = re.search(r'"sales_order_header"\s*:\s*\{[^}]*\}', response_text, re.DOTALL)
        if header_match:
            try:
                header_str = header_match.group(0)
                minimal_json = '{' + header_str + ', "sales_order_details": []}'
                return json.loads(minimal_json)
            except json.JSONDecodeError:
                pass

        # If all else fails, raise error with more context
        error_preview = response_text[:500] if len(response_text) > 500 else response_text
        raise ValueError(f"Could not parse JSON from LLM response. Response preview: {error_preview}")
