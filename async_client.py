import base64
import json
import time
from pathlib import Path
import urllib.request
import urllib.error

def main():
    # File path to the PDF
    file_path = Path("C:/Users/Osama Mo/Documents/n2.pdf")
    
    # Read and base64 encode the file
    with open(file_path, "rb") as f:
        file_content = f.read()
    base64_string = base64.b64encode(file_content).decode("utf-8")
    
    # Base URL from the curl
    base_url = "https://ur8psjsnq7xs1j-5001.proxy.runpod.net"
    
    # Prepare the JSON payload as in the curl
    payload = {
        "options": {
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
                "mets_gbs",
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
            "picture_description_area_threshold": 0.0,
            "enable_advanced_formula_enrichment": True,
            "enable_character_encoding_fix": True,
            "picture_description_local": {
                "repo_id": "Qwen/Qwen2.5-VL-7B-Instruct",
                "prompt": "قم بوصف هذه الصورة وصف دقيق وان كانت صورة رياضية قم بوصفها وصف رياضي دقيق بالارقام الدقيقة جداً وان كانت الصورة logo لا تقم بوصفه قم فقط بكتابة logo",
                "generation_config": {
                    "max_new_tokens": 500,
                    "do_sample": False
                }
            }
        },
        "sources": [
            {
                "base64_string": base64_string,
                "filename": "n2.pdf",
                "kind": "file"
            }
        ],
        "target": {
            "kind": "inbody"
        }
    }
    
    # Headers from the curl, plus User-Agent to mimic curl and avoid 403
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "curl/8.1.2"  # Mimic curl's User-Agent to bypass potential server restrictions
    }
    
    # Send the initial POST request
    convert_url = f"{base_url}/convert/source/async"
    data_json = json.dumps(payload)
    req = urllib.request.Request(convert_url, data=data_json.encode("utf-8"), headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(f"Error: Received status code {response.status}")
                return
            task = json.loads(response.read().decode("utf-8"))
            print("Initial task response:")
            print(json.dumps(task, indent=2))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return
    except Exception as e:
        print(f"Error sending request: {str(e)}")
        return
    
    # Poll the status until complete
    while task.get("task_status") not in ("success", "failure"):
        poll_url = f"{base_url}/status/poll/{task['task_id']}"
        poll_headers = {
            "User-Agent": "curl/8.1.2"  # Also add to poll requests
        }
        req = urllib.request.Request(poll_url, headers=poll_headers)
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    print(f"Error polling: Received status code {response.status}")
                    return
                task = json.loads(response.read().decode("utf-8"))
                print(f"Task status: {task.get('task_status')}")
                print(f"Task position: {task.get('task_position')}")
        except urllib.error.HTTPError as e:
            print(f"HTTP Error polling: {e.code} - {e.reason}")
            return
        except Exception as e:
            print(f"Error polling: {str(e)}")
            return
        
        time.sleep(5)
    
    # Check final status
    if task.get("task_status") != "success":
        print(f"Task failed with status: {task.get('task_status')}")
        return
    
    print(f"Task completed with status: {task.get('task_status')}")
    
    # Fetch the result
    result_url = f"{base_url}/result/{task['task_id']}"
    result_headers = {
        "User-Agent": "curl/8.1.2"  # Also add to result request
    }
    req = urllib.request.Request(result_url, headers=result_headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(f"Error fetching result: Received status code {response.status}")
                return
            result = json.loads(response.read().decode("utf-8"))
            print("Result fetched.")
            
            # Save Result
            if "document" in result and "json_content" in result["document"]:
                json_content = result["document"]["json_content"]
                if json_content:
                    with open("output.json", "w", encoding="utf-8") as f:
                        json.dump(json_content, f, ensure_ascii=False, indent=2)
                    print("JSON content saved to output.json")

    except urllib.error.HTTPError as e:
        print(f"HTTP Error fetching result: {e.code} - {e.reason}")
        return
    except Exception as e:
        print(f"Error fetching result: {str(e)}")
        return
    
    # Validate and save the markdown content (assuming 'md_content' is in result['document'])
    if "document" in result and "md_content" in result["document"]:
        md_content = result["document"]["md_content"]
        if md_content and len(md_content) > 10:
            with open("output.md", "w", encoding="utf-8") as f:
                f.write(md_content)
            print("Markdown content saved to output.md")
        else:
            print("Markdown content is empty or too short.")
    else:
        print("No 'md_content' found in result.")
    
    # Print full result for inspection
    print("Full result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()