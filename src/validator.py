"""
Field validator for FNOL documents.
"""
from typing import Dict, Any, List


class FieldValidator:
    """Validates extracted fields and identifies missing or invalid data."""
    
    # Define all mandatory fields
    MANDATORY_FIELDS = [
        "policyNumber",
        "policyholderName",
        "effectiveDates.start",
        "effectiveDates.end",
        "incidentDate",
        "incidentTime",
        "incidentLocation",
        "incidentDescription",
        "claimantName",
        "assetType",
        "assetId",
        "estimatedDamage",
        "claimType",
    ]
    
    def validate(self, extracted_fields: Dict[str, Any]) -> List[str]:
        """
        Validate extracted fields and return list of missing fields.
        
        Args:
            extracted_fields: Dictionary of extracted fields
            
        Returns:
            List of missing field names
        """
        missing_fields = []
        
        for field_path in self.MANDATORY_FIELDS:
            if not self._is_field_present(extracted_fields, field_path):
                missing_fields.append(field_path)
        
        return missing_fields
    
    def _is_field_present(self, data: Dict[str, Any], field_path: str) -> bool:
        """
        Check if a field (including nested fields) is present and not empty.
        
        Args:
            data: Dictionary containing the data
            field_path: Dot-separated path to the field (e.g., "effectiveDates.start")
            
        Returns:
            True if field is present and not None/empty
        """
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if not isinstance(current, dict):
                return False
            
            current = current.get(part)
            
            if current is None:
                return False
        
        # Check if value is meaningful
        if isinstance(current, str):
            return bool(current.strip())
        elif isinstance(current, (int, float)):
            return True  # Numbers (including 0) are valid
        elif isinstance(current, list):
            return len(current) > 0
        elif isinstance(current, dict):
            return len(current) > 0
        
        return current is not None
    
    def get_field_name_display(self, field_path: str) -> str:
        """
        Convert field path to human-readable name.
        
        Args:
            field_path: Dot-separated field path
            
        Returns:
            Human-readable field name
        """
        replacements = {
            "policyNumber": "Policy Number",
            "policyholderName": "Policyholder Name",
            "effectiveDates.start": "Policy Start Date",
            "effectiveDates.end": "Policy End Date",
            "incidentDate": "Incident Date",
            "incidentTime": "Incident Time",
            "incidentLocation": "Incident Location",
            "incidentDescription": "Incident Description",
            "claimantName": "Claimant Name",
            "claimantContact": "Claimant Contact",
            "assetType": "Asset Type",
            "assetId": "Asset ID",
            "estimatedDamage": "Estimated Damage",
            "claimType": "Claim Type",
            "attachments": "Attachments",
            "initialEstimate": "Initial Estimate",
        }
        
        return replacements.get(field_path, field_path)
