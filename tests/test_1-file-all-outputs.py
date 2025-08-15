import json
import os

import httpx
import pytest
import pytest_asyncio
from pytest_check import check

from docling_serve.settings import docling_serve_settings


@pytest_asyncio.fixture
async def async_client():
    headers = {}
    if docling_serve_settings.api_key:
        headers["X-Api-Key"] = docling_serve_settings.api_key
    async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
        yield client


@pytest.mark.asyncio
async def test_convert_file(async_client):
    """Test convert single file to all outputs"""
    url = "http://localhost:5001/v1/convert/file"
    options =  {
      "from_formats": [
      "docx",
      "pptx",
      "html",
      "image",
      "pdf",
      "asciidoc",
      "md",
      "csv",
      "xlsx",
      "xml_uspto",
      "xml_jats",
      "json_docling",
      "audio"
    ],
    "to_formats": [
      "md",
      "json"
    ],
    "image_export_mode": "embedded",
    "do_ocr": True,
    "force_ocr": False,
    "ocr_engine": "easyocr",
    "pdf_backend": "dlparse_v4",
    "table_mode": "accurate",
    "table_cell_matching": True,
    "pipeline": "standard",
    "page_range": [
      1,
      9223372036854776000
    ],
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
    "picture_description_local": '{"repo_id": "ds4sd/SmolDocling-256M-preview", "prompt": "Describe this image in a few sentences.", "generation_config": {"max_new_tokens": 200, "do_sample": false}}'
  }

    current_dir = os.path.dirname(__file__)
    file_path = r"C:\Users\Osama Mo\Documents\n2.pdf"  # os.path.join(current_dir, r"C:\Users\Osama Mo\Documents\n2.pdf")

    files = {
        "files": ("n2.pdf", open(file_path, "rb"), "application/pdf"),
    }

    response = await async_client.post(url, files=files, data=options)
    assert response.status_code == 200, "Response should be 200 OK"

    data = response.json()

    # Response content checks
    # Helper function to safely slice strings
    def safe_slice(value, length=100):
        if isinstance(value, str):
            return value[:length]
        return str(value)  # Convert non-string values to string for debug purposes

    # Document check
    check.is_in(
        "document",
        data,
        msg=f"Response should contain 'document' key. Received keys: {list(data.keys())}",
    )
    # MD check
    check.is_in(
        "md_content",
        data.get("document", {}),
        msg=f"Response should contain 'md_content' key. Received keys: {list(data.get('document', {}).keys())}",
    )
    if data.get("document", {}).get("md_content") is not None:
        check.is_in(
            "## DocLayNet: ",
            data["document"]["md_content"],
            msg=f"Markdown document should contain 'DocLayNet: '. Received: {safe_slice(data['document']['md_content'])}",
        )
    # JSON check
    check.is_in(
        "json_content",
        data.get("document", {}),
        msg=f"Response should contain 'json_content' key. Received keys: {list(data.get('document', {}).keys())}",
    )
    if data.get("document", {}).get("json_content") is not None:
        check.is_in(
            '{"schema_name": "DoclingDocument"',
            json.dumps(data["document"]["json_content"]),
            msg=f'JSON document should contain \'{{\\n  "schema_name": "DoclingDocument\'". Received: {safe_slice(data["document"]["json_content"])}',
        )
    # HTML check
    if data.get("document", {}).get("html_content") is not None:
        check.is_in(
            "<!DOCTYPE html>\n<html>\n<head>",
            data["document"]["html_content"],
            msg=f"HTML document should contain '<!DOCTYPE html>\\n<html>'. Received: {safe_slice(data['document']['html_content'])}",
        )
    # Text check
    check.is_in(
        "text_content",
        data.get("document", {}),
        msg=f"Response should contain 'text_content' key. Received keys: {list(data.get('document', {}).keys())}",
    )
    if data.get("document", {}).get("text_content") is not None:
        check.is_in(
            "DocLayNet: A Large Human-Annotated Dataset",
            data["document"]["text_content"],
            msg=f"Text document should contain 'DocLayNet: A Large Human-Annotated Dataset'. Received: {safe_slice(data['document']['text_content'])}",
        )
    # DocTags check
    check.is_in(
        "doctags_content",
        data.get("document", {}),
        msg=f"Response should contain 'doctags_content' key. Received keys: {list(data.get('document', {}).keys())}",
    )
    if data.get("document", {}).get("doctags_content") is not None:
        check.is_in(
            "<doctag><page_header><loc",
            data["document"]["doctags_content"],
            msg=f"DocTags document should contain '<doctag><page_header><loc'. Received: {safe_slice(data['document']['doctags_content'])}",
        )
