import json
import time
from pathlib import Path

import httpx
import pytest
import pytest_asyncio

from docling_serve.settings import docling_serve_settings


@pytest_asyncio.fixture
async def async_client():
    headers = {}
    if docling_serve_settings.api_key:
        headers["X-Api-Key"] = docling_serve_settings.api_key
    async with httpx.AsyncClient(timeout=3600.0, headers=headers) as client:
        yield client


@pytest.mark.asyncio
async def test_convert_url(async_client):
    """Test convert URL to all outputs"""

    base_url = "http://localhost:5001/v1"
    payload  =  {
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

    file_path = Path("C:/Users/Osama Mo/Documents/n2.pdf") #Path(__file__).parent / "2206.01062v1.pdf"
    files = {
        "files": (file_path.name, file_path.open("rb"), "application/pdf"),
    }

    for n in range(1):
        response = await async_client.post(
            f"{base_url}/convert/file/async", files=files, data=payload
        )
        assert response.status_code == 200, "Response should be 200 OK"

    task = response.json()

    print(json.dumps(task, indent=2))

    while task["task_status"] not in ("success", "failure"):
        response = await async_client.get(f"{base_url}/status/poll/{task['task_id']}")
        assert response.status_code == 200, "Response should be 200 OK"
        task = response.json()
        print(f"{task['task_status']=}")
        print(f"{task['task_position']=}")

        time.sleep(5)

    assert task["task_status"] == "success"
    print(f"Task completed with status {task['task_status']=}")

    result_resp = await async_client.get(f"{base_url}/result/{task['task_id']}")
    assert result_resp.status_code == 200, "Response should be 200 OK"
    result = result_resp.json()
    print("Got result.")

    assert "md_content" in result["document"]
    assert result["document"]["md_content"] is not None
    assert len(result["document"]["md_content"]) > 10

    assert "html_content" in result["document"]
    assert result["document"]["html_content"] is not None
    assert len(result["document"]["html_content"]) > 10

    assert "json_content" in result["document"]
    assert result["document"]["json_content"] is not None
    assert result["document"]["json_content"]["schema_name"] == "DoclingDocument"
