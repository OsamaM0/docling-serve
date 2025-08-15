#!/usr/bin/env python3
"""
Demonstration script for the new document enhancement features in docling-serve.

This script shows how to use the new enhancement options:
- enable_advanced_formula_enrichment: Enhances formula recognition using OCR
- enable_character_encoding_fix: Fixes corrupted text characters

The enhancement is integrated at the response preparation level and works with all endpoints.
"""

import json
import asyncio
from docling_serve.datamodel.convert import ConvertDocumentsRequestOptions
from docling_serve.document_enhancement import DocumentProcessor


def demo_new_options():
    """Demonstrate the new enhancement options in the API."""
    print("=== Document Enhancement Integration Demo ===\n")
    
    # Show how to use the new options
    print("1. Creating options with new enhancement flags:")
    options = ConvertDocumentsRequestOptions(
        enable_advanced_formula_enrichment=True,
        enable_character_encoding_fix=True
    )
    
    print(f"   Advanced formula enrichment: {options.enable_advanced_formula_enrichment}")
    print(f"   Character encoding fix: {options.enable_character_encoding_fix}")
    print()
    
    # Show the JSON representation
    print("2. API payload with enhancement options:")
    payload = {
        "options": {
            "enable_advanced_formula_enrichment": options.enable_advanced_formula_enrichment,
            "enable_character_encoding_fix": options.enable_character_encoding_fix,
            "to_formats": ["json", "md"],
            "ocr": True
        },
        "sources": [{"kind": "http", "url": "https://arxiv.org/pdf/2206.01062"}]
    }
    print(json.dumps(payload, indent=2))
    print()
    
    # Show how the enhancement processor works
    print("3. Document Enhancement Processor:")
    processor = DocumentProcessor(
        enable_formula_enhancement=True,
        enable_character_encoding_fix=True
    )
    print(f"   Formula enhancement enabled: {processor.enable_formula_enhancement}")
    print(f"   Character encoding fix enabled: {processor.enable_character_encoding_fix}")
    print()
    
    print("4. Integration Points:")
    print("   - API Options: Added to ConvertDocumentsRequestOptions")
    print("   - UI Controls: Added to Gradio interface")
    print("   - Processing: Integrated in response_preparation.py")
    print("   - Enhancement: Applied after docling conversion, before response")
    print()
    
    print("5. Example API requests:")
    print("\n   Synchronous endpoint:")
    print("   POST /v1/convert/source")
    print("   {")
    print('     "options": {')
    print('       "enable_advanced_formula_enrichment": true,')
    print('       "enable_character_encoding_fix": true')
    print('     },')
    print('     "sources": [{"kind": "http", "url": "https://example.com/doc.pdf"}]')
    print("   }")
    
    print("\n   Asynchronous endpoint:")
    print("   POST /v1/convert/source/async")
    print("   (same payload)")
    print()
    
    print("✅ Enhancement integration completed successfully!")
    print("   The enhancement will be applied automatically when:")
    print("   - enable_advanced_formula_enrichment=true OR")
    print("   - enable_character_encoding_fix=true")
    print("   - Enhancement happens after docling conversion")
    print("   - Original results are preserved if enhancement fails")


if __name__ == "__main__":
    demo_new_options()
