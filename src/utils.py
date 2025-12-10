"""
Utility functions for the claims processing agent.
"""
import os
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
import PyPDF2


def read_document(file_path: str) -> str:
    """
    Read content from a document (PDF or TXT).
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Extracted text content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document not found: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return read_pdf(file_path)
    elif file_extension in ['.txt', '.text']:
        return read_text(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def read_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    
    return text.strip()


def read_text(file_path: str) -> str:
    """Read text from a TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        raise Exception(f"Error reading text file: {str(e)}")


def parse_currency(value: Any) -> Optional[float]:
    """
    Parse a currency value from various formats.
    
    Examples:
        "$25,000" -> 25000.0
        "25000" -> 25000.0
        "25,000.50" -> 25000.5
    """
    if value is None:
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,\s]', '', value)
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    return None


def format_output(result: Dict[str, Any], pretty: bool = True) -> str:
    """
    Format the output as JSON.
    
    Args:
        result: Result dictionary
        pretty: Whether to pretty-print the JSON
        
    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(result, indent=2, ensure_ascii=False)
    return json.dumps(result, ensure_ascii=False)


def save_output(result: Dict[str, Any], output_path: str) -> None:
    """
    Save the result to a JSON file.
    
    Args:
        result: Result dictionary
        output_path: Path to save the output
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def extract_number_from_text(text: str) -> Optional[float]:
    """Extract a numeric value from text."""
    if not text:
        return None
    
    # Look for numbers (with optional decimals and commas)
    match = re.search(r'[\d,]+\.?\d*', str(text))
    if match:
        return parse_currency(match.group())
    
    return None


def normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize date string to YYYY-MM-DD format.
    
    Handles various date formats:
        - 06/15/2023
        - June 15, 2023
        - 15-06-2023
        - 2023-06-15
    """
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    # Try different date formats
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d-%m-%Y",
        "%m-%d-%Y",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return date_str  # Return as-is if no format matches


def get_fraud_indicators() -> list:
    """Return list of fraud indicator keywords."""
    return [
        "fraud",
        "fraudulent",
        "inconsistent",
        "staged",
        "suspicious",
        "fabricated",
        "false claim",
        "deceptive"
    ]


def contains_fraud_indicators(text: str) -> bool:
    """Check if text contains fraud indicator keywords."""
    if not text:
        return False
    
    text_lower = text.lower()
    indicators = get_fraud_indicators()
    
    return any(indicator in text_lower for indicator in indicators)
