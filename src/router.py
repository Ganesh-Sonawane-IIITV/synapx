"""
Claim routing engine that classifies and routes claims based on business rules.
"""
from typing import Dict, Any, Tuple, List
from src.utils import contains_fraud_indicators


class ClaimRouter:
    """Routes claims to appropriate workflows based on business rules."""
    
    # Routing destinations
    ROUTE_FAST_TRACK = "Fast-track"
    ROUTE_MANUAL_REVIEW = "Manual Review"
    ROUTE_INVESTIGATION = "Investigation Flag"
    ROUTE_SPECIALIST = "Specialist Queue"
    
    # Thresholds
    FAST_TRACK_THRESHOLD = 25000  # USD
    
    def route_claim(
        self, 
        extracted_fields: Dict[str, Any], 
        missing_fields: List[str]
    ) -> Tuple[str, str]:
        """
        Determine the appropriate route for a claim based on business rules.
        
        Business Rules (in priority order):
        1. If any mandatory field is missing → Manual Review
        2. If description contains fraud indicators → Investigation Flag
        3. If claim type includes injury → Specialist Queue
        4. If estimated damage < $25,000 → Fast-track
        5. Otherwise → Manual Review
        
        Args:
            extracted_fields: Dictionary of extracted fields
            missing_fields: List of missing field names
            
        Returns:
            Tuple of (route, reasoning)
        """
        reasons = []
        
        # Rule 1: Missing fields → Manual Review
        if missing_fields:
            return (
                self.ROUTE_MANUAL_REVIEW,
                f"Mandatory fields are missing: {', '.join(missing_fields)}. "
                "Claim requires manual review to complete missing information."
            )
        
        # Rule 2: Fraud indicators → Investigation
        description = extracted_fields.get("incidentDescription", "")
        if contains_fraud_indicators(description):
            return (
                self.ROUTE_INVESTIGATION,
                "Incident description contains potential fraud indicators (e.g., 'fraud', 'inconsistent', 'staged'). "
                "Claim flagged for investigation team review."
            )
        
        # Rule 3: Injury claims → Specialist Queue
        claim_type = extracted_fields.get("claimType", "")
        if claim_type and self._is_injury_claim(claim_type, description):
            return (
                self.ROUTE_SPECIALIST,
                "Claim type involves injury or bodily harm. Routing to specialist queue for expert assessment."
            )
        
        # Rule 4: Low-value claims → Fast-track
        estimated_damage = extracted_fields.get("estimatedDamage")
        if estimated_damage is not None:
            if estimated_damage < self.FAST_TRACK_THRESHOLD:
                reasons.append(f"Estimated damage (${estimated_damage:,.2f}) is below the ${self.FAST_TRACK_THRESHOLD:,} threshold for fast-track processing")
                reasons.append("All mandatory fields are present")
                reasons.append("No fraud indicators detected")
                reasons.append("Claim type does not require specialist review")
                
                return (
                    self.ROUTE_FAST_TRACK,
                    ". ".join(reasons) + "."
                )
            else:
                return (
                    self.ROUTE_MANUAL_REVIEW,
                    f"Estimated damage (${estimated_damage:,.2f}) exceeds the ${self.FAST_TRACK_THRESHOLD:,} fast-track threshold. "
                    "High-value claim requires manual review and approval."
                )
        
        # Rule 5: Default → Manual Review
        return (
            self.ROUTE_MANUAL_REVIEW,
            "Unable to determine estimated damage or claim does not meet fast-track criteria. "
            "Routing to manual review for proper assessment."
        )
    
    def _is_injury_claim(self, claim_type: str, description: str) -> bool:
        """
        Check if claim involves injury.
        
        Args:
            claim_type: The claim type field
            description: The incident description
            
        Returns:
            True if claim involves injury
        """
        injury_keywords = [
            "injury", "injured", "bodily harm", "medical", 
            "hospital", "ambulance", "hurt", "pain",
            "personal injury", "bodily injury"
        ]
        
        text_to_check = f"{claim_type} {description}".lower()
        
        return any(keyword in text_to_check for keyword in injury_keywords)
    
    def get_routing_summary(self) -> Dict[str, str]:
        """
        Get a summary of all routing rules.
        
        Returns:
            Dictionary mapping route names to their criteria
        """
        return {
            self.ROUTE_FAST_TRACK: f"Estimated damage < ${self.FAST_TRACK_THRESHOLD:,}, all fields present, no red flags",
            self.ROUTE_MANUAL_REVIEW: "Missing mandatory fields OR high-value claim OR default routing",
            self.ROUTE_INVESTIGATION: "Fraud indicators detected in description",
            self.ROUTE_SPECIALIST: "Claim involves injury or bodily harm",
        }
