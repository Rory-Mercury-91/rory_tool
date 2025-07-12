# core/__init__.py
"""
Module core pour le Traducteur Ren'Py Pro
Contient la logique d'extraction, reconstruction et validation
"""

from .extraction import TextExtractor, get_file_base_name
from .reconstruction import FileReconstructor, validate_translations
from .validation import FileValidator, BackupManager, TranslationValidator
from .file_manager import file_manager, FileOpener, TempFileManager

__all__ = [
    'TextExtractor',
    'FileReconstructor', 
    'FileValidator',
    'BackupManager',
    'TranslationValidator',
    'file_manager',
    'FileOpener',
    'TempFileManager',
    'get_file_base_name',
    'validate_translations'
]