"""
Main Window - Interfaz Simplificada y Corregida
==============================================
Versión simplificada y más intuitiva de la interfaz gráfica.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading
from pathlib import Path
from datetime import datetime
import logging

# Agregar directorios al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pdf_processor import PDFProcessor
from utils import format_file_size, format_duration, load_config, save_config
from progress_dialog import ProgressDialog

logger = logging.getLogger(__name__)


class PDFOCRApp:
    """
    Aplicación simplificada con interfaz más intuitiva para procesamiento de PDFs con OCR.
    """
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.root = tk.Tk()
        self.root.title("📄 PDF OCR Processor")
        self.root.geometry("800x600")  # MÁS GRANDE
        self.root.minsize(700, 500)   # MÍNIMO MÁS GRANDE
        
        # Variables de estado
        self.selected_files = []
        self.current_language = tk.StringVar(value='spa')
        self.processing_active = False
        
        # Configurar automáticamente carpeta de Descargas
        import os
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_directory = tk.StringVar(value=downloads_path)
        
        # Cargar configuración
        self.config = load_config()
        self.load_settings_from_config()
        
        # Inicializar procesador con Downloads como directorio por defecto
        self.processor = PDFProcessor(
            language=self.current_language.get(),
            output_dir=Path(downloads_path)
        )
        
        # Configurar interfaz
        self.setup_gui()
        
        # Validar sistema al inicio
        self.validate_system()
        
        logger.info("Aplicación simplificada inicializada correctamente")
    
    def setup_gui(self):
        """Configura la interfaz gráfica simplificada."""
        # Configurar estilo moderno
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores modernos
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2C3E50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), foreground='#7F8C8D')
        style.configure('Success.TLabel', foreground='#27AE60')
        style.configure('Error.TLabel', foreground='#E74C3C')
        style.configure('Big.TButton', font=('Segoe UI', 12, 'bold'), padding=10)
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === HEADER ===
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Título principal
        title_label = ttk.Label(header_frame, text="📄 PDF OCR Processor", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Convierte PDFs escaneados en documentos buscables", 
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        # === ZONA DE ARCHIVOS ===
        files_section = ttk.LabelFrame(main_frame, text="📁 Tus Archivos PDF", 
                                      padding="15")
        files_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Zona de arrastrar y soltar (MEJORADA)
        self.drop_frame = tk.Frame(files_section, bg='#ECF0F1', relief='solid', bd=2, height=120)
        self.drop_frame.pack(fill=tk.X, pady=(0, 10))
        self.drop_frame.pack_propagate(False)  # Mantener altura fija
        
        drop_label = tk.Label(self.drop_frame, 
                             text="🗂️ Arrastra archivos PDF aquí\no haz clic para seleccionar", 
                             bg='#ECF0F1', font=('Segoe UI', 14, 'bold'), 
                             fg='#7F8C8D', cursor="hand2")
        drop_label.pack(expand=True)
        drop_label.bind("<Button-1>", lambda e: self.select_files())
        
        # Lista de archivos seleccionados
        self.files_listbox = tk.Listbox(files_section, height=4, 
                                       font=('Segoe UI', 9))
        self.files_listbox.pack(fill=tk.X, pady=(10, 0))
        
        # Solo botón de limpiar (SIMPLIFICADO)
        file_buttons_frame = ttk.Frame(files_section)
        file_buttons_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(file_buttons_frame, text="🗑️ Limpiar Lista", 
                  command=self.clear_files).pack(side=tk.LEFT)
        
        # === CONFIGURACIÓN RÁPIDA (SIMPLIFICADA) ===
        config_section = ttk.LabelFrame(main_frame, text="⚙️ Configuración", 
                                       padding="15")
        config_section.pack(fill=tk.X, pady=(0, 15))
        
        config_grid = ttk.Frame(config_section)
        config_grid.pack(fill=tk.X)
        
        # Solo idioma (automático a Downloads)
        ttk.Label(config_grid, text="🌐 Idioma del OCR:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        languages = {'spa': '🇪🇸 Español', 'eng': '🇺🇸 English', 'fra': '🇫🇷 Français'}
        language_combo = ttk.Combobox(config_grid, textvariable=self.current_language, 
                                     values=list(languages.keys()), state="readonly", width=15)
        language_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
        
        # Mostrar donde se guardarán (solo informativo)
        ttk.Label(config_grid, text="📂 Se guardarán en:").grid(row=0, column=2, sticky=tk.W, padx=(20, 10))
        ttk.Label(config_grid, text="📥 Carpeta Descargas", 
                 foreground='#27AE60', font=('Segoe UI', 9, 'bold')).grid(row=0, column=3, sticky=tk.W)
        
        # === BOTONES PRINCIPALES ===
        action_section = ttk.Frame(main_frame)
        action_section.pack(fill=tk.X, pady=(0, 15))
        
        # Botones grandes y visibles
        buttons_frame = ttk.Frame(action_section)
        buttons_frame.pack()
        
        self.analyze_btn = ttk.Button(buttons_frame, text="🔍 ANALIZAR ARCHIVOS", 
                                     style='Big.TButton', command=self.analyze_files)
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.process_btn = ttk.Button(buttons_frame, text="⚡ APLICAR OCR", 
                                     style='Big.TButton', command=self.process_files)
        self.process_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # NUEVO: Botón para convertir a Word
        self.word_btn = ttk.Button(buttons_frame, text="📝 PDF → WORD", 
                                  style='Big.TButton', command=self.convert_to_word)
        self.word_btn.pack(side=tk.LEFT)
        
        # === ESTADO Y PROGRESO ===
        status_section = ttk.Frame(main_frame)
        status_section.pack(fill=tk.X)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_section, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Estado
        self.status_var = tk.StringVar(value="✅ Listo - Selecciona archivos PDF para comenzar")
        self.status_label = ttk.Label(status_section, textvariable=self.status_var)
        self.status_label.pack()
        
        # Configurar arrastrar y soltar
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """Configura funcionalidad de arrastrar y soltar."""
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            
            # Configurar drop en el frame
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
            
        except ImportError:
            # Sin drag & drop, solo hacer clic
            pass
    
    def on_drop(self, event):
        """Maneja archivos arrastrados y soltados."""
        files = self.root.tk.splitlist(event.data)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]
        
        if pdf_files:
            self.selected_files.extend(pdf_files)
            self.update_files_display()
            self.update_status(f"📁 {len(pdf_files)} archivos agregados")
        else:
            messagebox.showwarning("Archivos no válidos", 
                                 "Solo se aceptan archivos PDF")
    
    def load_settings_from_config(self):
        """Carga configuración desde archivo."""
        try:
            self.current_language.set(self.config.get('OCR', 'language'))
        except Exception as e:
            logger.warning(f"Error al cargar configuración: {e}")
    
    def select_files(self):
        """Selecciona archivos PDF individuales."""
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if files:
            self.selected_files.extend(files)
            self.update_files_display()
            self.update_status(f"📄 {len(files)} archivos seleccionados")
    
    def clear_files(self):
        """Limpia la lista de archivos seleccionados."""
        self.selected_files.clear()
        self.update_files_display()
        self.update_status("🗑️ Lista limpiada - Selecciona nuevos archivos")
    
    def update_files_display(self):
        """Actualiza la visualización de archivos en la lista."""
        self.files_listbox.delete(0, tk.END)
        
        for file_path in self.selected_files:
            filename = os.path.basename(file_path)
            try:
                size = format_file_size(os.path.getsize(file_path))
                display_text = f"📄 {filename} ({size})"
            except OSError:
                display_text = f"❌ {filename} (Error)"
            
            self.files_listbox.insert(tk.END, display_text)
    
    def on_language_change(self, event=None):
        """Maneja cambio de idioma."""
        new_language = self.current_language.get()
        if self.processor.set_language(new_language):
            languages = {'spa': 'español', 'eng': 'inglés', 'fra': 'francés'}
            lang_name = languages.get(new_language, new_language)
            self.update_status(f"🌐 Idioma cambiado a: {lang_name}")
    
    def analyze_files(self):
        """Analiza los archivos seleccionados."""
        if not self.selected_files:
            messagebox.showwarning("Sin archivos", "Selecciona archivos PDF primero")
            return
        
        if self.processing_active:
            messagebox.showwarning("Procesamiento activo", "Espera a que termine el proceso actual")
            return
        
        self.processing_active = True
        self.analyze_btn.config(state='disabled')
        
        def analyze_worker():
            try:
                self.update_status("🔍 Analizando archivos...")
                
                results = []
                for i, file_path in enumerate(self.selected_files):
                    progress = int((i / len(self.selected_files)) * 100)
                    self.progress_var.set(progress)
                    
                    filename = os.path.basename(file_path)
                    self.update_status(f"🔍 Analizando: {filename}")
                    
                    analysis = self.processor.analyze_file(file_path)
                    results.append(analysis)
                
                self.root.after(0, lambda: self.show_analysis_results(results))
                
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"❌ Error durante análisis: {e}"))
            finally:
                self.root.after(0, self.analysis_completed)
        
        thread = threading.Thread(target=analyze_worker, daemon=True)
        thread.start()
    
    def show_analysis_results(self, results):
        """Muestra los resultados del análisis de forma simple."""
        # Contar resultados
        total = len(results)
        need_ocr = sum(1 for r in results if r.get('success', False) and not r.get('has_embedded_text', True))
        have_text = sum(1 for r in results if r.get('success', False) and r.get('has_embedded_text', False))
        errors = sum(1 for r in results if not r.get('success', False))
        
        # Crear mensaje simple
        if errors > 0:
            message = f"⚠️ {errors} archivos con errores\n"
        else:
            message = ""
        
        if need_ocr > 0:
            message += f"📄 {need_ocr} archivos necesitan OCR\n"
        
        if have_text > 0:
            message += f"✅ {have_text} archivos ya tienen texto\n"
        
        message += f"\n📊 Total: {total} archivos analizados"
        
        # Mostrar resultado
        if need_ocr > 0:
            result = messagebox.askyesno("Análisis Completado", 
                                       f"{message}\n\n¿Aplicar OCR a los archivos que lo necesitan?")
            if result:
                self.process_files()
        else:
            messagebox.showinfo("Análisis Completado", 
                              f"{message}\n\n✨ ¡Todos tus archivos ya tienen texto buscable!")
    
    def analysis_completed(self):
        """Llamada cuando termina el análisis."""
        self.processing_active = False
        self.analyze_btn.config(state='normal')
        self.progress_var.set(0)
        self.update_status("✅ Análisis completado")
    
    def process_files(self):
        """Procesa los archivos seleccionados."""
        if not self.selected_files:
            messagebox.showwarning("Sin archivos", "Selecciona archivos PDF primero")
            return
        
        if self.processing_active:
            messagebox.showwarning("Procesamiento activo", "Espera a que termine el proceso actual")
            return
        
        # Confirmar procesamiento
        message = f"¿Aplicar OCR a {len(self.selected_files)} archivos?\n\n"
        message += "✨ Solo se procesarán los archivos que realmente necesiten OCR"
        
        if not messagebox.askyesno("Confirmar OCR", message):
            return
        
        # Crear diálogo de progreso
        progress_dialog = ProgressDialog(self.root, "Aplicando OCR a tus PDFs...")
        
        self.processing_active = True
        self.process_btn.config(state='disabled')
        
        def progress_callback(percent, message):
            self.root.after(0, lambda: progress_dialog.update_progress(percent, message))
            self.root.after(0, lambda: self.progress_var.set(percent))
            self.root.after(0, lambda: self.update_status(message))
        
        def completion_callback(results, stats):
            self.root.after(0, lambda: self.processing_completed(results, stats, progress_dialog))
        
        # Ejecutar procesamiento asíncrono
        self.processor.process_batch_async(
            self.selected_files,
            progress_callback,
            completion_callback
        )
    
    def processing_completed(self, results, stats, progress_dialog):
        """Llamada cuando termina el procesamiento."""
        self.processing_active = False
        self.process_btn.config(state='normal')
        
        # Cerrar diálogo de progreso
        progress_dialog.destroy()
        
        # Mostrar resultados simples
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        if successful == total:
            message = f"🎉 ¡Éxito total!\n\n✅ {successful} archivos procesados correctamente"
            if stats.get('files_with_ocr', 0) > 0:
                message += f"\n📄 {stats['files_with_ocr']} archivos con OCR aplicado"
            if stats.get('files_copied', 0) > 0:
                message += f"\n📋 {stats['files_copied']} archivos ya tenían texto"
            
            messagebox.showinfo("Procesamiento Completado", message)
        else:
            failed = total - successful
            message = f"⚠️ Procesamiento completado con algunos errores\n\n"
            message += f"✅ {successful} archivos exitosos\n"
            message += f"❌ {failed} archivos con errores"
            
            messagebox.showwarning("Procesamiento Completado", message)
        
        self.update_status(f"✅ Procesamiento completado: {successful}/{total} exitosos")
        
        # NUEVO: Solo preguntar dónde guardar (sin opciones confusas)
        if successful > 0:
            downloads_folder = self.output_directory.get()
            
            # Preguntar directamente dónde quiere guardar
            save_elsewhere = messagebox.askyesno("¿Dónde guardar archivos?", 
                                               f"📂 Archivos procesados están en Descargas\n\n¿Quieres guardarlos en otra carpeta?\n\n(Si eliges 'No', se quedan en Descargas)")
            
            if save_elsewhere:
                # Elegir directorio de destino
                dest_dir = filedialog.askdirectory(
                    title="Seleccionar dónde guardar los archivos procesados",
                    initialdir=downloads_folder
                )
                
                if dest_dir:
                    # Mover archivos exitosos
                    moved_count = 0
                    for result in results:
                        if result['success'] and 'output_path' in result:
                            try:
                                import shutil
                                src = result['output_path']
                                filename = os.path.basename(src)
                                dst = os.path.join(dest_dir, filename)
                                shutil.move(src, dst)
                                moved_count += 1
                            except Exception as e:
                                logger.error(f"Error moviendo archivo: {e}")
                    
                    if moved_count > 0:
                        # Abrir carpeta de destino automáticamente
                        try:
                            import subprocess
                            subprocess.run(f'explorer "{dest_dir}"', shell=True)
                        except:
                            try:
                                os.startfile(dest_dir)
                            except:
                                pass
                        
                        messagebox.showinfo("¡Archivos guardados!", 
                                          f"✅ {moved_count} archivos guardados en:\n{dest_dir}")
            else:
                # Se quedan en Descargas - abrir carpeta automáticamente
                try:
                    import subprocess
                    subprocess.run(f'explorer "{downloads_folder}"', shell=True)
                except:
                    try:
                        os.startfile(downloads_folder)
                    except:
                        pass
                
                messagebox.showinfo("¡Archivos listos!", 
                                   f"✅ Archivos guardados en Descargas\n📂 Carpeta abierta automáticamente")

    def convert_to_word(self):
        """Convierte PDFs a Word aplicando OCR primero si es necesario."""
        if not self.selected_files:
            messagebox.showwarning("Sin archivos", "Selecciona archivos PDF primero")
            return
        
        if self.processing_active:
            messagebox.showwarning("Procesamiento activo", "Espera a que termine el proceso actual")
            return
        
        # Confirmar conversión
        message = f"¿Convertir {len(self.selected_files)} archivos PDF a Word?\n\n"
        message += "✨ Se aplicará OCR automáticamente si es necesario\n"
        message += "📝 Los archivos .docx se guardarán donde elijas"
        
        if not messagebox.askyesno("Confirmar conversión a Word", message):
            return
        
        # Elegir directorio de salida para Word (por defecto Descargas)
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        output_dir = filedialog.askdirectory(
            title="¿Dónde guardar los archivos Word?",
            initialdir=downloads_path  # CORREGIDO: inicia en Descargas
        )
        if not output_dir:
            return
        
        # Crear diálogo de progreso
        progress_dialog = ProgressDialog(self.root, "Convirtiendo PDFs a Word...")
        
        self.processing_active = True
        self.word_btn.config(state='disabled')
        
        def progress_callback(percent, message):
            self.root.after(0, lambda: progress_dialog.update_progress(percent, message))
            self.root.after(0, lambda: self.progress_var.set(percent))
            self.root.after(0, lambda: self.update_status(message))
        
        def completion_callback(results):
            self.root.after(0, lambda: self.word_conversion_completed(results, output_dir, progress_dialog))
        
        # Ejecutar conversión asíncrona
        self.convert_to_word_async(self.selected_files, output_dir, progress_callback, completion_callback)
    
    def convert_to_word_async(self, file_paths, output_dir, progress_callback, completion_callback):
        """Convierte PDFs a Word de forma asíncrona."""
        def worker():
            results = []
            total_files = len(file_paths)
            
            for i, pdf_path in enumerate(file_paths):
                try:
                    filename = os.path.basename(pdf_path)
                    progress_callback(int((i / total_files) * 100), f"Procesando: {filename}")
                    
                    # Primero aplicar OCR si es necesario
                    temp_pdf_path = self.apply_ocr_if_needed(pdf_path, progress_callback)
                    
                    # Convertir a Word
                    word_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.docx")
                    success = self.pdf_to_word(temp_pdf_path, word_path)
                    
                    results.append({
                        'success': success,
                        'input_path': pdf_path,
                        'output_path': word_path if success else None,
                        'filename': filename
                    })
                    
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': str(e),
                        'input_path': pdf_path,
                        'filename': os.path.basename(pdf_path)
                    })
            
            self.root.after(0, lambda: completion_callback(results))
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def apply_ocr_if_needed(self, pdf_path, progress_callback):
        """Aplica OCR al PDF si es necesario usando nuestro procesador que funciona bien."""
        try:
            # Analizar si necesita OCR
            analysis = self.processor.analyze_file(pdf_path)
            
            if analysis.get('success') and not analysis.get('has_embedded_text'):
                # Necesita OCR - usar el mismo que funciona en APLICAR OCR
                if progress_callback:
                    progress_callback(None, "📄 Aplicando OCR (usando el motor principal)...")
                
                import tempfile
                import time
                temp_dir = tempfile.gettempdir()
                timestamp = int(time.time())
                temp_pdf = os.path.join(temp_dir, f"word_ocr_{timestamp}_{os.path.basename(pdf_path)}")
                
                # Usar exactamente el mismo método que funciona en "APLICAR OCR"
                result = self.processor.process_file(
                    pdf_path, 
                    output_path=temp_pdf,
                    force_ocr=True  # Forzar OCR
                )
                
                if result['success']:
                    logger.info(f"OCR aplicado exitosamente para Word: {temp_pdf}")
                    return temp_pdf
                else:
                    logger.warning(f"OCR falló, usando PDF original: {result.get('error', 'Error desconocido')}")
                    return pdf_path
            else:
                # Ya tiene texto, usar original
                if progress_callback:
                    progress_callback(None, "✅ PDF ya tiene texto, convirtiendo directamente...")
                return pdf_path
                
        except Exception as e:
            logger.error(f"Error aplicando OCR para Word: {e}")
            return pdf_path
    
    def pdf_to_word(self, pdf_path, word_path):
        """Convierte PDF a Word usando pdf2docx."""
        try:
            # Intentar usar pdf2docx
            try:
                from pdf2docx import Converter
                
                cv = Converter(pdf_path)
                cv.convert(word_path, start=0, end=None)
                cv.close()
                
                return True
                
            except ImportError:
                # Si no está instalado pdf2docx, usar método alternativo
                return self.pdf_to_word_alternative(pdf_path, word_path)
                
        except Exception as e:
            logger.error(f"Error convirtiendo a Word: {e}")
            return False
    
    def pdf_to_word_alternative(self, pdf_path, word_path):
        """Método alternativo para convertir PDF a Word usando PyMuPDF y python-docx."""
        try:
            import fitz
            from docx import Document
            
            # Crear documento Word
            doc = Document()
            
            # Abrir PDF
            pdf_doc = fitz.open(pdf_path)
            
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                text = page.get_text()
                
                if text.strip():
                    # Agregar texto al documento Word
                    doc.add_paragraph(text)
                    
                    # Salto de página (excepto última página)
                    if page_num < len(pdf_doc) - 1:
                        doc.add_page_break()
            
            pdf_doc.close()
            
            # Guardar documento Word
            doc.save(word_path)
            return True
            
        except ImportError:
            # Si no están las librerías, mostrar error
            messagebox.showerror("Librerías faltantes", 
                               "Para convertir a Word necesitas instalar:\npip install pdf2docx python-docx")
            return False
        except Exception as e:
            logger.error(f"Error en conversión alternativa: {e}")
            return False
    
    def word_conversion_completed(self, results, output_dir, progress_dialog):
        """Llamada cuando termina la conversión a Word."""
        self.processing_active = False
        self.word_btn.config(state='normal')
        
        # Cerrar diálogo de progreso
        progress_dialog.destroy()
        
        # Mostrar resultados
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        if successful == total:
            message = f"🎉 ¡Conversión exitosa!\n\n📝 {successful} archivos convertidos a Word"
            messagebox.showinfo("Conversión Completada", message)
        else:
            failed = total - successful
            message = f"⚠️ Conversión completada con algunos errores\n\n"
            message += f"✅ {successful} archivos exitosos\n"
            message += f"❌ {failed} archivos con errores"
            messagebox.showwarning("Conversión Completada", message)
        
        self.update_status(f"✅ Conversión completada: {successful}/{total} exitosos")
        
        # Preguntar si abrir carpeta
        if successful > 0:
            show_location = messagebox.askyesno("¡Archivos Word creados!", 
                                               f"📂 Archivos guardados en:\n{output_dir}\n\n¿Abrir carpeta?")
            if show_location:
                try:
                    import subprocess
                    subprocess.run(f'explorer "{output_dir}"', shell=True)
                except:
                    try:
                        os.startfile(output_dir)
                    except:
                        pass
        """Llamada cuando termina el procesamiento."""
        self.processing_active = False
        self.process_btn.config(state='normal')
        
        # Cerrar diálogo de progreso
        progress_dialog.destroy()
        
        # Mostrar resultados simples
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        if successful == total:
            message = f"🎉 ¡Éxito total!\n\n✅ {successful} archivos procesados correctamente"
            if stats.get('files_with_ocr', 0) > 0:
                message += f"\n📄 {stats['files_with_ocr']} archivos con OCR aplicado"
            if stats.get('files_copied', 0) > 0:
                message += f"\n📋 {stats['files_copied']} archivos ya tenían texto"
            
            messagebox.showinfo("Procesamiento Completado", message)
        else:
            failed = total - successful
            message = f"⚠️ Procesamiento completado con algunos errores\n\n"
            message += f"✅ {successful} archivos exitosos\n"
            message += f"❌ {failed} archivos con errores"
            
            messagebox.showwarning("Procesamiento Completado", message)
        
        self.update_status(f"✅ Procesamiento completado: {successful}/{total} exitosos")
        
        # Mostrar ubicación de archivos automáticamente
        if successful > 0:
            downloads_folder = self.output_directory.get()
            location_msg = f"📂 Archivos guardados automáticamente en:\n📥 {downloads_folder}"
            
            show_location = messagebox.askyesno("¡Archivos Procesados!", 
                                               f"{location_msg}\n\n¿Abrir carpeta de Descargas?")
            if show_location:
                try:
                    import subprocess
                    subprocess.run(f'explorer "{downloads_folder}"', shell=True)
                except:
                    try:
                        os.startfile(downloads_folder)
                    except:
                        pass
    
    def validate_system(self):
        """Valida la configuración del sistema silenciosamente."""
        try:
            system_status = self.processor.validate_system()
            
            if not system_status['overall_ok']:
                if not system_status['tesseract_ok']:
                    self.update_status("❌ Tesseract OCR no está instalado correctamente")
                elif not system_status['language_available']:
                    self.update_status(f"❌ Idioma '{system_status['current_language']}' no disponible")
                else:
                    self.update_status("⚠️ Hay problemas en la configuración")
            else:
                self.update_status("✅ Sistema listo - Selecciona archivos PDF para comenzar")
        except Exception as e:
            self.update_status("⚠️ No se pudo validar el sistema completamente")
    
    def update_status(self, message):
        """Actualiza el mensaje de estado."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def run(self):
        """Ejecuta la aplicación."""
        # Configurar manejo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Ejecutar loop principal
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Aplicación interrumpida por el usuario")
        except Exception as e:
            logger.error(f"Error en aplicación: {e}")
            messagebox.showerror("Error crítico", f"Error en la aplicación:\n{e}")
    
    def on_closing(self):
        """Maneja el cierre de la aplicación."""
        if self.processing_active:
            if not messagebox.askyesno("Procesamiento activo", 
                                     "Hay un procesamiento en curso. ¿Salir de todas formas?"):
                return
        
        # Guardar configuración
        try:
            self.config.set('OCR', 'language', self.current_language.get())
            self.config.set('Processing', 'output_directory', self.output_directory.get())
            save_config(self.config)
        except:
            pass
        
        # Cerrar aplicación
        self.root.destroy()


def main():
    """Función principal para ejecutar la aplicación simplificada."""
    try:
        app = PDFOCRApp()
        app.run()
    except Exception as e:
        logger.error(f"Error al iniciar aplicación: {e}")
        messagebox.showerror("Error de inicio", f"No se pudo iniciar la aplicación:\n{e}")


if __name__ == "__main__":
    main()