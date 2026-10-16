"""
TPL3 - Editor de Imágenes
=========================
Materia: Programación II · 5.º año
Institución: IPETyM N° 246 "Dr. Amadeo Sabattini"
Docente: Ing. Federico Coronati

Punto de entrada principal de la aplicación de escritorio.
Compatible con el entorno de desarrollo Thonny y ejecutable compilado.
"""

import sys
import tkinter as tk
from tkinter import messagebox

from interfaz import EditorApp


def configurar_alta_resolucion():
    """
    Mejora la nitidez visual de la ventana y fuentes en pantallas Windows modernas (DPI Awareness).
    """
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


def main():
    """Función principal de inicio del programa."""
    configurar_alta_resolucion()

    root = tk.Tk()
    
    # Manejador global de excepciones para evitar que el programa se cierre inesperadamente
    def reportar_error_inesperado(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        mensaje = f"Se produjo un error imprevisto:\n{exc_value}"
        print(f"[ERROR]: {exc_type.__name__}: {exc_value}")
        try:
            messagebox.showerror("Error inesperado", mensaje)
        except Exception:
            pass

    sys.excepthook = reportar_error_inesperado

    app = EditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
