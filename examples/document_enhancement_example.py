#!/usr/bin/env python3
"""
Example script showing how to use the new document enhancement features in docling-serve.

This script demonstrates:
1. How to use the new enhancement options in API calls
2. How to enable advanced formula enrichment
3. How to enable character encoding fix
4. How the enhancement is applied automatically during processing
"""

import json
import time
import httpx
import asyncio
from pathlib import Path


async def example_with_enhancement():
    """Example showing how to use the new enhancement features."""
    
    # Configuration
    base_url = "http://localhost:5001/v1"
    
    # Example 1: URL conversion with enhancement
    print("=== Example 1: URL Conversion with Enhancement ===")
    
    payload = {
        "options": {
            "to_formats": ["json", "md"],
            "image_export_mode": "placeholder",
            "ocr": True,
            "force_ocr": False,
            "ocr_engine": "easyocr",
            "ocr_lang": ["en"],
            "pdf_backend": "dlparse_v2",
            "table_mode": "fast",
            "abort_on_error": False,
            # New enhancement options
            "enable_advanced_formula_enrichment": True,
            "enable_character_encoding_fix": True,
            "do_formula_enrichment": True,  # Original formula enrichment
        },
        "sources": [
            {"kind": "http", "url": "https://arxiv.org/pdf/2206.01062"}
        ],
        "target": {"kind": "inbody"}
    }
    
    print("Payload:")
    print(json.dumps(payload, indent=2))
    
    # Submit async request
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(f"{base_url}/convert/source/async", json=payload)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            return
        
        task = response.json()
        task_id = task["task_id"]
        print(f"Task ID: {task_id}")
        
        # Poll for completion
        while task["task_status"] not in ("success", "failure"):
            await asyncio.sleep(2)
            response = await client.get(f"{base_url}/status/poll/{task_id}")
            task = response.json()
            print(f"Status: {task['task_status']}, Position: {task.get('task_position', 'N/A')}")
        
        if task["task_status"] == "success":
            # Get result
            response = await client.get(f"{base_url}/result/{task_id}")
            result = response.json()
            
            print("✅ Conversion completed successfully!")
            print(f"Document has {len(result['document'].get('md_content', ''))} characters in markdown")
            
            # Show sample of enhanced content
            if result["document"].get("md_content"):
                sample = result["document"]["md_content"][:500]
                print(f"Sample content: {sample}...")
        else:
            print(f"❌ Conversion failed with status: {task['task_status']}")


async def example_with_file_enhancement():
    """Example showing file upload with enhancement."""
    
    print("\n=== Example 2: File Upload with Enhancement ===")
    
    # Create a simple test file (you would use a real PDF here)
    test_file_path = Path("test_document.txt")
    test_file_path.write_text("This is a test document with some mathematical formulas: E=mc² and α + β = γ")
    
    base_url = "http://localhost:5001/v1"
    
    # Prepare form data
    files = {
        "files": ("test_document.txt", test_file_path.open("rb"), "text/plain"),
    }
    
    data = {
        "to_formats": ["json", "md"],
        "image_export_mode": "placeholder",
        "ocr": True,
        "enable_advanced_formula_enrichment": True,
        "enable_character_encoding_fix": True,
        "target_type": "inbody"
    }
    
    print("Form data:")
    print(json.dumps(data, indent=2))
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(f"{base_url}/convert/file/async", files=files, data=data)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            # Clean up
            test_file_path.unlink(missing_ok=True)
            return
        
        task = response.json()
        task_id = task["task_id"]
        print(f"Task ID: {task_id}")
        
        # Poll for completion
        while task["task_status"] not in ("success", "failure"):
            await asyncio.sleep(2)
            response = await client.get(f"{base_url}/status/poll/{task_id}")
            task = response.json()
            print(f"Status: {task['task_status']}, Position: {task.get('task_position', 'N/A')}")
        
        if task["task_status"] == "success":
            # Get result
            response = await client.get(f"{base_url}/result/{task_id}")
            result = response.json()
            
            print("✅ File conversion completed successfully!")
            print(f"Document processed: {result['document'].get('md_content', 'No content')}")
        else:
            print(f"❌ File conversion failed with status: {task['task_status']}")
    
    # Clean up
    test_file_path.unlink(missing_ok=True)


def example_sync_api():
    """Example using synchronous API with enhancement."""
    
    print("\n=== Example 3: Synchronous API with Enhancement ===")
    
    base_url = "http://localhost:5001/v1"
    
    payload = {
        "options": {
            "to_formats": ["md"],
            "image_export_mode": "placeholder",
            "ocr": False,
            "enable_advanced_formula_enrichment": True,
            "enable_character_encoding_fix": True,
        },
        "sources": [
            {"kind": "http", "url": "https://arxiv.org/pdf/2206.01062"}
        ],
        "target": {"kind": "inbody"}
    }
    
    print("Making synchronous request...")
    
    # Note: This will wait for completion before returning
    response = httpx.post(f"{base_url}/convert/source", json=payload, timeout=120)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Synchronous conversion completed!")
        print(f"Document has {len(result['document'].get('md_content', ''))} characters")
    else:
        print(f"❌ Synchronous conversion failed: {response.status_code}")
        print(response.text)


async def main():
    """Run all examples."""
    print("Document Enhancement Integration Examples")
    print("=" * 50)
    
    try:
        await example_with_enhancement()
        await example_with_file_enhancement()
        example_sync_api()
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure docling-serve is running on localhost:5001")


if __name__ == "__main__":
    asyncio.run(main())
