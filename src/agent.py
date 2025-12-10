"""
Main Claims Processing Agent
"""
import sys
import os
from typing import Dict, Any, Optional
from pathlib import Path

from src.extractor import FieldExtractor
from src.validator import FieldValidator
from src.router import ClaimRouter
from src.utils import read_document, format_output, save_output


class ClaimsProcessingAgent:
    """
    Autonomous agent for processing insurance FNOL documents.
    
    This agent:
    1. Extracts key fields from FNOL documents
    2. Validates data completeness
    3. Classifies and routes claims
    4. Provides reasoning for routing decisions
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the claims processing agent.
        
        Args:
            api_key: Google Gemini API key (optional)
        """
        self.extractor = FieldExtractor(api_key)
        self.validator = FieldValidator()
        self.router = ClaimRouter()
    
    def process_claim(self, document_path: str) -> Dict[str, Any]:
        """
        Process a single FNOL document.
        
        Args:
            document_path: Path to the FNOL document (PDF or TXT)
            
        Returns:
            Dictionary containing:
                - extractedFields: Structured data from document
                - missingFields: List of missing mandatory fields
                - recommendedRoute: Routing destination
                - reasoning: Explanation for routing decision
        """
        print(f"\n{'='*60}")
        print(f"Processing: {document_path}")
        print(f"{'='*60}\n")
        
        # Step 1: Read document
        print("📄 Reading document...")
        document_text = read_document(document_path)
        print(f"   ✓ Extracted {len(document_text)} characters\n")
        
        # Step 2: Extract fields using AI
        print("🤖 Extracting fields with AI...")
        extracted_fields = self.extractor.extract_fields(document_text, file_path=document_path)
        print(f"   ✓ Extracted {len([v for v in extracted_fields.values() if v])} fields\n")
        
        # Step 3: Validate fields
        print("✅ Validating fields...")
        missing_fields = self.validator.validate(extracted_fields)
        if missing_fields:
            print(f"   ⚠ Missing {len(missing_fields)} mandatory fields")
            for field in missing_fields:
                display_name = self.validator.get_field_name_display(field)
                print(f"      - {display_name}")
        else:
            print("   ✓ All mandatory fields present")
        print()
        
        # Step 4: Route claim
        print("🔀 Routing claim...")
        route, reasoning = self.router.route_claim(extracted_fields, missing_fields)
        print(f"   → Route: {route}")
        print(f"   → Reason: {reasoning}\n")
        
        # Prepare result
        result = {
            "extractedFields": extracted_fields,
            "missingFields": missing_fields,
            "recommendedRoute": route,
            "reasoning": reasoning
        }
        
        return result
    
    def process_batch(self, document_dir: str, output_dir: Optional[str] = None) -> None:
        """
        Process all FNOL documents in a directory.
        
        Args:
            document_dir: Directory containing FNOL documents
            output_dir: Directory to save output JSON files (optional)
        """
        doc_path = Path(document_dir)
        
        if not doc_path.exists():
            raise FileNotFoundError(f"Directory not found: {document_dir}")
        
        # Find all supported documents
        documents = []
        for ext in ['*.txt', '*.pdf']:
            documents.extend(doc_path.glob(ext))
        
        if not documents:
            print(f"No documents found in {document_dir}")
            return
        
        print(f"\n🚀 Processing {len(documents)} documents from {document_dir}\n")
        
        results = []
        for doc in sorted(documents):
            try:
                result = self.process_claim(str(doc))
                results.append({
                    "document": doc.name,
                    "result": result
                })
                
                # Save individual output if output_dir specified
                if output_dir:
                    output_path = Path(output_dir) / f"{doc.stem}_result.json"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    save_output(result, str(output_path))
                    print(f"💾 Saved output to: {output_path}\n")
                
            except Exception as e:
                print(f"❌ Error processing {doc.name}: {str(e)}\n")
                results.append({
                    "document": doc.name,
                    "error": str(e)
                })
        
        # Print summary
        print("\n" + "="*60)
        print("BATCH PROCESSING SUMMARY")
        print("="*60)
        
        successful = sum(1 for r in results if "error" not in r)
        print(f"\nTotal documents: {len(documents)}")
        print(f"Successfully processed: {successful}")
        print(f"Errors: {len(documents) - successful}\n")
        
        # Route distribution
        if successful > 0:
            routes = {}
            for r in results:
                if "error" not in r:
                    route = r["result"]["recommendedRoute"]
                    routes[route] = routes.get(route, 0) + 1
            
            print("Routing Distribution:")
            for route, count in sorted(routes.items()):
                print(f"  {route}: {count}")
        
        print()


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous Insurance Claims Processing Agent"
    )
    parser.add_argument(
        "document",
        nargs="?",
        help="Path to FNOL document (PDF or TXT)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all sample documents in sample_documents/"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path for result JSON"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for batch processing results"
    )
    
    args = parser.parse_args()
    
    try:
        agent = ClaimsProcessingAgent()
        
        if args.all:
            # Process all sample documents
            sample_dir = "sample_documents"
            agent.process_batch(sample_dir, args.output_dir)
        elif args.document:
            # Process single document
            result = agent.process_claim(args.document)
            
            # Print result
            print("\n" + "="*60)
            print("RESULT")
            print("="*60)
            print(format_output(result))
            
            # Save to file if specified
            if args.output:
                save_output(result, args.output)
                print(f"\n💾 Saved output to: {args.output}")
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
