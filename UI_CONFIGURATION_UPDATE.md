# UI Configuration Update Summary

## Overview
Successfully added comprehensive configuration options from the test file to the docling-serve UI, with conditional visibility for picture description specific fields.

## Added Configuration Options

### Picture Description Options (Conditional)
- **`picture_description_area_threshold`** (Number, default: 0.05)
  - Minimum percentage (0-1) of page area for a picture to be described
  - Only visible when `do_picture_description` is enabled

- **`picture_description_local`** (Textbox, JSON format)
  - Configuration for local picture description model
  - Default: `{"repo_id": "ds4sd/SmolDocling-256M-preview", "prompt": "Describe this image in a few sentences.", "generation_config": {"max_new_tokens": 200, "do_sample": false}}`
  - Only visible when `do_picture_description` is enabled

- **`include_images`** (Checkbox, default: True)
  - Whether to include images in the output
  - Only visible when `do_picture_description` is enabled

- **`images_scale`** (Number, default: 2)
  - Scale factor for images
  - Only visible when `do_picture_description` is enabled

### Always Visible Options
- **`do_table_structure`** (Checkbox, default: True)
  - Enable table structure detection

- **`table_cell_matching`** (Checkbox, default: True)
  - Enable table cell matching

- **`md_page_break_placeholder`** (Textbox, default: "")
  - Placeholder for markdown page breaks

## Implementation Details

### Conditional Visibility Logic
```python
def toggle_picture_description_fields(do_picture_description):
    visible = bool(do_picture_description)
    return (
        gr.update(visible=visible),  # picture_description_area_threshold
        gr.update(visible=visible),  # picture_description_local
        gr.update(visible=visible),  # include_images
        gr.update(visible=visible),  # images_scale
    )
```

### API Parameter Mapping
- UI uses `ocr` → API expects `do_ocr` ✅ Fixed
- All new parameters are correctly mapped to their API equivalents
- JSON parsing with error handling for `picture_description_local`

### Updated Function Signatures
Both `process_url()` and `process_file()` functions now include all the new parameters:

```python
def process_url(
    # ... existing parameters ...
    picture_description_area_threshold,
    picture_description_local,
    include_images,
    images_scale,
    do_table_structure,
    table_cell_matching,
    md_page_break_placeholder,
    # ... other parameters ...
):
```

## Testing Results

### ✅ API Compatibility Test
- Configuration successfully accepted by the API
- Task ID generated: `2210f9a4-c3e8-4cd8-ba93-9e395ef6eb77`
- All parameter names correctly mapped

### ✅ JSON Parsing Test
- Valid JSON for `picture_description_local` parses correctly
- Invalid JSON properly raises errors with helpful messages
- Error handling prevents UI crashes

### ✅ Visibility Logic Test
- Fields are hidden when `do_picture_description = False`
- Fields are shown when `do_picture_description = True`
- Interactive toggle works as expected

## Configuration Match with Test File

The UI now supports the exact same configuration as used in `test_1-file-async.py`:

```json
{
  "do_picture_description": true,
  "picture_description_area_threshold": 0.05,
  "picture_description_local": {
    "repo_id": "ds4sd/SmolDocling-256M-preview",
    "prompt": "Describe this image in a few sentences.",
    "generation_config": {
      "max_new_tokens": 200,
      "do_sample": false
    }
  },
  "include_images": true,
  "images_scale": 2,
  "do_table_structure": true,
  "table_cell_matching": true,
  "md_page_break_placeholder": ""
}
```

## Files Modified

1. **`docling_serve/gradio_ui.py`**
   - Added new UI components
   - Updated function signatures
   - Added conditional visibility logic
   - Updated API parameter mapping
   - Added JSON parsing with error handling

## Next Steps

The UI is now fully compatible with the test configuration and provides:
- ✅ All configuration options from the test file
- ✅ Conditional visibility for picture description fields
- ✅ Proper API parameter mapping
- ✅ Error handling for JSON configuration
- ✅ Interactive UI that works with the existing docling-serve backend

Users can now access these advanced picture description and document processing options through the web interface, making the powerful features from the test configuration easily accessible via the UI.
