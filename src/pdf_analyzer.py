"""
PDF Analyzer - Análisis de documentos PDF
==========================================
Módulo para analizar PDFs y determinar si contienen texto embebido o son escaneados.
"""

import os
import logging
from typing import Tuple, Dict, List
import fitz  # PyMuPDF
import PyPDF2
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFAnalyzer:
    """
    Clase para analizar PDFs y determinar sus características.
    """
    
    def __init__(self, min_text_length: int = 50):
        """
        Inicializa el analizador de PDFs.
        
        Args:
            min_text_length (int): Longitud mínima de texto para considerar que tiene contenido
        """
        self.min_text_length = min_text_length
    
    def analyze_pdf(self, pdf_path: str) -> Dict:
        """
        Analiza completamente un PDF y retorna toda la información.
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            
        Returns:
            Dict: Información completa del PDF
        """
        try:
            if not os.path.exists(pdf_path):
                return {'error': 'Archivo no encontrado', 'success': False}
            
            # Información básica
            file_size = os.path.getsize(pdf_path)
            file_name = os.path.basename(pdf_path)
            
            # Análisis con PyMuPDF
            has_text, page_count = self.has_embedded_text(pdf_path)
            detailed_info = self.get_detailed_info(pdf_path)
            page_analysis = self.analyze_pages(pdf_path)
            
            result = {
                'success': True,
                'file_name': file_name,
                'file_path': pdf_path,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'page_count': page_count,
                'has_embedded_text': has_text,
                'text_coverage': self._calculate_text_coverage(page_analysis),
                'recommendation': self._get_recommendation(has_text, page_analysis),
                'detailed_info': detailed_info,
                'page_analysis': page_analysis,
                'processing_needed': not has_text
            }
            
            logger.info(f"Análisis completado para {file_name}: "
                       f"{'Con texto' if has_text else 'Sin texto'}, {page_count} páginas")
            
            return result
            
        except Exception as e:
            logger.error(f"Error al analizar PDF {pdf_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_path': pdf_path
            }
    
    def has_embedded_text(self, pdf_path: str) -> Tuple[bool, int]:
        """
        Detecta si un PDF tiene texto embebido.
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            
        Returns:
            Tuple[bool, int]: (tiene_texto, número_de_páginas)
        """
        try:
            doc = fitz.open(pdf_path)
            total_text = ""
            total_pages = len(doc)
            
            # Analizar máximo 5 páginas para eficiencia
            pages_to_check = min(5, total_pages)
            
            for page_num in range(pages_to_check):
                page = doc[page_num]
                text = page.get_text()
                total_text += text
            
            doc.close()
            
            # Filtrar texto significativo
            meaningful_text = ''.join(c for c in total_text if c.isalnum() or c.isspace())
            has_text = len(meaningful_text.strip()) > self.min_text_length
            
            return has_text, total_pages
            
        except Exception as e:
            logger.error(f"Error al verificar texto en PDF: {str(e)}")
            return False, 0
    
    def get_detailed_info(self, pdf_path: str) -> Dict:
        """
        Obtiene información detallada del PDF usando PyMuPDF.
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            
        Returns:
            Dict: Información detallada del PDF
        """
        try:
            doc = fitz.open(pdf_path)
            
            info = {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', ''),
                'pages': len(doc),
                'is_encrypted': doc.is_encrypted,
                'page_mode': doc.page_mode if hasattr(doc, 'page_mode') else 'Unknown'
            }
            
            doc.close()
            return info
            
        except Exception as e:
            logger.error(f"Error al obtener información detallada: {str(e)}")
            return {}
    
    def analyze_pages(self, pdf_path: str, max_pages: int = 10) -> List[Dict]:
        """
        Analiza páginas individuales del PDF.
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            max_pages (int): Máximo número de páginas a analizar
            
        Returns:
            List[Dict]: Lista con análisis de cada página
        """
        try:
            doc = fitz.open(pdf_path)
            page_analysis = []
            
            pages_to_analyze = min(max_pages, len(doc))
            
            for page_num in range(pages_to_analyze):
                page = doc[page_num]
                
                # Extraer texto
                text = page.get_text()
                text_length = len(text.strip())
                
                # Obtener imágenes
                image_list = page.get_images()
                image_count = len(image_list)
                
                # Calcular área de texto aproximada
                text_blocks = page.get_text("blocks")
                text_area = sum(block[2] * block[3] for block in text_blocks if isinstance(block[4], str))
                
                page_info = {
                    'page_number': page_num + 1,
                    'text_length': text_length,
                    'has_meaningful_text': text_length > 20,
                    'image_count': image_count,
                    'text_area': text_area,
                    'dimensions': {
                        'width': page.rect.width,
                        'height': page.rect.height
                    }
                }
                
                page_analysis.append(page_info)
            
            doc.close()
            return page_analysis
            
        except Exception as e:
            logger.error(f"Error al analizar páginas: {str(e)}")
            return []
    
    def _calculate_text_coverage(self, page_analysis: List[Dict]) -> float:
        """
        Calcula el porcentaje de páginas que tienen texto significativo.
        
        Args:
            page_analysis (List[Dict]): Análisis de páginas
            
        Returns:
            float: Porcentaje de cobertura de texto (0-100)
        """
        if not page_analysis:
            return 0.0
        
        pages_with_text = sum(1 for page in page_analysis if page['has_meaningful_text'])
        return (pages_with_text / len(page_analysis)) * 100
    
    def _get_recommendation(self, has_text: bool, page_analysis: List[Dict]) -> str:
        """
        Genera una recomendación basada en el análisis.
        
        Args:
            has_text (bool): Si el PDF tiene texto embebido
            page_analysis (List[Dict]): Análisis de páginas
            
        Returns:
            str: Recomendación de procesamiento
        """
        if has_text:
            text_coverage = self._calculate_text_coverage(page_analysis)
            
            if text_coverage > 80:
                return "✅ El PDF ya tiene texto embebido. No necesita OCR."
            elif text_coverage > 50:
                return "⚠️ El PDF tiene texto parcial. Considera OCR para completar."
            else:
                return "🔄 El PDF tiene poco texto. Se recomienda OCR."
        else:
            return "📄 PDF escaneado detectado. Se requiere OCR para hacerlo buscable."
    
    def validate_pdf(self, pdf_path: str) -> Tuple[bool, str]:
        """
        Valida si el archivo es un PDF válido.
        
        Args:
            pdf_path (str): Ruta al archivo PDF
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje)
        """
        try:
            if not os.path.exists(pdf_path):
                return False, "El archivo no existe"
            
            if not pdf_path.lower().endswith('.pdf'):
                return False, "El archivo no tiene extensión .pdf"
            
            # Intentar abrir con PyMuPDF
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            
            if page_count == 0:
                return False, "El PDF no contiene páginas"
            
            return True, f"PDF válido con {page_count} páginas"
            
        except Exception as e:
            return False, f"Error al validar PDF: {str(e)}"


def test_analyzer():
    """Función de prueba para el analizador."""
    analyzer = PDFAnalyzer()
    
    # Crear un PDF de prueba si no existe
    test_file = "test.pdf"
    
    if os.path.exists(test_file):
        result = analyzer.analyze_pdf(test_file)
        print("Resultado del análisis:")
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        print("No se encontró archivo de prueba")


if __name__ == "__main__":
    test_analyzer()