#!/usr/bin/env python3
"""
Test script to verify the UI configuration options work correctly.
"""

import httpx
import json
from pathlib import Path

def test_ui_configuration():
    """Test that the UI configuration matches the test file configuration."""
    
    base_url = "http://localhost:5001/v1"
    
    # Configuration that matches the test file
    payload = {
        "from_formats": [
            "docx", "pptx", "html", "image", "pdf", "asciidoc", "md", 
            "csv", "xlsx", "xml_uspto", "xml_jats", "json_docling", "audio"
        ],
        "to_formats": ["md", "json"],
        "image_export_mode": "embedded",
        "do_ocr": True,
        "force_ocr": False,
        "ocr_engine": "easyocr",
        "pdf_backend": "dlparse_v4",
        "table_mode": "accurate",
        "table_cell_matching": True,
        "pipeline": "standard",
        "page_range": [1, 9223372036854776000],
        "document_timeout": 604800,
        "abort_on_error": False,
        "do_table_structure": True,
        "include_images": True,
        "images_scale": 2,
        "md_page_break_placeholder": "",
        "do_code_enrichment": True,
        "do_formula_enrichment": True,
        "do_picture_classification": True,
        "do_picture_description": True,
        "picture_description_area_threshold": 0.05,
        "enable_advanced_formula_enrichment": True,
        "enable_character_encoding_fix": True,
        "picture_description_local": {
            "repo_id": "ds4sd/SmolDocling-256M-preview", 
            "prompt": "Describe this image in a few sentences.", 
            "generation_config": {"max_new_tokens": 200, "do_sample": False}
        }
    }
    
    print("Testing configuration:")
    print(json.dumps(payload, indent=2))
    
    # Test if we can create a conversion request with this configuration
    test_sources = [{"kind": "http", "url": "https://arxiv.org/pdf/2501.17887"}]
    
    convert_request = {
        "sources": test_sources,
        "options": payload,
        "target": {"kind": "inbody"}
    }
    
    try:
        # Just test that the API accepts our configuration
        response = httpx.post(
            f"{base_url}/convert/source/async",
            json=convert_request,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Configuration accepted by API!")
            task_data = response.json()
            print(f"Task ID: {task_data.get('task_id')}")
        else:
            print(f"❌ API rejected configuration: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")

if __name__ == "__main__":
    test_ui_configuration()
