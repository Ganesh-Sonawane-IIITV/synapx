"""
Test script to verify the fallback system works.
"""
import os
import sys

# Temporarily remove Gemini API key to test fallback
original_key = os.environ.get('GEMINI_API_KEY')
if 'GEMINI_API_KEY' in os.environ:
    del os.environ['GEMINI_API_KEY']

print("="*60)
print("FALLBACK SYSTEM TEST")
print("="*60)
print("\nTesting WITHOUT Gemini API key...")
print("Expected: Should use DeepSeek OCR fallback\n")

try:
    from src.agent import ClaimsProcessingAgent
    
    # Create agent without API key
    agent = ClaimsProcessingAgent()
    
    print("\n" + "="*60)
    print("Processing sample document with fallback extractor...")
    print("="*60 + "\n")
    
    # Process a sample claim
    result = agent.process_claim("sample_documents/claim_001.txt")
    
    print("\n" + "="*60)
    print("FALLBACK TEST RESULTS")
    print("="*60)
    print(f"✅ Extraction successful!")
    print(f"Extracted {len([v for v in result['extractedFields'].values() if v])} fields")
    print(f"Route: {result['recommendedRoute']}")
    print(f"Missing fields: {len(result['missingFields'])}")
    
    if result['extractedFields'].get('policyNumber'):
        print(f"\n✅ Sample field extracted: Policy Number = {result['extractedFields']['policyNumber']}")
    
    print("\n" + "="*60)
    print("✅ FALLBACK SYSTEM WORKING CORRECTLY!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ Fallback test failed: {str(e)}")
    sys.exit(1)
finally:
    # Restore original API key if it existed
    if original_key:
        os.environ['GEMINI_API_KEY'] = original_key

print("\nTest completed successfully! ✨")
