"""
PDF Processor - Orquestador Principal
=====================================
Módulo principal que coordina el análisis y procesamiento de PDFs.
"""

import os
import shutil
import logging
from typing import Dict, List, Optional, Callable
from pathlib import Path
import threading
from datetime import datetime

from pdf_analyzer import PDFAnalyzer
from ocr_processor import OCRProcessor
from utils import create_backup, generate_output_filename, validate_paths

logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Clase principal para procesar PDFs con detección automática y OCR.
    """
    
    def __init__(self, language: str = 'spa', output_dir: Optional[str] = None,
                 create_backups: bool = True):
        """
        Inicializa el procesador principal.
        
        Args:
            language (str): Idioma para OCR
            output_dir (str): Directorio de salida
            create_backups (bool): Crear backups de archivos originales
        """
        self.analyzer = PDFAnalyzer()
        self.ocr_processor = OCRProcessor(language)
        self.output_dir = Path(output_dir) if output_dir else None
        self.create_backups = create_backups
        
        # Estadísticas de procesamiento
        self.stats = {
            'files_processed': 0,
            'files_with_ocr': 0,
            'files_copied': 0,
            'total_size_processed': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Configurar directorio de salida
        if self.output_dir:
            self.output_dir.mkdir(exist_ok=True)
            logger.info(f"Directorio de salida configurado: {self.output_dir}")
    
    def analyze_file(self, file_path: str) -> Dict:
        """
        Analiza un archivo PDF sin procesarlo.
        
        Args:
            file_path (str): Ruta al archivo PDF
            
        Returns:
            Dict: Análisis completo del archivo
        """
        try:
            logger.info(f"Analizando archivo: {os.path.basename(file_path)}")
            
            # Validar archivo
            is_valid, message = self.analyzer.validate_pdf(file_path)
            if not is_valid:
                return {
                    'success': False,
                    'error': message,
                    'file_path': file_path
                }
            
            # Realizar análisis completo
            analysis = self.analyzer.analyze_pdf(file_path)
            
            if analysis['success']:
                # Agregar estimación de tiempo de procesamiento
                time_estimate = self.ocr_processor.estimate_processing_time(file_path)
                analysis['time_estimate'] = time_estimate
                
                logger.info(f"Análisis completado: {analysis['recommendation']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error al analizar archivo {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def process_file(self, input_path: str, output_path: Optional[str] = None,
                    force_ocr: bool = False, progress_callback: Optional[Callable] = None) -> Dict:
        """
        Procesa un único archivo PDF.
        
        Args:
            input_path (str): Ruta del archivo de entrada
            output_path (str): Ruta del archivo de salida
            force_ocr (bool): Forzar OCR aunque tenga texto
            progress_callback (Callable): Función para reportar progreso
            
        Returns:
            Dict: Resultado del procesamiento
        """
        try:
            input_file = Path(input_path)
            
            if progress_callback:
                progress_callback(0, "Validando archivo...")
            
            # Validar entrada
            if not input_file.exists():
                return {
                    'success': False,
                    'error': 'Archivo no encontrado',
                    'input_path': input_path
                }
            
            # Generar ruta de salida si no se proporciona
            if not output_path:
                output_path = generate_output_filename(
                    input_path, 
                    self.output_dir,
                    suffix="_processed"
                )
            
            output_file = Path(output_path)
            
            if progress_callback:
                progress_callback(10, "Analizando contenido del PDF...")
            
            # Analizar el PDF
            analysis = self.analyze_file(input_path)
            if not analysis['success']:
                return analysis
            
            # Crear backup si está habilitado
            backup_path = None
            if self.create_backups and not force_ocr:
                backup_path = create_backup(input_path)
                if backup_path:
                    logger.info(f"Backup creado: {backup_path}")
            
            # Preparar resultado base
            result = {
                'input_path': str(input_file),
                'output_path': str(output_file),
                'analysis': analysis,
                'backup_path': backup_path,
                'processing_start': datetime.now(),
                'success': False
            }
            
            if progress_callback:
                progress_callback(20, "Determinando tipo de procesamiento...")
            
            # Decidir procesamiento
            needs_ocr = not analysis['has_embedded_text'] or force_ocr
            
            if needs_ocr:
                if progress_callback:
                    progress_callback(30, "Aplicando OCR al documento...")
                
                # Aplicar OCR
                ocr_result = self.ocr_processor.process_pdf(
                    str(input_file),
                    str(output_file),
                    progress_callback,
                    config={'force_ocr': force_ocr}
                )
                
                result.update(ocr_result)
                result['processing_type'] = 'ocr_applied'
                
                if ocr_result['success']:
                    self.stats['files_with_ocr'] += 1
                
            else:
                if progress_callback:
                    progress_callback(50, "Copiando archivo (ya contiene texto)...")
                
                # Simplemente copiar el archivo
                try:
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(input_file), str(output_file))
                    
                    result.update({
                        'success': True,
                        'processing_type': 'copy_only',
                        'input_size': input_file.stat().st_size,
                        'output_size': output_file.stat().st_size
                    })
                    
                    self.stats['files_copied'] += 1
                    
                    if progress_callback:
                        progress_callback(100, "Archivo copiado exitosamente")
                    
                except Exception as e:
                    result.update({
                        'success': False,
                        'error': f"Error al copiar archivo: {str(e)}"
                    })
            
            # Actualizar estadísticas
            result['processing_end'] = datetime.now()
            result['processing_duration'] = (
                result['processing_end'] - result['processing_start']
            ).total_seconds()
            
            if result['success']:
                self.stats['files_processed'] += 1
                self.stats['total_size_processed'] += analysis.get('file_size', 0)
                
                logger.info(f"Procesamiento exitoso: {output_file.name} "
                           f"({result['processing_type']})")
            else:
                self.stats['errors'] += 1
                logger.error(f"Error en procesamiento: {result.get('error', 'Error desconocido')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error crítico al procesar {input_path}: {str(e)}")
            self.stats['errors'] += 1
            
            if progress_callback:
                progress_callback(-1, f"Error: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'input_path': input_path
            }
    
    def process_batch(self, file_paths: List[str], 
                     progress_callback: Optional[Callable] = None,
                     completion_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Procesa múltiples archivos PDF.
        
        Args:
            file_paths (List[str]): Lista de rutas de archivos
            progress_callback (Callable): Función para reportar progreso
            completion_callback (Callable): Función llamada al completar
            
        Returns:
            List[Dict]: Lista de resultados
        """
        self.stats['start_time'] = datetime.now()
        
        total_files = len(file_paths)
        results = []
        
        logger.info(f"Iniciando procesamiento por lotes: {total_files} archivos")
        
        for i, file_path in enumerate(file_paths):
            try:
                if progress_callback:
                    overall_progress = int((i / total_files) * 100)
                    progress_callback(overall_progress, 
                                    f"Procesando {i+1}/{total_files}: {os.path.basename(file_path)}")
                
                # Función de progreso individual
                def file_progress(percent, message):
                    if progress_callback:
                        # Calcular progreso combinado
                        file_weight = 100 / total_files
                        combined_progress = int((i * file_weight) + (percent * file_weight / 100))
                        progress_callback(combined_progress, f"{message} ({i+1}/{total_files})")
                
                # Procesar archivo individual
                result = self.process_file(file_path, progress_callback=file_progress)
                results.append(result)
                
                # Log del resultado
                status = "✓" if result['success'] else "✗"
                logger.info(f"{status} {os.path.basename(file_path)}")
                
            except Exception as e:
                error_result = {
                    'success': False,
                    'error': str(e),
                    'input_path': file_path
                }
                results.append(error_result)
                logger.error(f"✗ {os.path.basename(file_path)}: {str(e)}")
        
        self.stats['end_time'] = datetime.now()
        
        # Resumen final
        successful = sum(1 for r in results if r['success'])
        logger.info(f"Procesamiento por lotes completado: {successful}/{total_files} exitosos")
        
        if progress_callback:
            progress_callback(100, f"¡Procesamiento completado! {successful}/{total_files} archivos")
        
        if completion_callback:
            completion_callback(results, self.get_stats())
        
        return results
    
    def process_batch_async(self, file_paths: List[str],
                          progress_callback: Optional[Callable] = None,
                          completion_callback: Optional[Callable] = None):
        """
        Procesa múltiples archivos de forma asíncrona.
        
        Args:
            file_paths (List[str]): Lista de rutas de archivos
            progress_callback (Callable): Función para reportar progreso
            completion_callback (Callable): Función llamada al completar
        """
        def worker():
            results = self.process_batch(file_paths, progress_callback, completion_callback)
            return results
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del procesamiento.
        
        Returns:
            Dict: Estadísticas detalladas
        """
        stats = self.stats.copy()
        
        if stats['start_time'] and stats['end_time']:
            stats['total_duration'] = (
                stats['end_time'] - stats['start_time']
            ).total_seconds()
            stats['average_time_per_file'] = (
                stats['total_duration'] / max(stats['files_processed'], 1)
            )
        
        stats['success_rate'] = (
            (stats['files_processed'] / 
             max(stats['files_processed'] + stats['errors'], 1)) * 100
        )
        
        return stats
    
    def reset_stats(self):
        """Reinicia las estadísticas."""
        self.stats = {
            'files_processed': 0,
            'files_with_ocr': 0,
            'files_copied': 0,
            'total_size_processed': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        logger.info("Estadísticas reiniciadas")
    
    def set_language(self, language: str) -> bool:
        """
        Cambia el idioma del OCR.
        
        Args:
            language (str): Código del idioma
            
        Returns:
            bool: True si el cambio fue exitoso
        """
        return self.ocr_processor.set_language(language)
    
    def get_available_languages(self) -> Dict[str, str]:
        """Obtiene idiomas disponibles para OCR."""
        return self.ocr_processor.get_available_languages()
    
    def validate_system(self) -> Dict:
        """
        Valida que el sistema esté correctamente configurado.
        
        Returns:
            Dict: Estado del sistema
        """
        tesseract_validation = self.ocr_processor.validate_tesseract()
        
        system_status = {
            'tesseract_ok': tesseract_validation['success'],
            'current_language': self.ocr_processor.language,
            'language_available': tesseract_validation.get('language_available', False),
            'output_dir_writable': True,
            'dependencies_ok': True
        }
        
        # Verificar directorio de salida
        if self.output_dir:
            try:
                test_file = self.output_dir / 'test_write.tmp'
                test_file.touch()
                test_file.unlink()
            except Exception:
                system_status['output_dir_writable'] = False
        
        # Verificar dependencias críticas
        try:
            import fitz
            import PyPDF2
            import ocrmypdf
        except ImportError:
            system_status['dependencies_ok'] = False
        
        system_status['overall_ok'] = all([
            system_status['tesseract_ok'],
            system_status['language_available'],
            system_status['output_dir_writable'],
            system_status['dependencies_ok']
        ])
        
        return system_status


def test_pdf_processor():
    """Función de prueba para el procesador principal."""
    processor = PDFProcessor()
    
    # Validar sistema
    system_status = processor.validate_system()
    print("Estado del sistema:")
    for key, value in system_status.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")
    
    print(f"\nIdiomas disponibles: {processor.get_available_languages()}")
    print(f"Estadísticas: {processor.get_stats()}")


if __name__ == "__main__":
    test_pdf_processor()