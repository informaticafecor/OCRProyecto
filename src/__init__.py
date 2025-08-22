# src/__init__.py
"""
PDF OCR Processor - Módulos principales
=======================================
Biblioteca para procesamiento de PDFs con OCR automático.
"""

__version__ = "1.0.0"
__author__ = "Tu Nombre"
__email__ = "tu@email.com"

from .pdf_analyzer import PDFAnalyzer
from .ocr_processor import OCRProcessor
from .pdf_processor import PDFProcessor

__all__ = ['PDFAnalyzer', 'OCRProcessor', 'PDFProcessor']


# gui/__init__.py
"""
PDF OCR Processor - Interfaz Gráfica
====================================
Módulos de la interfaz gráfica de usuario.
"""

from .main_window import PDFOCRApp
from .progress_dialog import ProgressDialog, BatchProgressDialog
from .settings_dialog import SettingsDialog

__all__ = ['PDFOCRApp', 'ProgressDialog', 'BatchProgressDialog', 'SettingsDialog']