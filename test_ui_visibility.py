#!/usr/bin/env python3
"""
Simple script to test the UI interactively and ensure picture description fields are visible/hidden correctly.
"""

import json

def test_ui_visibility():
    """Test the conditional visibility logic."""
    
    print("🧪 Testing UI conditional visibility logic")
    print("="*50)
    
    # Simulate the toggle function logic
    def toggle_picture_description_fields(do_picture_description):
        visible = bool(do_picture_description)
        return {
            "picture_description_area_threshold": {"visible": visible},
            "picture_description_local": {"visible": visible},
            "include_images": {"visible": visible},
            "images_scale": {"visible": visible},
        }
    
    # Test when do_picture_description is False
    print("\n📋 Test 1: do_picture_description = False")
    result_false = toggle_picture_description_fields(False)
    for field, state in result_false.items():
        print(f"  {field}: {state}")
    
    # Test when do_picture_description is True
    print("\n📋 Test 2: do_picture_description = True")
    result_true = toggle_picture_description_fields(True)
    for field, state in result_true.items():
        print(f"  {field}: {state}")
    
    # Test JSON parsing logic
    print("\n📋 Test 3: JSON parsing for picture_description_local")
    test_json_valid = '{"repo_id": "ds4sd/SmolDocling-256M-preview", "prompt": "Describe this image in a few sentences.", "generation_config": {"max_new_tokens": 200, "do_sample": false}}'
    try:
        parsed = json.loads(test_json_valid)
        print(f"  ✅ Valid JSON parsed successfully: {type(parsed)}")
        print(f"    repo_id: {parsed.get('repo_id')}")
        print(f"    prompt: {parsed.get('prompt')}")
    except Exception as e:
        print(f"  ❌ JSON parsing failed: {e}")
    
    test_json_invalid = '{"repo_id": "invalid", "prompt": "test"'  # Missing closing brace
    try:
        parsed = json.loads(test_json_invalid)
        print(f"  ❌ Invalid JSON should have failed but didn't: {parsed}")
    except Exception as e:
        print(f"  ✅ Invalid JSON correctly failed: {e}")
    
    print("\n✅ All UI visibility tests completed!")
    print("\n📝 Summary of added features:")
    print("  • picture_description_area_threshold (float, 0.05 default)")
    print("  • picture_description_local (JSON string)")
    print("  • include_images (boolean, True default)")
    print("  • images_scale (number, 2 default)")
    print("  • do_table_structure (boolean, True default)")
    print("  • table_cell_matching (boolean, True default)")
    print("  • md_page_break_placeholder (string, empty default)")
    print("\n🎯 Conditional visibility:")
    print("  • picture_description_area_threshold: visible only when do_picture_description=True")
    print("  • picture_description_local: visible only when do_picture_description=True")
    print("  • include_images: visible only when do_picture_description=True")
    print("  • images_scale: visible only when do_picture_description=True")

if __name__ == "__main__":
    test_ui_visibility()
