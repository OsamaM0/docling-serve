"""
Simple store for tracking enhancement options per task.
This is needed because the orchestrator's ConvertDocumentsOptions 
doesn't include our custom enhancement fields.
"""
import threading
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class EnhancementOptions:
    """Container for document enhancement options."""
    enable_advanced_formula_enrichment: bool = False
    enable_character_encoding_fix: bool = False

class EnhancementStore:
    """Thread-safe store for enhancement options per task."""
    
    def __init__(self):
        self._store: Dict[str, EnhancementOptions] = {}
        self._lock = threading.Lock()
    
    def set_options(self, task_id: str, options: EnhancementOptions) -> None:
        """Store enhancement options for a task."""
        with self._lock:
            self._store[task_id] = options
    
    def get_options(self, task_id: str) -> Optional[EnhancementOptions]:
        """Retrieve enhancement options for a task."""
        with self._lock:
            return self._store.get(task_id)
    
    def remove_options(self, task_id: str) -> None:
        """Remove enhancement options for a task."""
        with self._lock:
            self._store.pop(task_id, None)
    
    def clear(self) -> None:
        """Clear all stored options."""
        with self._lock:
            self._store.clear()

# Global instance
_enhancement_store = EnhancementStore()

def get_enhancement_store() -> EnhancementStore:
    """Get the global enhancement store instance."""
    return _enhancement_store
