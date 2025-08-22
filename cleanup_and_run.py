"""
Cleanup and Run - Script de limpieza y ejecución
===============================================
Script para limpiar posibles conflictos y ejecutar la aplicación.
"""

import os
import sys
import shutil
from pathlib import Path

def cleanup_directories():
    """Limpia y recrea directorios problemáticos."""
    base_dir = Path(__file__).parent
    problem_dirs = ['assets', 'logs', 'temp']
    
    print("🧹 Limpiando directorios...")
    
    for dir_name in problem_dirs:
        dir_path = base_dir / dir_name
        
        # Si existe como archivo, eliminarlo
        if dir_path.exists() and not dir_path.is_dir():
            print(f"🗑️ Eliminando archivo conflictivo: {dir_path}")
            try:
                dir_path.unlink()
            except Exception as e:
                print(f"⚠️ No se pudo eliminar {dir_path}: {e}")
        
        # Si existe como directorio, verificar que esté bien
        elif dir_path.exists() and dir_path.is_dir():
            print(f"✅ Directorio OK: {dir_path}")
        
        # Crear directorio si no existe
        else:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"📁 Directorio creado: {dir_path}")
            except Exception as e:
                print(f"⚠️ Error creando {dir_path}: {e}")
    
    # Crear subdirectorios de assets
    assets_dir = base_dir / 'assets'
    if assets_dir.exists():
        for subdir in ['icons', 'styles']:
            subdir_path = assets_dir / subdir
            try:
                subdir_path.mkdir(exist_ok=True)
                print(f"📁 Subdirectorio creado: {subdir_path}")
            except Exception as e:
                print(f"⚠️ Error creando {subdir_path}: {e}")

def check_files():
    """Verifica que los archivos principales existan."""
    base_dir = Path(__file__).parent
    required_files = [
        'main.py',
        'requirements.txt',
        'src/pdf_analyzer.py',
        'src/ocr_processor.py', 
        'src/pdf_processor.py',
        'src/utils.py',
        'gui/main_window.py',
        'gui/progress_dialog.py',
        'gui/settings_dialog.py'
    ]
    
    print("\n📋 Verificando archivos...")
    missing_files = []
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Faltan {len(missing_files)} archivos. La aplicación podría no funcionar correctamente.")
        return False
    
    print("\n✅ Todos los archivos principales están presentes")
    return True

def create_init_files():
    """Crea archivos __init__.py faltantes."""
    base_dir = Path(__file__).parent
    init_dirs = ['src', 'gui']
    
    print("\n📝 Creando archivos __init__.py...")
    
    for dir_name in init_dirs:
        init_file = base_dir / dir_name / '__init__.py'
        if not init_file.exists():
            try:
                init_file.parent.mkdir(exist_ok=True)
                init_file.write_text(f'# {dir_name} module\n', encoding='utf-8')
                print(f"📝 Creado: {init_file}")
            except Exception as e:
                print(f"⚠️ Error creando {init_file}: {e}")
        else:
            print(f"✅ Existe: {init_file}")

def main():
    """Función principal del script de limpieza."""
    print("🛠️ PDF OCR Processor - Script de Limpieza y Verificación")
    print("=" * 60)
    
    # Limpiar directorios
    cleanup_directories()
    
    # Crear archivos __init__.py
    create_init_files()
    
    # Verificar archivos
    files_ok = check_files()
    
    print("\n" + "=" * 60)
    
    if files_ok:
        print("✅ Sistema listo para ejecutar")
        
        # Preguntar si ejecutar la aplicación
        response = input("\n¿Ejecutar la aplicación ahora? (s/n): ").lower().strip()
        
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            print("\n🚀 Ejecutando aplicación...")
            try:
                # Ejecutar main.py
                import subprocess
                result = subprocess.run([sys.executable, 'main.py'], cwd=Path(__file__).parent)
                sys.exit(result.returncode)
            except Exception as e:
                print(f"❌ Error al ejecutar: {e}")
                print("💡 Intenta ejecutar manualmente: python main.py")
        else:
            print("👍 Limpieza completada. Ejecuta: python main.py")
    else:
        print("❌ Sistema no está completo. Verifica los archivos faltantes.")
        input("\nPresiona Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        input("Presiona Enter para salir...")
        sys.exit(1)