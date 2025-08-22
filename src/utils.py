"""
Utils - Utilidades Generales
============================
Funciones de utilidad para el procesador de PDFs.
"""

import os
import shutil
import logging
from typing import Optional, Tuple, List
from pathlib import Path
from datetime import datetime
import configparser

logger = logging.getLogger(__name__)


def create_backup(file_path: str, backup_dir: Optional[str] = None) -> Optional[str]:
    """
    Crea una copia de seguridad de un archivo.
    
    Args:
        file_path (str): Ruta del archivo original
        backup_dir (str): Directorio de backup (opcional)
        
    Returns:
        str: Ruta del archivo de backup o None si falló
    """
    try:
        source_file = Path(file_path)
        
        if not source_file.exists():
            logger.error(f"Archivo no existe para backup: {file_path}")
            return None
        
        # Determinar directorio de backup
        if backup_dir:
            backup_path = Path(backup_dir)
        else:
            backup_path = source_file.parent / "backups"
        
        backup_path.mkdir(exist_ok=True)
        
        # Generar nombre único con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{source_file.stem}_backup_{timestamp}{source_file.suffix}"
        backup_file = backup_path / backup_filename
        
        # Copiar archivo
        shutil.copy2(str(source_file), str(backup_file))
        
        logger.info(f"Backup creado: {backup_file}")
        return str(backup_file)
        
    except Exception as e:
        logger.error(f"Error al crear backup de {file_path}: {str(e)}")
        return None


def generate_output_filename(input_path: str, output_dir: Optional[Path] = None,
                           suffix: str = "_processed") -> str:
    """
    Genera un nombre de archivo de salida único.
    
    Args:
        input_path (str): Ruta del archivo de entrada
        output_dir (Path): Directorio de salida
        suffix (str): Sufijo a agregar al nombre
        
    Returns:
        str: Ruta completa del archivo de salida
    """
    input_file = Path(input_path)
    
    # Determinar directorio de salida
    if output_dir:
        output_directory = output_dir
    else:
        output_directory = input_file.parent
    
    # Generar nombre base
    base_name = input_file.stem + suffix
    output_path = output_directory / f"{base_name}{input_file.suffix}"
    
    # Asegurar que el nombre sea único
    counter = 1
    while output_path.exists():
        unique_name = f"{base_name}_{counter}{input_file.suffix}"
        output_path = output_directory / unique_name
        counter += 1
    
    return str(output_path)


def validate_paths(*paths: str) -> Tuple[bool, List[str]]:
    """
    Valida múltiples rutas de archivos o directorios.
    
    Args:
        *paths: Rutas a validar
        
    Returns:
        Tuple[bool, List[str]]: (todas_válidas, lista_de_errores)
    """
    errors = []
    
    for path in paths:
        if not path:
            errors.append("Ruta vacía proporcionada")
            continue
            
        path_obj = Path(path)
        
        if not path_obj.exists():
            errors.append(f"No existe: {path}")
        elif path_obj.is_file() and not path.lower().endswith('.pdf'):
            errors.append(f"No es un archivo PDF: {path}")
        elif not os.access(path, os.R_OK):
            errors.append(f"Sin permisos de lectura: {path}")
    
    return len(errors) == 0, errors


def format_file_size(size_bytes: int) -> str:
    """
    Formatea el tamaño de archivo en unidades legibles.
    
    Args:
        size_bytes (int): Tamaño en bytes
        
    Returns:
        str: Tamaño formateado
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def format_duration(seconds: float) -> str:
    """
    Formatea duración en formato legible.
    
    Args:
        seconds (float): Duración en segundos
        
    Returns:
        str: Duración formateada
    """
    if seconds < 1:
        return f"{int(seconds * 1000)} ms"
    elif seconds < 60:
        return f"{seconds:.1f} s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def setup_logging(log_dir: str = "logs", log_level: str = "INFO") -> str:
    """
    Configura el sistema de logging.
    
    Args:
        log_dir (str): Directorio para archivos de log
        log_level (str): Nivel de logging
        
    Returns:
        str: Ruta del archivo de log
    """
    # Crear directorio de logs
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"pdf_processor_{timestamp}.log"
    
    # Configurar formato
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(str(log_file), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger.info(f"Sistema de logging configurado: {log_file}")
    return str(log_file)


def load_config(config_path: str = "config.ini") -> configparser.ConfigParser:
    """
    Carga configuración desde archivo INI.
    
    Args:
        config_path (str): Ruta del archivo de configuración
        
    Returns:
        configparser.ConfigParser: Objeto de configuración
    """
    config = configparser.ConfigParser()
    
    # Configuración por defecto
    default_config = {
        'OCR': {
            'language': 'spa',
            'optimize_level': '1',
            'clean_images': 'True',
            'deskew': 'True',
            'remove_background': 'False'
        },
        'Processing': {
            'create_backups': 'True',
            'output_directory': '',
            'max_file_size_mb': '100',
            'skip_existing': 'False'
        },
        'GUI': {
            'theme': 'default',
            'window_width': '800',
            'window_height': '600',
            'remember_settings': 'True'
        },
        'Logging': {
            'level': 'INFO',
            'log_directory': 'logs',
            'max_log_files': '10'
        }
    }
    
    # Cargar configuración por defecto
    config.read_dict(default_config)
    
    # Intentar cargar configuración del archivo
    if os.path.exists(config_path):
        try:
            config.read(config_path, encoding='utf-8')
            logger.info(f"Configuración cargada desde: {config_path}")
        except Exception as e:
            logger.warning(f"Error al cargar configuración: {e}. Usando valores por defecto.")
    else:
        logger.info("Archivo de configuración no encontrado. Usando valores por defecto.")
    
    return config


def save_config(config: configparser.ConfigParser, config_path: str = "config.ini") -> bool:
    """
    Guarda configuración en archivo INI.
    
    Args:
        config (configparser.ConfigParser): Objeto de configuración
        config_path (str): Ruta del archivo de configuración
        
    Returns:
        bool: True si se guardó exitosamente
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as config_file:
            config.write(config_file)
        
        logger.info(f"Configuración guardada en: {config_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error al guardar configuración: {e}")
        return False


def get_pdf_files(directory: str, recursive: bool = False) -> List[str]:
    """
    Obtiene lista de archivos PDF en un directorio.
    
    Args:
        directory (str): Directorio a escanear
        recursive (bool): Buscar recursivamente en subdirectorios
        
    Returns:
        List[str]: Lista de rutas de archivos PDF
    """
    pdf_files = []
    directory_path = Path(directory)
    
    if not directory_path.exists() or not directory_path.is_dir():
        logger.error(f"Directorio no válido: {directory}")
        return []
    
    try:
        if recursive:
            pattern = "**/*.pdf"
            pdf_files = [str(f) for f in directory_path.rglob("*.pdf")]
        else:
            pdf_files = [str(f) for f in directory_path.glob("*.pdf")]
        
        pdf_files.sort()  # Ordenar alfabéticamente
        
        logger.info(f"Encontrados {len(pdf_files)} archivos PDF en {directory}")
        return pdf_files
        
    except Exception as e:
        logger.error(f"Error al buscar archivos PDF: {e}")
        return []


def cleanup_temp_files(temp_dir: str = "temp", max_age_hours: int = 24) -> int:
    """
    Limpia archivos temporales antiguos.
    
    Args:
        temp_dir (str): Directorio de archivos temporales
        max_age_hours (int): Edad máxima en horas
        
    Returns:
        int: Número de archivos eliminados
    """
    try:
        temp_path = Path(temp_dir)
        
        if not temp_path.exists():
            return 0
        
        current_time = datetime.now()
        max_age_seconds = max_age_hours * 3600
        files_deleted = 0
        
        for file_path in temp_path.glob("*"):
            if file_path.is_file():
                file_age = current_time.timestamp() - file_path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                        files_deleted += 1
                        logger.debug(f"Archivo temporal eliminado: {file_path}")
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar {file_path}: {e}")
        
        if files_deleted > 0:
            logger.info(f"Limpieza completada: {files_deleted} archivos temporales eliminados")
        
        return files_deleted
        
    except Exception as e:
        logger.error(f"Error durante limpieza de archivos temporales: {e}")
        return 0


def create_directory_structure():
    """Crea la estructura de directorios necesaria para la aplicación."""
    base_dir = Path.cwd()
    directories = [
        'src',
        'gui', 
        'logs',
        'temp',
        'assets/icons',
        'assets/styles',
        'backups'
    ]
    
    created_dirs = []
    
    for directory in directories:
        dir_path = base_dir / directory
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                created_dirs.append(str(dir_path))
                logger.debug(f"Directorio creado: {dir_path}")
            except Exception as e:
                logger.error(f"Error al crear directorio {dir_path}: {e}")
    
    if created_dirs:
        logger.info(f"Estructura de directorios creada: {len(created_dirs)} directorios")
    
    return created_dirs


def sanitize_filename(filename: str) -> str:
    """
    Limpia un nombre de archivo eliminando caracteres no válidos.
    
    Args:
        filename (str): Nombre de archivo original
        
    Returns:
        str: Nombre de archivo limpio
    """
    # Caracteres no permitidos en nombres de archivo
    invalid_chars = '<>:"/\\|?*'
    
    # Reemplazar caracteres inválidos
    clean_name = filename
    for char in invalid_chars:
        clean_name = clean_name.replace(char, '_')
    
    # Eliminar espacios múltiples y al inicio/final
    clean_name = ' '.join(clean_name.split())
    
    # Limitar longitud
    if len(clean_name) > 200:
        clean_name = clean_name[:200]
    
    return clean_name


def get_system_info() -> dict:
    """
    Obtiene información del sistema para diagnóstico.
    
    Returns:
        dict: Información del sistema
    """
    import platform
    import sys
    
    info = {
        'platform': platform.platform(),
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': sys.version,
        'python_executable': sys.executable,
        'working_directory': str(Path.cwd())
    }
    
    # Información de memoria (si está disponible)
    try:
        import psutil
        memory = psutil.virtual_memory()
        info['total_memory_gb'] = round(memory.total / (1024**3), 2)
        info['available_memory_gb'] = round(memory.available / (1024**3), 2)
        info['cpu_count'] = psutil.cpu_count()
    except ImportError:
        info['memory_info'] = 'psutil no disponible'
    
    return info


def test_utils():
    """Función de prueba para las utilidades."""
    print("🧪 Probando utilidades...")
    
    # Probar formateo de tamaños
    sizes = [0, 512, 1024, 1048576, 1073741824]
    print("\n📏 Formateo de tamaños:")
    for size in sizes:
        print(f"  {size} bytes = {format_file_size(size)}")
    
    # Probar formateo de duración
    durations = [0.5, 5, 65, 3665]
    print("\n⏱️ Formateo de duración:")
    for duration in durations:
        print(f"  {duration} segundos = {format_duration(duration)}")
    
    # Probar limpieza de nombres
    filenames = ["archivo normal.pdf", "archivo<con>caracteres:inválidos.pdf", "   espacios   múltiples   .pdf"]
    print("\n🧹 Limpieza de nombres:")
    for filename in filenames:
        clean = sanitize_filename(filename)
        print(f"  '{filename}' -> '{clean}'")
    
    # Información del sistema
    print("\n💻 Información del sistema:")
    sys_info = get_system_info()
    for key, value in sys_info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    test_utils()