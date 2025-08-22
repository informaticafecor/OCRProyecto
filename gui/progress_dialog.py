"""
Progress Dialog - Diálogo de Progreso
=====================================
Ventana modal para mostrar el progreso de operaciones largas.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time


class ProgressDialog:
    """
    Diálogo modal para mostrar progreso de operaciones largas.
    """
    
    def __init__(self, parent, title="Procesando...", cancelable=True):
        """
        Inicializa el diálogo de progreso.
        
        Args:
            parent: Ventana padre
            title (str): Título del diálogo
            cancelable (bool): Si se puede cancelar la operación
        """
        self.parent = parent
        self.canceled = False
        self.window = None
        
        # Crear ventana modal
        self.create_dialog(title, cancelable)
        
        # Variables de progreso
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Iniciando...")
        self.detail_var = tk.StringVar(value="")
        
        # Variables de tiempo
        self.start_time = time.time()
        self.last_update = time.time()
        
        # Variable para forzar detención del procesamiento
        self.force_stop = False
        
        # Configurar interfaz
        self.setup_interface()
        
        # Centrar ventana
        self.center_window()
    
    def create_dialog(self, title, cancelable):
        """Crea la ventana del diálogo."""
        self.window = tk.Toplevel(self.parent)
        self.window.title(title)
        self.window.geometry("600x250")  # MÁS GRANDE
        self.window.resizable(False, False)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Configurar cierre
        if cancelable:
            self.window.protocol("WM_DELETE_WINDOW", self.on_cancel)
        else:
            self.window.protocol("WM_DELETE_WINDOW", lambda: None)  # No hacer nada
    
    def setup_interface(self):
        """Configura la interfaz del diálogo."""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icono y título
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Icono (usando emoji como placeholder)
        icon_label = ttk.Label(header_frame, text="⚡", font=('TkDefaultFont', 24))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Información de estado
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Estado principal
        self.status_label = ttk.Label(info_frame, textvariable=self.status_var, 
                                     font=('TkDefaultFont', 10, 'bold'))
        self.status_label.pack(anchor=tk.W)
        
        # Detalles
        self.detail_label = ttk.Label(info_frame, textvariable=self.detail_var, 
                                     font=('TkDefaultFont', 8))
        self.detail_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Barra de progreso
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
        # Etiqueta de porcentaje y tiempo
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.percent_var = tk.StringVar(value="0%")
        self.time_var = tk.StringVar(value="Tiempo transcurrido: 0s")
        self.eta_var = tk.StringVar(value="")
        
        ttk.Label(stats_frame, textvariable=self.percent_var).pack(side=tk.LEFT)
        ttk.Label(stats_frame, textvariable=self.time_var).pack(side=tk.RIGHT)
        
        # ETA (tiempo estimado)
        ttk.Label(main_frame, textvariable=self.eta_var, 
                 font=('TkDefaultFont', 8)).pack(pady=(0, 10))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Botón cancelar
        self.cancel_btn = ttk.Button(button_frame, text="Cancelar", 
                                    command=self.on_cancel)
        self.cancel_btn.pack(side=tk.RIGHT)
        
        # Botón minimizar
        self.minimize_btn = ttk.Button(button_frame, text="Minimizar", 
                                      command=self.minimize)
        self.minimize_btn.pack(side=tk.RIGHT, padx=(0, 5))
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def update_progress(self, percent, status="", details=""):
        """
        Actualiza el progreso del diálogo.
        
        Args:
            percent (float): Porcentaje completado (0-100)
            status (str): Mensaje de estado principal
            details (str): Detalles adicionales
        """
        # Validar entrada
        percent = max(0, min(100, percent))
        
        # Actualizar variables
        self.progress_var.set(percent)
        
        if status:
            self.status_var.set(status)
        
        if details:
            self.detail_var.set(details)
        
        # Actualizar porcentaje
        self.percent_var.set(f"{percent:.1f}%")
        
        # Calcular tiempo transcurrido
        elapsed = time.time() - self.start_time
        self.time_var.set(f"Tiempo transcurrido: {self.format_time(elapsed)}")
        
        # Calcular ETA si hay progreso
        if percent > 0 and percent < 100:
            eta_seconds = (elapsed / percent) * (100 - percent)
            self.eta_var.set(f"Tiempo estimado restante: {self.format_time(eta_seconds)}")
        elif percent >= 100:
            self.eta_var.set("¡Completado!")
        
        # Actualizar interfaz
        self.window.update_idletasks()
        
        # Registrar tiempo de última actualización
        self.last_update = time.time()
    
    def update_status(self, status, details=""):
        """
        Actualiza solo el estado sin cambiar el progreso.
        
        Args:
            status (str): Nuevo estado
            details (str): Detalles adicionales
        """
        if status:
            self.status_var.set(status)
        
        if details:
            self.detail_var.set(details)
        
        self.window.update_idletasks()
    
    def set_indeterminate(self, active=True):
        """
        Configura la barra de progreso en modo indeterminado.
        
        Args:
            active (bool): Si activar modo indeterminado
        """
        if active:
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start(10)  # Velocidad de animación
            self.percent_var.set("Procesando...")
        else:
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate')
    
    def format_time(self, seconds):
        """
        Formatea tiempo en formato legible.
        
        Args:
            seconds (float): Tiempo en segundos
            
        Returns:
            str: Tiempo formateado
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def on_cancel(self):
        """Maneja la cancelación de la operación."""
        if not self.canceled:
            self.canceled = True
            self.update_status("🛑 Cancelando...", "Por favor espera, finalizando operación actual")
            self.cancel_btn.config(state='disabled', text="Cancelando...")
            
            # Forzar cierre después de 3 segundos si no responde
            self.window.after(3000, self.force_close)
    
    def force_close(self):
        """Fuerza el cierre del diálogo si no responde."""
        if self.canceled and self.window:
            try:
                self.window.destroy()
            except:
                pass
    
    def minimize(self):
        """Minimiza la ventana."""
        try:
            # No intentar minimizar ventanas transient, solo ocultar
            self.window.withdraw()  # Ocultar en lugar de minimizar
        except Exception as e:
            print(f"Error al ocultar ventana: {e}")  # Usar print en lugar de logger
    
    def complete(self, success=True, message="Operación completada"):
        """
        Marca la operación como completada.
        
        Args:
            success (bool): Si la operación fue exitosa
            message (str): Mensaje final
        """
        if success:
            self.update_progress(100, message, "")
            self.progress_bar.config(style='success.Horizontal.TProgressbar')
        else:
            self.update_status(message, "Operación completada con errores")
            self.progress_bar.config(style='danger.Horizontal.TProgressbar')
        
        # Cambiar botón cancelar a cerrar
        self.cancel_btn.config(text="Cerrar", command=self.close)
        
        # Auto-cerrar después de unos segundos si fue exitoso
        if success:
            self.window.after(2000, self.close)
    
    def close(self):
        """Cierra el diálogo."""
        if self.window:
            self.window.destroy()
    
    def destroy(self):
        """Destruye el diálogo (alias para close)."""
        self.close()
    
    def is_canceled(self):
        """
        Verifica si la operación fue cancelada.
        
        Returns:
            bool: True si fue cancelada
        """
        return self.canceled
    
    def show_error(self, error_message):
        """
        Muestra un error en el diálogo.
        
        Args:
            error_message (str): Mensaje de error
        """
        self.update_status("❌ Error", error_message)
        self.progress_bar.config(style='danger.Horizontal.TProgressbar')
        self.cancel_btn.config(text="Cerrar", command=self.close)


class BatchProgressDialog(ProgressDialog):
    """
    Diálogo de progreso especializado para operaciones por lotes.
    """
    
    def __init__(self, parent, title="Procesando archivos...", total_items=0):
        """
        Inicializa el diálogo para procesamiento por lotes.
        
        Args:
            parent: Ventana padre
            title (str): Título del diálogo
            total_items (int): Número total de elementos a procesar
        """
        self.total_items = total_items
        self.current_item = 0
        self.completed_items = 0
        self.failed_items = 0
        
        super().__init__(parent, title)
        
        # Agregar información de lote
        self.setup_batch_info()
    
    def setup_batch_info(self):
        """Configura información adicional para procesamiento por lotes."""
        # Frame para información de lote
        batch_frame = ttk.Frame(self.window)
        batch_frame.pack(before=self.cancel_btn.master, fill=tk.X, padx=20, pady=(0, 10))
        
        # Variables de lote
        self.batch_var = tk.StringVar(value=f"Archivo 0 de {self.total_items}")
        self.success_var = tk.StringVar(value="Exitosos: 0")
        self.failed_var = tk.StringVar(value="Fallidos: 0")
        
        # Etiquetas de información
        ttk.Label(batch_frame, textvariable=self.batch_var, 
                 font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.W)
        
        stats_frame = ttk.Frame(batch_frame)
        stats_frame.pack(fill=tk.X, pady=(2, 0))
        
        ttk.Label(stats_frame, textvariable=self.success_var, 
                 foreground='green').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(stats_frame, textvariable=self.failed_var, 
                 foreground='red').pack(side=tk.LEFT)
    
    def update_batch_progress(self, current_item, item_name="", item_progress=0, 
                            item_status="", success=None):
        """
        Actualiza el progreso del lote.
        
        Args:
            current_item (int): Índice del elemento actual (0-based)
            item_name (str): Nombre del elemento actual
            item_progress (float): Progreso del elemento actual (0-100)
            item_status (str): Estado del elemento actual
            success (bool): Si el elemento anterior fue exitoso (None si aún no termina)
        """
        self.current_item = current_item
        
        # Actualizar contadores si el elemento anterior terminó
        if success is not None:
            if success:
                self.completed_items += 1
            else:
                self.failed_items += 1
        
        # Calcular progreso general
        if self.total_items > 0:
            # Progreso basado en elementos completados + progreso del actual
            base_progress = (current_item / self.total_items) * 100
            item_weight = (1 / self.total_items) * 100
            total_progress = base_progress + (item_progress * item_weight / 100)
            
            self.update_progress(total_progress, item_status, item_name)
        
        # Actualizar información de lote
        self.batch_var.set(f"Archivo {current_item + 1} de {self.total_items}")
        self.success_var.set(f"Exitosos: {self.completed_items}")
        self.failed_var.set(f"Fallidos: {self.failed_items}")
        
        # Si terminamos todos los elementos
        if current_item >= self.total_items - 1 and item_progress >= 100:
            success_rate = (self.completed_items / self.total_items) * 100 if self.total_items > 0 else 0
            final_message = f"Procesamiento completado: {self.completed_items}/{self.total_items} exitosos ({success_rate:.1f}%)"
            self.complete(success=self.failed_items == 0, message=final_message)


def demo_progress():
    """Función de demostración del diálogo de progreso."""
    import random
    
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Crear diálogo de progreso simple
    dialog = ProgressDialog(root, "Operación de prueba")
    
    def simulate_work():
        """Simula trabajo con progreso."""
        for i in range(101):
            if dialog.is_canceled():
                break
            
            # Simular trabajo
            time.sleep(0.05)
            
            # Actualizar progreso
            status = f"Procesando paso {i+1}/100"
            details = f"Operación simulada - paso {i+1}"
            dialog.update_progress(i, status, details)
        
        if not dialog.is_canceled():
            dialog.complete(True, "¡Operación completada exitosamente!")
        else:
            dialog.close()
    
    # Ejecutar simulación en hilo separado
    thread = threading.Thread(target=simulate_work, daemon=True)
    thread.start()
    
    root.mainloop()


def demo_batch_progress():
    """Función de demostración del diálogo de progreso por lotes."""
    import random
    
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    files = ["archivo1.pdf", "archivo2.pdf", "archivo3.pdf", "archivo4.pdf", "archivo5.pdf"]
    
    # Crear diálogo de progreso por lotes
    dialog = BatchProgressDialog(root, "Procesando archivos PDF", len(files))
    
    def simulate_batch_work():
        """Simula procesamiento por lotes."""
        for i, filename in enumerate(files):
            if dialog.is_canceled():
                break
            
            # Simular procesamiento de archivo individual
            for progress in range(0, 101, 10):
                if dialog.is_canceled():
                    break
                
                time.sleep(0.1)
                status = f"Procesando {filename}..."
                dialog.update_batch_progress(i, filename, progress, status)
            
            # Marcar como completado (simular éxito/fallo aleatorio)
            success = random.choice([True, True, True, False])  # 75% éxito
            dialog.update_batch_progress(i, filename, 100, 
                                       f"{'Completado' if success else 'Error'}: {filename}", 
                                       success)
        
        if dialog.is_canceled():
            dialog.close()
    
    # Ejecutar simulación en hilo separado
    thread = threading.Thread(target=simulate_batch_work, daemon=True)
    thread.start()
    
    root.mainloop()


if __name__ == "__main__":
    print("1. Progreso simple")
    print("2. Progreso por lotes")
    choice = input("Selecciona demo (1-2): ")
    
    if choice == "1":
        demo_progress()
    elif choice == "2":
        demo_batch_progress()
    else:
        print("Opción no válida")