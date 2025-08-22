"""
OCR Processor - Procesamiento OCR con OCRmyPDF
==============================================
Módulo para aplicar OCR a documentos PDF usando OCRmyPDF y Tesseract.
"""

import os
import logging
import subprocess
import threading
from typing import Dict, Callable, Optional
from pathlib import Path
import ocrmypdf

# Importar excepciones de forma compatible
try:
    from ocrmypdf.exceptions import ExitCodeNotZero
except ImportError:
    # Para versiones más antiguas de OCRmyPDF
    try:
        from ocrmypdf import ExitCodeNotZero
    except ImportError:
        # Crear una excepción personalizada si no existe
        class ExitCodeNotZero(Exception):
            def __init__(self, exit_code, message=""):
                self.exit_code = exit_code
                super().__init__(message)

logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    Clase para procesar PDFs con OCR usando OCRmyPDF.
    """
    
    def __init__(self, language: str = 'spa'):
        """
        Inicializa el procesador OCR.
        
        Args:
            language (str): Idioma para OCR ('spa', 'eng', etc.)
        """
        self.language = language
        self.supported_languages = {
            'spa': 'Español',
            'eng': 'English',
            'fra': 'Français',
            'deu': 'Deutsch',
            'ita': 'Italiano',
            'por': 'Português'
        }
        
        # Configuración por defecto
        self.default_config = {
            'optimize': 1,
            'clean': True,
            'deskew': True,
            'remove_background': False,
            'rotate_pages': True,
            'skip_big': 100.0,  # Skip pages larger than 100MB
            'jpeg_quality': 85,
            'png_quality': 85
        }
    
    def validate_tesseract(self) -> Dict[str, any]:
        """
        Valida la instalación de Tesseract y los idiomas disponibles.
        
        Returns:
            Dict: Estado de la validación
        """
        try:
            # Verificar que Tesseract esté instalado
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': 'Tesseract no está instalado o no está en PATH',
                    'tesseract_version': None,
                    'available_languages': []
                }
            
            # Obtener versión
            version_line = result.stdout.split('\n')[0]
            tesseract_version = version_line.split()[1] if len(version_line.split()) > 1 else 'Desconocida'
            
            # Obtener idiomas disponibles
            lang_result = subprocess.run(['tesseract', '--list-langs'], 
                                       capture_output=True, text=True, timeout=10)
            
            if lang_result.returncode == 0:
                available_languages = [lang.strip() for lang in lang_result.stdout.split('\n')[1:] if lang.strip()]
            else:
                available_languages = []
            
            # Verificar si el idioma configurado está disponible
            language_available = self.language in available_languages
            
            return {
                'success': True,
                'tesseract_version': tesseract_version,
                'available_languages': available_languages,
                'current_language': self.language,
                'language_available': language_available,
                'language_name': self.supported_languages.get(self.language, self.language)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Timeout al verificar Tesseract',
                'tesseract_version': None,
                'available_languages': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al verificar Tesseract: {str(e)}',
                'tesseract_version': None,
                'available_languages': []
            }
    
    def process_pdf(self, input_path: str, output_path: str, 
                   progress_callback: Optional[Callable] = None,
                   config: Optional[Dict] = None) -> Dict:
        """
        Procesa un PDF aplicando OCR.
        
        Args:
            input_path (str): Ruta del PDF de entrada
            output_path (str): Ruta del PDF de salida
            progress_callback (Callable): Función para reportar progreso
            config (Dict): Configuración personalizada
            
        Returns:
            Dict: Resultado del procesamiento
        """
        try:
            if not os.path.exists(input_path):
                return {
                    'success': False,
                    'error': 'Archivo de entrada no encontrado',
                    'input_path': input_path
                }
            
            # Usar configuración por defecto si no se proporciona una
            if config is None:
                config = self.default_config.copy()
            
            # Preparar directorio de salida
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"Iniciando OCR: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
            
            if progress_callback:
                progress_callback(0, "Verificando PDF...")
            
            # Verificar si el PDF está cifrado y intentar descifrarlo
            temp_input = input_path
            try:
                temp_input = self._handle_encrypted_pdf(input_path, progress_callback)
            except Exception as e:
                logger.warning(f"No se pudo descifrar PDF: {e}")
            
            if progress_callback:
                progress_callback(10, "Configurando OCR...")
            
            # Configurar OCRmyPDF con opciones más permisivas
            ocr_options = {
                'language': self.language,
                'output_type': 'pdf',
                'optimize': config.get('optimize', 1),
                'clean': config.get('clean', True),
                'deskew': config.get('deskew', True),
                'remove_background': config.get('remove_background', False),
                'rotate_pages': config.get('rotate_pages', True),
                'skip_big': config.get('skip_big', 100.0),
                'jpeg_quality': config.get('jpeg_quality', 85),
                'png_quality': config.get('png_quality', 85),
                'force_ocr': config.get('force_ocr', False),
                'skip_text': not config.get('force_ocr', False),
                'redo_ocr': config.get('force_ocr', False),
                # Opciones adicionales para PDFs problemáticos
                'invalidate_digital_signatures': True,  # Remover firmas digitales
                'pages': None,  # Procesar todas las páginas
                'max_image_mpixels': 128,  # Límite de píxeles para imágenes grandes
            }
            
            if progress_callback:
                progress_callback(20, "Iniciando procesamiento OCR...")
            
            # Ejecutar OCRmyPDF con manejo de errores mejorado
            try:
                ocrmypdf.ocr(
                    input_file=temp_input,
                    output_file=output_path,
                    **ocr_options
                )
            except Exception as ocr_error:
                # Si falla OCRmyPDF, intentar con método alternativo
                logger.warning(f"OCRmyPDF falló: {ocr_error}. Intentando método alternativo...")
                
                if progress_callback:
                    progress_callback(40, "Intentando método alternativo de OCR...")
                
                # Método alternativo usando solo Tesseract
                try:
                    success = self._tesseract_fallback_ocr(temp_input, output_path, progress_callback)
                    if not success:
                        raise Exception("Método alternativo también falló")
                except Exception as fallback_error:
                    logger.error(f"Método alternativo falló: {fallback_error}")
                    
                    # Si todo falla, intentar configuración más básica
                    logger.warning("Intentando configuración ultra-básica...")
                    if progress_callback:
                        progress_callback(50, "Último intento con configuración básica...")
                    
                    try:
                        # Configuración mínima
                        minimal_options = {
                            'language': self.language,
                            'force_ocr': True,
                            'invalidate_digital_signatures': True,
                            'optimize': 0,
                            'clean': False,
                            'deskew': False,
                            'remove_background': False,
                            'rotate_pages': False
                        }
                        
                        ocrmypdf.ocr(
                            input_file=temp_input,
                            output_file=output_path,
                            **minimal_options
                        )
                    except Exception as final_error:
                        # Si absolutamente todo falla, devolver error
                        raise Exception(f"Todos los métodos de OCR fallaron: {final_error}")
            
            # Limpiar archivo temporal si se creó
            if temp_input != input_path and os.path.exists(temp_input):
                try:
                    os.unlink(temp_input)
                except:
                    pass
            
            if progress_callback:
                progress_callback(90, "Finalizando...")
            
            # Verificar resultado
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                input_size = os.path.getsize(input_path)
                
                result = {
                    'success': True,
                    'input_path': input_path,
                    'output_path': output_path,
                    'input_size': input_size,
                    'output_size': output_size,
                    'size_change': output_size - input_size,
                    'compression_ratio': round(output_size / input_size, 2) if input_size > 0 else 1.0,
                    'language_used': self.language,
                    'config_used': config
                }
                
                if progress_callback:
                    progress_callback(100, "¡OCR completado exitosamente!")
                
                logger.info(f"OCR completado: {os.path.basename(output_path)} "
                           f"({output_size:,} bytes, ratio: {result['compression_ratio']})")
                
                return result
            else:
                return {
                    'success': False,
                    'error': 'El archivo de salida no se generó',
                    'input_path': input_path,
                    'output_path': output_path
                }
                
        except Exception as e:
            error_msg = f"Error durante procesamiento: {str(e)}"
            logger.error(error_msg)
            
            if progress_callback:
                progress_callback(-1, error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'input_path': input_path,
                'output_path': output_path
            }
    
    def _tesseract_fallback_ocr(self, input_path: str, output_path: str, 
                               progress_callback: Optional[Callable] = None) -> bool:
        """
        Método alternativo usando solo Tesseract cuando OCRmyPDF falla.
        
        Args:
            input_path (str): PDF de entrada
            output_path (str): PDF de salida
            progress_callback (Callable): Función de progreso
            
        Returns:
            bool: True si fue exitoso
        """
        try:
            import fitz
            from PIL import Image
            import tempfile
            import subprocess
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            if progress_callback:
                progress_callback(45, "Convirtiendo PDF a imágenes...")
            
            # Abrir PDF con PyMuPDF
            doc = fitz.open(input_path)
            temp_dir = tempfile.mkdtemp()
            
            ocr_results = []
            
            for page_num in range(len(doc)):
                if progress_callback:
                    progress = 45 + (page_num / len(doc)) * 40
                    progress_callback(progress, f"Procesando página {page_num + 1}/{len(doc)}")
                
                # Convertir página a imagen
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Aumentar resolución
                img_path = os.path.join(temp_dir, f"page_{page_num}.png")
                pix.save(img_path)
                
                # Aplicar OCR con Tesseract
                try:
                    result = subprocess.run([
                        'tesseract', img_path, 
                        os.path.join(temp_dir, f"page_{page_num}"),
                        '-l', self.language,
                        'pdf'
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        pdf_page_path = os.path.join(temp_dir, f"page_{page_num}.pdf")
                        if os.path.exists(pdf_page_path):
                            ocr_results.append(pdf_page_path)
                    
                except Exception as e:
                    logger.warning(f"Error en OCR de página {page_num}: {e}")
            
            doc.close()
            
            if progress_callback:
                progress_callback(85, "Combinando páginas...")
            
            # Combinar PDFs resultantes
            if ocr_results:
                self._combine_pdfs(ocr_results, output_path)
                
                # Limpiar archivos temporales
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error en método alternativo: {e}")
            return False
    
    def _combine_pdfs(self, pdf_list: list, output_path: str):
        """Combina múltiples PDFs en uno solo."""
        try:
            import PyPDF2
            
            writer = PyPDF2.PdfWriter()
            
            for pdf_path in pdf_list:
                if os.path.exists(pdf_path):
                    reader = PyPDF2.PdfReader(pdf_path)
                    for page in reader.pages:
                        writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
        except Exception as e:
            logger.error(f"Error combinando PDFs: {e}")
            raise
            
            # Limpiar archivo temporal si se creó
            if temp_input != input_path and os.path.exists(temp_input):
                try:
                    os.unlink(temp_input)
                except:
                    pass
            
            if progress_callback:
                progress_callback(90, "Finalizando...")
            
            # Verificar resultado
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                input_size = os.path.getsize(input_path)
                
                result = {
                    'success': True,
                    'input_path': input_path,
                    'output_path': output_path,
                    'input_size': input_size,
                    'output_size': output_size,
                    'size_change': output_size - input_size,
                    'compression_ratio': round(output_size / input_size, 2) if input_size > 0 else 1.0,
                    'language_used': self.language,
                    'config_used': config
                }
                
                if progress_callback:
                    progress_callback(100, "¡OCR completado exitosamente!")
                
                logger.info(f"OCR completado: {os.path.basename(output_path)} "
                           f"({output_size:,} bytes, ratio: {result['compression_ratio']})")
                
                return result
            else:
                return {
                    'success': False,
                    'error': 'El archivo de salida no se generó',
                    'input_path': input_path,
                    'output_path': output_path
                }
                
        except Exception as e:
            error_msg = f"Error durante procesamiento: {str(e)}"
            logger.error(error_msg)
            
            if progress_callback:
                progress_callback(-1, error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'input_path': input_path,
                'output_path': output_path
            }
    
    def _handle_encrypted_pdf(self, input_path: str, progress_callback: Optional[Callable] = None) -> str:
        """
        Maneja PDFs cifrados creando una versión temporal descifrada.
        
        Args:
            input_path (str): Ruta del PDF original
            progress_callback (Callable): Función de progreso
            
        Returns:
            str: Ruta del PDF temporal descifrado o el original si no está cifrado
        """
        try:
            import fitz  # PyMuPDF
            import tempfile
            
            if progress_callback:
                progress_callback(5, "Verificando cifrado del PDF...")
            
            # Abrir PDF y verificar cifrado
            doc = fitz.open(input_path)
            
            if not doc.is_encrypted:
                doc.close()
                return input_path  # No está cifrado, usar original
            
            if progress_callback:
                progress_callback(7, "PDF cifrado detectado, descifrando...")
            
            # Intentar descifrar con contraseña vacía
            if doc.authenticate(""):
                # Crear archivo temporal
                temp_dir = tempfile.gettempdir()
                temp_name = f"temp_decrypted_{os.path.basename(input_path)}"
                temp_path = os.path.join(temp_dir, temp_name)
                
                # Guardar versión descifrada
                doc.save(temp_path, encryption=fitz.PDF_ENCRYPT_NONE)
                doc.close()
                
                logger.info(f"PDF descifrado temporalmente: {temp_path}")
                return temp_path
            else:
                doc.close()
                raise Exception("PDF requiere contraseña para descifrar")
                
        except Exception as e:
            logger.error(f"Error al manejar PDF cifrado: {e}")
            return input_path  # Devolver original y dejar que OCRmyPDF maneje el error
    
    def process_pdf_async(self, input_path: str, output_path: str,
                         completion_callback: Callable,
                         progress_callback: Optional[Callable] = None,
                         config: Optional[Dict] = None):
        """
        Procesa un PDF de forma asíncrona en un hilo separado.
        
        Args:
            input_path (str): Ruta del PDF de entrada
            output_path (str): Ruta del PDF de salida
            completion_callback (Callable): Función llamada al completar
            progress_callback (Callable): Función para reportar progreso
            config (Dict): Configuración personalizada
        """
        def worker():
            result = self.process_pdf(input_path, output_path, progress_callback, config)
            completion_callback(result)
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
    
    def _interpret_ocr_error(self, exit_code: int) -> str:
        """
        Interpreta códigos de error de OCRmyPDF.
        
        Args:
            exit_code (int): Código de salida de OCRmyPDF
            
        Returns:
            str: Descripción del error
        """
        error_codes = {
            1: "Error general de OCRmyPDF",
            2: "PDF de entrada inválido o corrupto",
            3: "PDF de entrada cifrado con contraseña",
            4: "Error de Tesseract (posible problema de idioma)",
            5: "Archivo de salida no se pudo escribir",
            6: "PDF ya procesado con OCR",
            7: "Otras limitaciones de entrada",
            8: "PDF no contiene imágenes para procesar",
            15: "Error de tiempo de ejecución o memoria insuficiente"
        }
        
        return error_codes.get(exit_code, f"Error desconocido (código {exit_code})")
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        Obtiene los idiomas soportados.
        
        Returns:
            Dict[str, str]: Diccionario código -> nombre del idioma
        """
        return self.supported_languages.copy()
    
    def set_language(self, language: str) -> bool:
        """
        Cambia el idioma del OCR.
        
        Args:
            language (str): Código del idioma
            
        Returns:
            bool: True si el idioma es válido
        """
        if language in self.supported_languages:
            self.language = language
            logger.info(f"Idioma cambiado a: {self.supported_languages[language]}")
            return True
        else:
            logger.warning(f"Idioma no soportado: {language}")
            return False
    
    def estimate_processing_time(self, pdf_path: str) -> Dict:
        """
        Estima el tiempo de procesamiento basado en el tamaño del archivo.
        
        Args:
            pdf_path (str): Ruta al PDF
            
        Returns:
            Dict: Estimación de tiempo y recursos
        """
        try:
            if not os.path.exists(pdf_path):
                return {'error': 'Archivo no encontrado'}
            
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            
            # Estimaciones basadas en pruebas empíricas
            # Aproximadamente 1-3 MB por minuto dependiendo de la complejidad
            base_time_per_mb = 30  # segundos por MB
            
            if file_size_mb < 1:
                estimated_seconds = 15
                complexity = "Bajo"
            elif file_size_mb < 5:
                estimated_seconds = file_size_mb * base_time_per_mb
                complexity = "Medio"
            elif file_size_mb < 20:
                estimated_seconds = file_size_mb * (base_time_per_mb * 1.5)
                complexity = "Alto"
            else:
                estimated_seconds = file_size_mb * (base_time_per_mb * 2)
                complexity = "Muy Alto"
            
            return {
                'file_size_mb': round(file_size_mb, 2),
                'estimated_seconds': int(estimated_seconds),
                'estimated_minutes': round(estimated_seconds / 60, 1),
                'complexity': complexity,
                'recommendation': self._get_time_recommendation(estimated_seconds)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_time_recommendation(self, seconds: int) -> str:
        """Genera recomendación basada en tiempo estimado."""
        if seconds < 60:
            return "Procesamiento rápido"
        elif seconds < 300:  # 5 minutos
            return "Tiempo moderado - puedes esperar"
        elif seconds < 900:  # 15 minutos
            return "Procesamiento largo - considera hacer otras tareas"
        else:
            return "Procesamiento muy largo - considera partir el archivo"


def test_ocr_processor():
    """Función de prueba para el procesador OCR."""
    processor = OCRProcessor()
    
    # Validar Tesseract
    validation = processor.validate_tesseract()
    print("Validación de Tesseract:")
    for key, value in validation.items():
        print(f"  {key}: {value}")
    
    # Mostrar idiomas disponibles
    languages = processor.get_available_languages()
    print(f"\nIdiomas soportados: {languages}")


if __name__ == "__main__":
    test_ocr_processor()