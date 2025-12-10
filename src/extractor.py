"""
AI-powered field extraction using Google Gemini with DeepSeek OCR fallback.
"""
import os
import json
import requests
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Google Gemini (may not be available)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class PatternBasedExtractor:
    """Fallback extractor using local pattern matching and regex."""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize pattern-based extractor.
        
        Args:
            api_url: Deprecated, kept for compatibility
        """
        pass
    
    def extract_fields_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract fields from a document file using local text extraction + pattern parsing.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing extracted fields
        """
        from src.utils import read_document
        
        try:
            # Read the document text locally (PDF or TXT)
            document_text = read_document(file_path)
            
            # Use local pattern matching
            return self._parse_text_to_fields(document_text)
                
        except Exception as e:
            raise Exception(f"Local extraction failed: {str(e)}")
    
    def extract_fields(self, document_text: str) -> Dict[str, Any]:
        """
        Extract fields from already-extracted document text.
        
        Args:
            document_text: Text content from document
            
        Returns:
            Dictionary containing extracted fields
        """
        return self._parse_text_to_fields(document_text)
    
    def _parse_text_to_fields(self, text: str) -> Dict[str, Any]:
        """
        Parse text to extract structured fields using pattern matching.
        
        Args:
            text: Document text
            
        Returns:
            Dictionary of extracted fields
        """
        import re
        from src.utils import parse_currency, normalize_date
        
        fields = {
            "policyNumber": None,
            "policyholderName": None,
            "effectiveDates": {"start": None, "end": None},
            "incidentDate": None,
            "incidentTime": None,
            "incidentLocation": None,
            "incidentDescription": None,
            "claimantName": None,
            "claimantContact": None,
            "thirdParties": [],
            "assetType": None,
            "assetId": None,
            "estimatedDamage": None,
            "claimType": None,
            "attachments": [],
            "initialEstimate": None,
        }
        
        # Extract policy number
        policy_match = re.search(r'Policy Number:?\s*([A-Z0-9\-]+)', text, re.IGNORECASE)
        if policy_match:
            fields["policyNumber"] = policy_match.group(1)
        
        # Extract policyholder name
        holder_match = re.search(r'Policyholder Name:?\s*([A-Za-z\s]+?)(?:\n|Policy)', text, re.IGNORECASE)
        if holder_match:
            fields["policyholderName"] = holder_match.group(1).strip()
        
        # Extract effective dates
        dates_match = re.search(r'Effective Dates?:?\s*([A-Za-z0-9,\s\-]+?)\s+to\s+([A-Za-z0-9,\s\-]+)', text, re.IGNORECASE)
        if dates_match:
            fields["effectiveDates"]["start"] = normalize_date(dates_match.group(1))
            fields["effectiveDates"]["end"] = normalize_date(dates_match.group(2))
        
        # Extract incident date
        inc_date_match = re.search(r'(?:Date of Incident|Incident Date):?\s*([A-Za-z0-9,\s\-]+)', text, re.IGNORECASE)
        if inc_date_match:
            fields["incidentDate"] = normalize_date(inc_date_match.group(1))
        
        # Extract incident time
        time_match = re.search(r'(?:Time of Incident|Incident Time):?\s*(\d{1,2}:\d{2})', text, re.IGNORECASE)
        if time_match:
            fields["incidentTime"] = time_match.group(1)
        
        # Extract location
        loc_match = re.search(r'Location:?\s*([^\n]+)', text, re.IGNORECASE)
        if loc_match:
            fields["incidentLocation"] = loc_match.group(1).strip()
        
        # Extract description
        desc_match = re.search(r'Description:?\s*([^\n]+(?:\n(?![A-Z][A-Z\s]+:)[^\n]+)*)', text, re.IGNORECASE)
        if desc_match:
            fields["incidentDescription"] = desc_match.group(1).strip()
        
        # Extract claimant
        claimant_match = re.search(r'Claimant:?\s*([A-Za-z\s]+?)(?:\n|Contact)', text, re.IGNORECASE)
        if claimant_match:
            fields["claimantName"] = claimant_match.group(1).strip()
        
        # Extract contact
        contact_match = re.search(r'(?:Claimant )?Contact:?\s*([\+\d\-\s()]+)', text, re.IGNORECASE)
        if contact_match:
            fields["claimantContact"] = contact_match.group(1).strip()
        
        # Extract asset type
        asset_match = re.search(r'Asset Type:?\s*([A-Za-z\s]+?)(?:\n|Make)', text, re.IGNORECASE)
        if asset_match:
            fields["assetType"] = asset_match.group(1).strip()
        
        # Extract asset ID (VIN or address)
        vin_match = re.search(r'VIN:?\s*([A-Z0-9]+)', text, re.IGNORECASE)
        if vin_match:
            fields["assetId"] = f"VIN: {vin_match.group(1)}"
        
        # Extract estimated damage
        damage_match = re.search(r'Estimated Damage:?\s*\$?([\d,\.]+)', text, re.IGNORECASE)
        if damage_match:
            fields["estimatedDamage"] = parse_currency(damage_match.group(1))
            fields["initialEstimate"] = fields["estimatedDamage"]
        
        # Extract claim type
        type_match = re.search(r'Claim Type:?\s*([A-Za-z\s\-]+?)(?:\n|Date)', text, re.IGNORECASE)
        if type_match:
            fields["claimType"] = type_match.group(1).strip()
        
        # Extract attachments
        attachments_section = re.search(r'ATTACHMENTS?\s*-+\s*(.*?)(?:\n\n|ADDITIONAL|$)', text, re.IGNORECASE | re.DOTALL)
        if attachments_section:
            attachment_lines = attachments_section.group(1).strip().split('\n')
            fields["attachments"] = [
                re.sub(r'^\d+\.\s*', '', line.strip()) 
                for line in attachment_lines 
                if line.strip() and not line.strip().startswith('---')
            ]
        
        return fields


class FieldExtractor:
    """Extracts structured fields from FNOL documents using AI with automatic fallback."""
    
    def __init__(self, api_key: Optional[str] = None, use_fallback: bool = True):
        """
        Initialize the field extractor with automatic fallback.
        
        Args:
            api_key: Google Gemini API key (optional, will use env variable if not provided)
            use_fallback: Whether to use pattern-based fallback (default: True)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.use_fallback = use_fallback
        self.gemini_available = False
        self.model = None
        
        # Try to initialize Gemini
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.gemini_available = True
                print("✅ Gemini API initialized successfully")
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {str(e)}")
                if self.use_fallback:
                    print("📦 Will use pattern-based extraction as fallback")
                else:
                    raise ValueError(
                        "GEMINI_API_KEY invalid or Gemini unavailable.\n"
                        "Get your free API key from: https://makersuite.google.com/app/apikey"
                    )
        elif self.use_fallback:
            print("⚠️  Gemini API key not configured")
            print("📦 Using pattern-based extraction")
        else:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in your .env file or pass it as an argument.\n"
                "Get your free API key from: https://makersuite.google.com/app/apikey"
            )
        
        # Initialize fallback extractor
        if self.use_fallback:
            self.fallback_extractor = PatternBasedExtractor()
    
    def extract_fields(self, document_text: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured fields from FNOL document text with automatic fallback.
        
        Args:
            document_text: Raw text from the FNOL document
            file_path: Optional path to the original file (for DeepSeek OCR)
            
        Returns:
            Dictionary containing extracted fields
        """
        # Try Gemini first if available
        if self.gemini_available:
            print("🤖 Using Gemini AI for extraction...")
            try:
                return self._extract_with_gemini(document_text)
            except Exception as e:
                print(f"⚠️  Gemini extraction failed: {str(e)}")
                if self.use_fallback:
                    print("📦 Falling back to DeepSeek OCR...")
                else:
                    raise Exception(f"Error during field extraction: {str(e)}")
        
        # Use pattern-based fallback
        if self.use_fallback:
            print("🔄 Using pattern-based extraction...")
            try:
                # If we have a file path, use it directly for better extraction
                if file_path:
                    return self.fallback_extractor.extract_fields_from_file(file_path)
                else:
                    # Otherwise parse the text we have
                    return self.fallback_extractor.extract_fields(document_text)
            except Exception as e:
                raise Exception(f"Both Gemini and pattern-based extraction failed: {str(e)}")
        
        raise Exception("No extraction method available")
    
    def _extract_with_gemini(self, document_text: str) -> Dict[str, Any]:
        """Extract fields using Gemini AI."""
        prompt = self._create_extraction_prompt(document_text)
        
        response = self.model.generate_content(prompt)
        result = self._parse_response(response.text)
        return result
    
    def _create_extraction_prompt(self, document_text: str) -> str:
        """Create a detailed prompt for field extraction."""
        return f"""You are an insurance claims processing AI. Extract the following fields from the FNOL (First Notice of Loss) document below.

Return your response as valid JSON with this exact structure:

{{
  "policyNumber": "string or null",
  "policyholderName": "string or null",
  "effectiveDates": {{
    "start": "YYYY-MM-DD or null",
    "end": "YYYY-MM-DD or null"
  }},
  "incidentDate": "YYYY-MM-DD or null",
  "incidentTime": "HH:MM or null",
  "incidentLocation": "string or null",
  "incidentDescription": "string or null",
  "claimantName": "string or null",
  "claimantContact": "string or null",
  "thirdParties": ["list of names or empty array"],
  "assetType": "string or null (e.g., Vehicle, Property, etc.)",
  "assetId": "string or null (e.g., VIN, address, etc.)",
  "estimatedDamage": number or null,
  "claimType": "string or null (e.g., Auto, Property, Injury, etc.)",
  "attachments": ["list of attachment names or empty array"],
  "initialEstimate": number or null
}}

IMPORTANT INSTRUCTIONS:
1. Extract only factual information present in the document
2. Use null for missing fields
3. Convert dates to YYYY-MM-DD format
4. Convert currency amounts to numbers (remove $ and commas)
5. Return ONLY valid JSON, no additional text or explanation
6. If incident description mentions injury or bodily harm, ensure claimType reflects this

FNOL DOCUMENT:
{document_text}

JSON OUTPUT:"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response and extract JSON."""
        try:
            # Try to find JSON in the response
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                # Remove first and last lines (``` markers)
                response_text = '\n'.join(lines[1:-1])
                if response_text.startswith('json'):
                    response_text = '\n'.join(response_text.split('\n')[1:])
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Ensure all expected fields exist
            result = self._normalize_extracted_fields(result)
            
            return result
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}\nResponse: {response_text}")
    
    def _normalize_extracted_fields(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all expected fields exist in the extracted data."""
        normalized = {
            "policyNumber": fields.get("policyNumber"),
            "policyholderName": fields.get("policyholderName"),
            "effectiveDates": fields.get("effectiveDates", {}),
            "incidentDate": fields.get("incidentDate"),
            "incidentTime": fields.get("incidentTime"),
            "incidentLocation": fields.get("incidentLocation"),
            "incidentDescription": fields.get("incidentDescription"),
            "claimantName": fields.get("claimantName"),
            "claimantContact": fields.get("claimantContact"),
            "thirdParties": fields.get("thirdParties", []),
            "assetType": fields.get("assetType"),
            "assetId": fields.get("assetId"),
            "estimatedDamage": fields.get("estimatedDamage"),
            "claimType": fields.get("claimType"),
            "attachments": fields.get("attachments", []),
            "initialEstimate": fields.get("initialEstimate"),
        }
        
        # Ensure effectiveDates has correct structure
        if not isinstance(normalized["effectiveDates"], dict):
            normalized["effectiveDates"] = {}
        
        if "start" not in normalized["effectiveDates"]:
            normalized["effectiveDates"]["start"] = None
        if "end" not in normalized["effectiveDates"]:
            normalized["effectiveDates"]["end"] = None
        
        return normalized
