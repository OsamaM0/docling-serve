import asyncio
import logging

from fastapi import BackgroundTasks, Response

from docling_jobkit.datamodel.result import (
    ConvertDocumentResult,
    ExportResult,
    RemoteTargetResult,
    ZipArchiveResult,
    ExportDocumentResponse
)
from docling_jobkit.orchestrators.base_orchestrator import (
    BaseOrchestrator,
)

from docling_serve.datamodel.responses import (
    ConvertDocumentResponse,
    PresignedUrlConvertDocumentResponse,
)
from docling_serve.settings import docling_serve_settings
from docling_serve.document_enhancement import DocumentProcessor
from docling_serve.enhancement_store import get_enhancement_store

_log = logging.getLogger(__name__)


async def prepare_response(
    task_id: str,
    task_result: ConvertDocumentResult,
    orchestrator: BaseOrchestrator,
    background_tasks: BackgroundTasks,
):
    response: Response | ConvertDocumentResponse | PresignedUrlConvertDocumentResponse
    if isinstance(task_result.result, ExportResult):
        enhanced_result = task_result.result
        # Get enhancement options from the store
        enhancement_store = get_enhancement_store()
        enhancement_options = enhancement_store.get_options(task_id)
        
        if enhancement_options and (enhancement_options.enable_advanced_formula_enrichment or enhancement_options.enable_character_encoding_fix):
            _log.info(f"Preparing document enhancement with options: {enhancement_options}")
            try:
                processor = DocumentProcessor(
                    enable_formula_enhancement=enhancement_options.enable_advanced_formula_enrichment,
                    enable_character_encoding_fix=enhancement_options.enable_character_encoding_fix
                )
                # Apply enhancement on the conversion result
                if hasattr(enhanced_result.content, 'json_content') and enhanced_result.content.json_content:
                    new_doc = ""
                    try:
                        enhanced_conversion_result = processor.process_conversion_result(enhanced_result.content.json_content)
                        new_doc = enhanced_conversion_result
                    except Exception as e:
                        _log.error(f"Error enhancing document: {e}")
                        new_doc = enhanced_result.content.json_content  # Return original if enhancement fails

                    image_mode = "embedded"
                    # Update content based on correct options
                    if enhanced_result.content.json_content:
                         enhanced_result.content.json_content = new_doc
                    if enhanced_result.content.html_content:
                         enhanced_result.content.html_content = new_doc.export_to_html(image_mode=image_mode)
                    if enhanced_result.content.text_content:
                         enhanced_result.content.text_content = new_doc.export_to_markdown(
                            strict_text=True,
                            image_mode=image_mode,
                        )
                    if enhanced_result.content.md_content:
                         enhanced_result.content.md_content = new_doc.export_to_markdown(
                            image_mode=image_mode,
                            page_break_placeholder= None,
                        )
                    
                
                _log.info(f"Applied document enhancement with options: formula_enrichment={enhancement_options.enable_advanced_formula_enrichment}, character_encoding_fix={enhancement_options.enable_character_encoding_fix}")
            except Exception as e:
                _log.error(f"Error in document enhancement pipeline: {e}")
                # Continue with original result if enhancement setup fails
        
        # Clean up the stored options
        enhancement_store.remove_options(task_id)
        
        response = ConvertDocumentResponse(
            document=enhanced_result.content,
            status=enhanced_result.status,
            processing_time=task_result.processing_time,
            timings=enhanced_result.timings,
            errors=enhanced_result.errors,
        )
    elif isinstance(task_result.result, ZipArchiveResult):
        response = Response(
            content=task_result.result.content,
            media_type="application/zip",
            headers={
                "Content-Disposition": 'attachment; filename="converted_docs.zip"'
            },
        )
    elif isinstance(task_result.result, RemoteTargetResult):
        response = PresignedUrlConvertDocumentResponse(
            processing_time=task_result.processing_time,
            num_converted=task_result.num_converted,
            num_succeeded=task_result.num_succeeded,
            num_failed=task_result.num_failed,
        )
    else:
        raise ValueError("Unknown result type")

    if docling_serve_settings.single_use_results:

        async def _remove_task_impl():
            await asyncio.sleep(docling_serve_settings.result_removal_delay)
            await orchestrator.delete_task(task_id=task_id)

        async def _remove_task():
            asyncio.create_task(_remove_task_impl())  # noqa: RUF006

        background_tasks.add_task(_remove_task)

    return response
