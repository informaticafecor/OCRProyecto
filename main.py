"""
PDF OCR Processor - Archivo Principal
====================================
Aplicación con interfaz gráfica para procesar PDFs con OCR automático.

Uso: python main.py

Autor: Tu Nombrewwwwww
Fecha: Agosto 2025
Versión: 1.0
""" 


import sys
import os
import logging
from pathlib import Path

# Agregar el directorio src al path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'gui'))

# Configurar logging temprano
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_directories():
    """Crear directorios necesarios si no existen."""
    base_dir = Path(__file__).parent
    directories = ['logs', 'temp', 'assets', 'assets/icons', 'assets/styles']
    
    for directory in directories:
        dir_path = base_dir / directory
        try:
            # Verificar si ya existe como archivo (no directorio)
            if dir_path.exists() and not dir_path.is_dir():
                print(f"⚠️ Advertencia: {dir_path} existe como archivo, renombrando...")
                backup_path = dir_path.with_suffix(dir_path.suffix + '.backup')
                dir_path.rename(backup_path)
            
            dir_path.mkdir(parents=True, exist_ok=True)
            
        except FileExistsError:
            # Si aún hay error, intentar un enfoque diferente
            if not dir_path.exists():
                print(f"⚠️ Problema creando {directory}, continuando...")
        except Exception as e:
            print(f"⚠️ Error creando directorio {directory}: {e}")
            # Continuar sin este directorio

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas."""
    required_modules = [
        ('tkinter', 'tkinter'),
        ('PyPDF2', 'PyPDF2'), 
        ('fitz', 'PyMuPDF'),
        ('ocrmypdf', 'ocrmypdf'),
        ('PIL', 'Pillow')
    ]
    
    missing_modules = []
    
    for module_import, module_name in required_modules:
        try:
            __import__(module_import)
            print(f"✅ {module_name}")
        except ImportError:
            missing_modules.append(module_name)
            print(f"❌ {module_name}")
    
    if missing_modules:
        print("\n❌ Módulos faltantes:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\n📦 Instala las dependencias:")
        print("   pip install -r requirements.txt")
        return False
    
    print("\n✅ Todas las dependencias están instaladas")
    return True

def main():
    """Función principal de la aplicación."""
    print("🚀 Iniciando PDF OCR Processor...")
    
    try:
        # Configurar directorios
        setup_directories()
        
        # Verificar dependencias
        if not check_dependencies():
            input("\nPresiona Enter para salir...")
            sys.exit(1)
        
        # Importar y ejecutar la interfaz gráfica
        print("🖼️ Iniciando interfaz gráfica...")
        
        try:
            # Usar interfaz principal
            from gui.main_window import PDFOCRApp
            app = PDFOCRApp()
            app.run()
        except ImportError as e:
            print(f"❌ Error al importar interfaz: {e}")
            print("🔧 Verifica que todos los archivos estén en su lugar")
            
            # Intentar importación alternativa
            print("🔄 Intentando importación alternativa...")
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))
                from main_window import PDFOCRApp
                app = PDFOCRApp()
                app.run()
            except Exception as e2:
                print(f"❌ Error en importación alternativa: {e2}")
                input("\nPresiona Enter para salir...")
                sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        logging.exception("Error crítico en main")
        input("\nPresiona Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main()