import logging
from typing import Tuple

from PIL import Image

_log = logging.getLogger(__name__)

try:
    from surya.models import load_predictors
    SURYA_AVAILABLE = True
except ImportError:
    SURYA_AVAILABLE = False
    _log.warning("Surya models not available. OCR enhancement will be limited.")


class OCREnhancer:
    """Handles OCR enhancement using Surya models."""

    def __init__(self):
        """Initialize OCR predictors lazily for efficiency."""
        self._models_loaded = False
        self._models_loading = False
        self._foundation_predictor = None
        self._recognition_predictor = None
        self._detection_predictor = None
        self._table_rec_predictor = None
        self._device = None

    def _load_models(self):
        """Load OCR models with CPU fallback."""
        if self._models_loaded or self._models_loading:
            return
        
        if not SURYA_AVAILABLE:
            _log.warning("Surya models not available. OCR enhancement will be disabled.")
            return

        self._models_loading = True
        try:
            # Try GPU first, fallback to CPU
            use_cuda = self._try_cuda()
            device = 'cuda' if use_cuda else 'cpu'
            self._device = device
            
            _log.info(f"Loading Surya models on {device}...")
            
            predictor = load_predictors(device=device)

            self._recognition_predictor = predictor.get('recognition')
            self._detection_predictor = predictor.get('detection')
            self._table_rec_predictor = predictor.get('table_rec')

            self._models_loaded = True
                    
        except Exception as e:
            _log.error(f"Failed to load Surya models: {e}")
            self._models_loaded = False
        finally:
            self._models_loading = False

    def _try_cuda(self):
        """Test if CUDA is available and has enough memory."""
        try:
            import torch
            if not torch.cuda.is_available():
                return False
            
            # Test CUDA memory by trying to allocate a small tensor
            test_tensor = torch.zeros(100, 100).cuda()
            del test_tensor
            torch.cuda.empty_cache()
            return True
        except Exception:
            return False

    @property
    def recognition_predictor(self):
        if not self._models_loaded:
            self._load_models()
        return self._recognition_predictor

    @property 
    def detection_predictor(self):
        if not self._models_loaded:
            self._load_models()
        return self._detection_predictor

    @property
    def table_rec_predictor(self):
        if not self._models_loaded:
            self._load_models()
        return self._table_rec_predictor

    def extract_text_from_region(self, image: Image.Image, bbox: Tuple[int, int, int, int], old_text: str, math_mode: bool = False) -> str:
        """Extract text from a specific region using OCR with padding and background enhancement."""
        if not self._models_loaded:
            self._load_models()
            
        if not self._models_loaded:
            _log.warning("OCR models not available, returning original text")
            return old_text

        try:
            x1, y1, x2, y2 = bbox
            thr = 5  # Slight padding to improve OCR accuracy

            # Safe cropping with bounds
            left = max(x1 - thr, 0)
            top = max(y1 - thr, 0)
            right = min(x2 + thr, image.width)
            bottom = min(y2 + thr, image.height)

            # Crop and create padded background
            cropped = image.crop((left, top, right, bottom))

            # Create background and paste cropped image at center
            scale_w = 2
            scale_h = 2
            bg_w = int(cropped.width * scale_w)
            bg_h = int(cropped.height * scale_h)
            background = Image.new("RGB", (bg_w, bg_h), (255, 255, 255))  # white background
            paste_x = (bg_w - cropped.width) // 2
            paste_y = (bg_h - cropped.height) // 2
            background.paste(cropped, (paste_x, paste_y))
            
            # Enable Math Mode for formula recognition
            
            # Run OCR on enhanced image
            predictions = self.recognition_predictor(
                [background], 
                det_predictor=self.detection_predictor, 
                math_mode=math_mode, 
                task_names=['ocr_with_boxes']
            )

            # Extract high-confidence lines
            lines = []
            if predictions:
                for line in predictions[0].text_lines:
                    if line.confidence > 0.5:
                        lines.append(line.text)

            enhanced_text = ' '.join(lines).strip()
            return enhanced_text if enhanced_text else old_text

        except Exception as e:
            _log.error(f"Error in OCR enhancement: {e}")
            return old_text

    def enhance_table_structure(self, table_image: Image.Image, page_dim: Tuple[int, int],
                               table_item, table_bbox: Tuple[int, int, int, int],
                               pdf_w: float, pdf_h: float):
        """Enhanced table structure using Surya table recognition."""
        if not self._models_loaded:
            self._load_models()
            
        if not self._models_loaded:
            _log.warning("Table recognition models not available")
            return

        try:
            from .bbox_utils import BoundingBoxConverter
            
            # Get table predictions from Surya
            table_predictions = self.table_rec_predictor([table_image])
            if not table_predictions:
                return

            surya_table = table_predictions[0]
            surya_cell_dict = {(cell.row_id, cell.col_id): cell for cell in surya_table.cells}

            # Update each table cell with Surya predictions
            for cell in table_item.data.table_cells:
                row, col = cell.start_row_offset_idx, cell.start_col_offset_idx

                if (row, col) in surya_cell_dict:
                    surya_cell = surya_cell_dict[(row, col)]
                    # Update cell bbox using the corrected logic
                    BoundingBoxConverter.update_cell_bbox(
                        cell, surya_cell, table_bbox, page_dim, pdf_w, pdf_h
                    )

        except Exception as e:
            _log.error(f"Error in table structure enhancement: {e}")
