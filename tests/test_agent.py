"""
Automated tests for the Claims Processing Agent.
"""
import pytest
import os
from pathlib import Path
from src.agent import ClaimsProcessingAgent
from src.extractor import FieldExtractor
from src.validator import FieldValidator
from src.router import ClaimRouter


@pytest.fixture
def agent():
    """Create a test agent instance."""
    # Skip if no API key
    if not os.getenv('GEMINI_API_KEY'):
        pytest.skip("GEMINI_API_KEY not set")
    return ClaimsProcessingAgent()


@pytest.fixture
def sample_dir():
    """Get sample documents directory."""
    return Path(__file__).parent.parent / "sample_documents"


def test_validator_missing_fields():
    """Test field validation."""
    validator = FieldValidator()
    
    # Complete data
    complete_data = {
        "policyNumber": "POL-123",
        "policyholderName": "John Doe",
        "effectiveDates": {"start": "2023-01-01", "end": "2024-01-01"},
        "incidentDate": "2023-06-15",
        "incidentTime": "14:30",
        "incidentLocation": "123 Main St",
        "incidentDescription": "Accident",
        "claimantName": "John Doe",
        "assetType": "Vehicle",
        "assetId": "VIN123",
        "estimatedDamage": 15000,
        "claimType": "Auto"
    }
    
    missing = validator.validate(complete_data)
    assert len(missing) == 0, "Should have no missing fields"
    
    # Incomplete data
    incomplete_data = {
        "policyNumber": "POL-123",
        "policyholderName": None,
    }
    
    missing = validator.validate(incomplete_data)
    assert len(missing) > 0, "Should have missing fields"


def test_router_fast_track():
    """Test fast-track routing."""
    router = ClaimRouter()
    
    fields = {
        "estimatedDamage": 15000,
        "incidentDescription": "Normal accident",
        "claimType": "Auto"
    }
    
    route, reasoning = router.route_claim(fields, [])
    assert route == router.ROUTE_FAST_TRACK
    assert "fast-track" in reasoning.lower()


def test_router_high_value():
    """Test high-value claim routing."""
    router = ClaimRouter()
    
    fields = {
        "estimatedDamage": 50000,
        "incidentDescription": "Severe damage",
        "claimType": "Property"
    }
    
    route, reasoning = router.route_claim(fields, [])
    assert route == router.ROUTE_MANUAL_REVIEW
    assert "exceeds" in reasoning.lower()


def test_router_fraud():
    """Test fraud detection routing."""
    router = ClaimRouter()
    
    fields = {
        "estimatedDamage": 10000,
        "incidentDescription": "The damage seems staged and inconsistent",
        "claimType": "Auto"
    }
    
    route, reasoning = router.route_claim(fields, [])
    assert route == router.ROUTE_INVESTIGATION
    assert "fraud" in reasoning.lower() or "investigation" in reasoning.lower()


def test_router_injury():
    """Test injury claim routing."""
    router = ClaimRouter()
    
    fields = {
        "estimatedDamage": 15000,
        "incidentDescription": "Accident with bodily injury",
        "claimType": "Personal Injury"
    }
    
    route, reasoning = router.route_claim(fields, [])
    assert route == router.ROUTE_SPECIALIST
    assert "injury" in reasoning.lower()


def test_router_missing_fields():
    """Test missing fields routing."""
    router = ClaimRouter()
    
    fields = {
        "estimatedDamage": 10000
    }
    
    missing_fields = ["policyNumber", "policyholderName"]
    
    route, reasoning = router.route_claim(fields, missing_fields)
    assert route == router.ROUTE_MANUAL_REVIEW
    assert "missing" in reasoning.lower()


def test_sample_claim_001(agent, sample_dir):
    """Test processing of sample claim 001 (fast-track)."""
    claim_file = sample_dir / "claim_001.txt"
    
    if not claim_file.exists():
        pytest.skip("Sample file not found")
    
    result = agent.process_claim(str(claim_file))
    
    assert "extractedFields" in result
    assert "missingFields" in result
    assert "recommendedRoute" in result
    assert "reasoning" in result
    
    # Should be fast-track
    assert result["recommendedRoute"] == "Fast-track"


def test_sample_claim_002(agent, sample_dir):
    """Test processing of sample claim 002 (high-value)."""
    claim_file = sample_dir / "claim_002.txt"
    
    if not claim_file.exists():
        pytest.skip("Sample file not found")
    
    result = agent.process_claim(str(claim_file))
    
    # Should be manual review due to high value
    assert result["recommendedRoute"] == "Manual Review"


def test_sample_claim_003(agent, sample_dir):
    """Test processing of sample claim 003 (fraud indicators)."""
    claim_file = sample_dir / "claim_003.txt"
    
    if not claim_file.exists():
        pytest.skip("Sample file not found")
    
    result = agent.process_claim(str(claim_file))
    
    # Should be investigation flag
    assert result["recommendedRoute"] == "Investigation Flag"


def test_sample_claim_004(agent, sample_dir):
    """Test processing of sample claim 004 (injury)."""
    claim_file = sample_dir / "claim_004.txt"
    
    if not claim_file.exists():
        pytest.skip("Sample file not found")
    
    result = agent.process_claim(str(claim_file))
    
    # Should be specialist queue
    assert result["recommendedRoute"] == "Specialist Queue"


def test_sample_claim_005(agent, sample_dir):
    """Test processing of sample claim 005 (missing fields)."""
    claim_file = sample_dir / "claim_005.txt"
    
    if not claim_file.exists():
        pytest.skip("Sample file not found")
    
    result = agent.process_claim(str(claim_file))
    
    # Should have missing fields
    assert len(result["missingFields"]) > 0
    
    # Should be manual review
    assert result["recommendedRoute"] == "Manual Review"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
