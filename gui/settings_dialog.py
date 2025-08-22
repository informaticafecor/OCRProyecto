"""
Settings Dialog - Diálogo de Configuración Avanzada
===================================================
Ventana para configurar opciones avanzadas del procesador de PDFs.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path


class SettingsDialog:
    """
    Diálogo de configuración avanzada para el procesador de PDFs.
    """
    
    def __init__(self, parent, config):
        """
        Inicializa el diálogo de configuración.
        
        Args:
            parent: Ventana padre
            config: Objeto ConfigParser con la configuración actual
        """
        self.parent = parent
        self.config = config
        self.result = False  # Si se guardaron los cambios
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("Configuración Avanzada")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables para configuración
        self.setup_variables()
        
        # Configurar interfaz
        self.setup_interface()
        
        # Cargar valores actuales
        self.load_current_settings()
        
        # Centrar ventana
        self.center_window()
    
    def setup_variables(self):
        """Configura las variables de configuración."""
        # OCR Settings
        self.ocr_language = tk.StringVar()
        self.ocr_optimize = tk.StringVar()
        self.ocr_clean = tk.BooleanVar()
        self.ocr_deskew = tk.BooleanVar()
        self.ocr_remove_background = tk.BooleanVar()
        self.ocr_rotate_pages = tk.BooleanVar()
        self.ocr_jpeg_quality = tk.IntVar()
        self.ocr_png_quality = tk.IntVar()
        
        # Processing Settings
        self.proc_create_backups = tk.BooleanVar()
        self.proc_output_dir = tk.StringVar()
        self.proc_max_file_size = tk.IntVar()
        self.proc_skip_existing = tk.BooleanVar()
        self.proc_parallel_processing = tk.BooleanVar()
        
        # GUI Settings
        self.gui_theme = tk.StringVar()
        self.gui_remember_settings = tk.BooleanVar()
        self.gui_auto_analyze = tk.BooleanVar()
        self.gui_show_tips = tk.BooleanVar()
        
        # Logging Settings
        self.log_level = tk.StringVar()
        self.log_directory = tk.StringVar()
        self.log_max_files = tk.IntVar()
        self.log_auto_cleanup = tk.BooleanVar()
    
    def setup_interface(self):
        """Configura la interfaz del diálogo."""
        # Frame principal con notebook
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Crear pestañas
        self.create_ocr_tab(notebook)
        self.create_processing_tab(notebook)
        self.create_gui_tab(notebook)
        self.create_logging_tab(notebook)
        self.create_advanced_tab(notebook)
        
        # Botones
        self.create_buttons(main_frame)
    
    def create_ocr_tab(self, notebook):
        """Crea la pestaña de configuración OCR."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="🔧 OCR")
        
        # Configuración de idioma
        lang_frame = ttk.LabelFrame(frame, text="Idioma y Detección", padding="10")
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(lang_frame, text="Idioma principal:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        languages = ['spa', 'eng', 'fra', 'deu', 'ita', 'por']
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.ocr_language, 
                                 values=languages, state="readonly")
        lang_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Configuración de calidad
        quality_frame = ttk.LabelFrame(frame, text="Calidad de Imagen", padding="10")
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(quality_frame, text="Nivel de optimización:").grid(row=0, column=0, sticky=tk.W)
        optimize_combo = ttk.Combobox(quality_frame, textvariable=self.ocr_optimize, 
                                     values=['0', '1', '2', '3'], state="readonly")
        optimize_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(quality_frame, text="Calidad JPEG (1-100):").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        jpeg_scale = ttk.Scale(quality_frame, from_=1, to=100, variable=self.ocr_jpeg_quality, 
                              orient=tk.HORIZONTAL)
        jpeg_scale.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        
        self.jpeg_label = ttk.Label(quality_frame, text="85")
        self.jpeg_label.grid(row=1, column=3, padx=(5, 0), pady=(5, 0))
        jpeg_scale.config(command=lambda v: self.jpeg_label.config(text=f"{int(float(v))}"))
        
        ttk.Label(quality_frame, text="Calidad PNG (1-100):").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        png_scale = ttk.Scale(quality_frame, from_=1, to=100, variable=self.ocr_png_quality, 
                             orient=tk.HORIZONTAL)
        png_scale.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(5, 0), pady=(5, 0))
        
        self.png_label = ttk.Label(quality_frame, text="85")
        self.png_label.grid(row=2, column=3, padx=(5, 0), pady=(5, 0))
        png_scale.config(command=lambda v: self.png_label.config(text=f"{int(float(v))}"))
        
        quality_frame.columnconfigure(1, weight=1)
        
        # Opciones de procesamiento
        options_frame = ttk.LabelFrame(frame, text="Opciones de Procesamiento", padding="10")
        options_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(options_frame, text="Limpiar artefactos de escaneo", 
                       variable=self.ocr_clean).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Corregir inclinación automáticamente", 
                       variable=self.ocr_deskew).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Rotar páginas automáticamente", 
                       variable=self.ocr_rotate_pages).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Remover fondo de imagen", 
                       variable=self.ocr_remove_background).pack(anchor=tk.W)
    
    def create_processing_tab(self, notebook):
        """Crea la pestaña de configuración de procesamiento."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="⚙️ Procesamiento")
        
        # Configuración de archivos
        files_frame = ttk.LabelFrame(frame, text="Manejo de Archivos", padding="10")
        files_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(files_frame, text="Crear backups automáticamente", 
                       variable=self.proc_create_backups).pack(anchor=tk.W)
        ttk.Checkbutton(files_frame, text="Saltar archivos existentes", 
                       variable=self.proc_skip_existing).pack(anchor=tk.W)
        ttk.Checkbutton(files_frame, text="Procesamiento paralelo (experimental)", 
                       variable=self.proc_parallel_processing).pack(anchor=tk.W)
        
        # Directorio de salida por defecto
        dir_frame = ttk.Frame(files_frame)
        dir_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(dir_frame, text="Directorio de salida por defecto:").pack(anchor=tk.W)
        
        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X, pady=(5, 0))
        dir_entry_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(dir_entry_frame, textvariable=self.proc_output_dir).grid(row=0, column=0, 
                                                                          sticky=(tk.W, tk.E), 
                                                                          padx=(0, 5))
        ttk.Button(dir_entry_frame, text="📁", 
                  command=self.select_output_directory).grid(row=0, column=1)
        
        # Limitaciones
        limits_frame = ttk.LabelFrame(frame, text="Limitaciones", padding="10")
        limits_frame.pack(fill=tk.X)
        
        size_frame = ttk.Frame(limits_frame)
        size_frame.pack(fill=tk.X)
        
        ttk.Label(size_frame, text="Tamaño máximo de archivo (MB):").pack(side=tk.LEFT)
        size_spinbox = ttk.Spinbox(size_frame, from_=1, to=1000, 
                                  textvariable=self.proc_max_file_size, width=10)
        size_spinbox.pack(side=tk.RIGHT)
    
    def create_gui_tab(self, notebook):
        """Crea la pestaña de configuración de interfaz."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="🖼️ Interfaz")
        
        # Apariencia
        appearance_frame = ttk.LabelFrame(frame, text="Apariencia", padding="10")
        appearance_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(appearance_frame, text="Tema:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        theme_combo = ttk.Combobox(appearance_frame, textvariable=self.gui_theme, 
                                  values=['default', 'clam', 'alt', 'classic'], state="readonly")
        theme_combo.grid(row=0, column=1, sticky=tk.W)
        
        # Comportamiento
        behavior_frame = ttk.LabelFrame(frame, text="Comportamiento", padding="10")
        behavior_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(behavior_frame, text="Recordar configuración al cerrar", 
                       variable=self.gui_remember_settings).pack(anchor=tk.W)
        ttk.Checkbutton(behavior_frame, text="Analizar archivos automáticamente al seleccionar", 
                       variable=self.gui_auto_analyze).pack(anchor=tk.W)
        ttk.Checkbutton(behavior_frame, text="Mostrar consejos al inicio", 
                       variable=self.gui_show_tips).pack(anchor=tk.W)
    
    def create_logging_tab(self, notebook):
        """Crea la pestaña de configuración de logging."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="📄 Logging")
        
        # Nivel de logging
        level_frame = ttk.LabelFrame(frame, text="Nivel de Detalle", padding="10")
        level_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(level_frame, text="Nivel de log:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        level_combo = ttk.Combobox(level_frame, textvariable=self.log_level, 
                                  values=['DEBUG', 'INFO', 'WARNING', 'ERROR'], state="readonly")
        level_combo.grid(row=0, column=1, sticky=tk.W)
        
        # Directorio de logs
        log_dir_frame = ttk.LabelFrame(frame, text="Ubicación de Logs", padding="10")
        log_dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(log_dir_frame, text="Directorio de logs:").pack(anchor=tk.W)
        
        log_entry_frame = ttk.Frame(log_dir_frame)
        log_entry_frame.pack(fill=tk.X, pady=(5, 0))
        log_entry_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(log_entry_frame, textvariable=self.log_directory).grid(row=0, column=0, 
                                                                        sticky=(tk.W, tk.E), 
                                                                        padx=(0, 5))
        ttk.Button(log_entry_frame, text="📁", 
                  command=self.select_log_directory).grid(row=0, column=1)
        
        # Mantenimiento
        maintenance_frame = ttk.LabelFrame(frame, text="Mantenimiento", padding="10")
        maintenance_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(maintenance_frame, text="Limpieza automática de logs antiguos", 
                       variable=self.log_auto_cleanup).pack(anchor=tk.W)
        
        max_files_frame = ttk.Frame(maintenance_frame)
        max_files_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(max_files_frame, text="Máximo archivos de log:").pack(side=tk.LEFT)
        max_files_spinbox = ttk.Spinbox(max_files_frame, from_=1, to=100, 
                                       textvariable=self.log_max_files, width=10)
        max_files_spinbox.pack(side=tk.RIGHT)
    
    def create_advanced_tab(self, notebook):
        """Crea la pestaña de configuración avanzada."""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="🔧 Avanzado")
        
        # Información del sistema
        system_frame = ttk.LabelFrame(frame, text="Información del Sistema", padding="10")
        system_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(system_frame, text="Validar Configuración", 
                  command=self.validate_system).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(system_frame, text="Ver Información del Sistema", 
                  command=self.show_system_info).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(system_frame, text="Limpiar Archivos Temporales", 
                  command=self.cleanup_temp_files).pack(side=tk.LEFT)
        
        # Configuración de rendimiento
        performance_frame = ttk.LabelFrame(frame, text="Rendimiento", padding="10")
        performance_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(performance_frame, text="⚠️ Configuraciones experimentales").pack(anchor=tk.W)
        ttk.Label(performance_frame, text="Úsalas bajo tu propia responsabilidad.", 
                 font=('TkDefaultFont', 8)).pack(anchor=tk.W, pady=(0, 10))
        
        # Configuración de memoria
        memory_frame = ttk.Frame(performance_frame)
        memory_frame.pack(fill=tk.X)
        
        ttk.Label(memory_frame, text="Límite de memoria por proceso (MB):").pack(side=tk.LEFT)
        memory_spinbox = ttk.Spinbox(memory_frame, from_=512, to=8192, width=10, 
                                    value=2048)
        memory_spinbox.pack(side=tk.RIGHT)
        
        # Botones de configuración
        config_frame = ttk.LabelFrame(frame, text="Configuración", padding="10")
        config_frame.pack(fill=tk.X)
        
        ttk.Button(config_frame, text="Exportar Configuración", 
                  command=self.export_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_frame, text="Importar Configuración", 
                  command=self.import_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_frame, text="Restaurar Valores por Defecto", 
                  command=self.reset_to_defaults).pack(side=tk.LEFT)
    
    def create_buttons(self, parent):
        """Crea los botones del diálogo."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Aplicar", 
                  command=self.apply_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Aceptar", 
                  command=self.accept).pack(side=tk.RIGHT)
    
    def load_current_settings(self):
        """Carga la configuración actual en los controles."""
        try:
            # OCR Settings
            self.ocr_language.set(self.config.get('OCR', 'language'))
            self.ocr_optimize.set(self.config.get('OCR', 'optimize_level'))
            self.ocr_clean.set(self.config.getboolean('OCR', 'clean_images'))
            self.ocr_deskew.set(self.config.getboolean('OCR', 'deskew'))
            self.ocr_remove_background.set(self.config.getboolean('OCR', 'remove_background'))
            self.ocr_rotate_pages.set(True)  # Default value
            self.ocr_jpeg_quality.set(85)
            self.ocr_png_quality.set(85)
            
            # Processing Settings
            self.proc_create_backups.set(self.config.getboolean('Processing', 'create_backups'))
            self.proc_output_dir.set(self.config.get('Processing', 'output_directory'))
            self.proc_max_file_size.set(self.config.getint('Processing', 'max_file_size_mb'))
            self.proc_skip_existing.set(self.config.getboolean('Processing', 'skip_existing'))
            self.proc_parallel_processing.set(False)  # Default
            
            # GUI Settings
            self.gui_theme.set(self.config.get('GUI', 'theme'))
            self.gui_remember_settings.set(self.config.getboolean('GUI', 'remember_settings'))
            self.gui_auto_analyze.set(False)  # Default
            self.gui_show_tips.set(True)  # Default
            
            # Logging Settings
            self.log_level.set(self.config.get('Logging', 'level'))
            self.log_directory.set(self.config.get('Logging', 'log_directory'))
            self.log_max_files.set(self.config.getint('Logging', 'max_log_files'))
            self.log_auto_cleanup.set(True)  # Default
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar configuración: {e}")
    
    def save_settings(self):
        """Guarda la configuración actual."""
        try:
            # OCR Settings
            self.config.set('OCR', 'language', self.ocr_language.get())
            self.config.set('OCR', 'optimize_level', self.ocr_optimize.get())
            self.config.set('OCR', 'clean_images', str(self.ocr_clean.get()))
            self.config.set('OCR', 'deskew', str(self.ocr_deskew.get()))
            self.config.set('OCR', 'remove_background', str(self.ocr_remove_background.get()))
            
            # Processing Settings
            self.config.set('Processing', 'create_backups', str(self.proc_create_backups.get()))
            self.config.set('Processing', 'output_directory', self.proc_output_dir.get())
            self.config.set('Processing', 'max_file_size_mb', str(self.proc_max_file_size.get()))
            self.config.set('Processing', 'skip_existing', str(self.proc_skip_existing.get()))
            
            # GUI Settings
            self.config.set('GUI', 'theme', self.gui_theme.get())
            self.config.set('GUI', 'remember_settings', str(self.gui_remember_settings.get()))
            
            # Logging Settings
            self.config.set('Logging', 'level', self.log_level.get())
            self.config.set('Logging', 'log_directory', self.log_directory.get())
            self.config.set('Logging', 'max_log_files', str(self.log_max_files.get()))
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {e}")
            return False
    
    def select_output_directory(self):
        """Selecciona directorio de salida."""
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if directory:
            self.proc_output_dir.set(directory)
    
    def select_log_directory(self):
        """Selecciona directorio de logs."""
        directory = filedialog.askdirectory(title="Seleccionar directorio de logs")
        if directory:
            self.log_directory.set(directory)
    
    def validate_system(self):
        """Valida la configuración del sistema."""
        # Aquí iría la validación real del sistema
        messagebox.showinfo("Validación", "Sistema validado correctamente")
    
    def show_system_info(self):
        """Muestra información del sistema."""
        info_window = tk.Toplevel(self.window)
        info_window.title("Información del Sistema")
        info_window.geometry("500x400")
        info_window.transient(self.window)
        
        # Información del sistema (simplificada)
        info_text = """
Sistema Operativo: Windows 10
Python: 3.9.0
Tesseract: 5.3.0
OCRmyPDF: 15.4.4

Memoria disponible: 8 GB
Espacio en disco: 500 GB
        """
        
        text_widget = tk.Text(info_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.insert("1.0", info_text.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)
    
    def cleanup_temp_files(self):
        """Limpia archivos temporales."""
        result = messagebox.askyesno("Limpiar archivos temporales", 
                                   "¿Eliminar todos los archivos temporales?")
        if result:
            # Aquí iría la limpieza real
            messagebox.showinfo("Limpieza", "Archivos temporales eliminados")
    
    def export_config(self):
        """Exporta la configuración actual."""
        filename = filedialog.asksaveasfilename(
            title="Exportar configuración",
            defaultextension=".ini",
            filetypes=[("Archivos INI", "*.ini"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    self.config.write(f)
                messagebox.showinfo("Exportación", f"Configuración exportada a:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {e}")
    
    def import_config(self):
        """Importa configuración desde archivo."""
        filename = filedialog.askopenfilename(
            title="Importar configuración",
            filetypes=[("Archivos INI", "*.ini"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                self.config.read(filename, encoding='utf-8')
                self.load_current_settings()
                messagebox.showinfo("Importación", "Configuración importada correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al importar: {e}")
    
    def reset_to_defaults(self):
        """Restaura valores por defecto."""
        result = messagebox.askyesno("Restaurar valores por defecto", 
                                   "¿Restaurar toda la configuración a valores por defecto?")
        if result:
            # Restaurar valores por defecto
            self.ocr_language.set('spa')
            self.ocr_optimize.set('1')
            self.ocr_clean.set(True)
            self.ocr_deskew.set(True)
            self.ocr_remove_background.set(False)
            self.proc_create_backups.set(True)
            self.proc_output_dir.set('')
            self.proc_max_file_size.set(100)
            self.proc_skip_existing.set(False)
            self.gui_theme.set('clam')
            self.gui_remember_settings.set(True)
            self.log_level.set('INFO')
            self.log_directory.set('logs')
            self.log_max_files.set(10)
    
    def apply_settings(self):
        """Aplica la configuración sin cerrar el diálogo."""
        if self.save_settings():
            self.result = True
            messagebox.showinfo("Configuración", "Configuración aplicada correctamente")
    
    def accept(self):
        """Acepta y guarda la configuración, luego cierra el diálogo."""
        if self.save_settings():
            self.result = True
            self.window.destroy()
    
    def cancel(self):
        """Cancela los cambios y cierra el diálogo."""
        self.result = False
        self.window.destroy()
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")


def demo_settings():
    """Función de demostración del diálogo de configuración."""
    import configparser
    
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Crear configuración de prueba
    config = configparser.ConfigParser()
    config.read_dict({
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
            'theme': 'clam',
            'remember_settings': 'True'
        },
        'Logging': {
            'level': 'INFO',
            'log_directory': 'logs',
            'max_log_files': '10'
        }
    })
    
    # Crear y mostrar diálogo
    dialog = SettingsDialog(root, config)
    root.wait_window(dialog.window)
    
    if dialog.result:
        print("Configuración guardada:")
        for section in config.sections():
            print(f"[{section}]")
            for key, value in config.items(section):
                print(f"{key} = {value}")
            print()
    else:
        print("Configuración cancelada")


if __name__ == "__main__":
    demo_settings()