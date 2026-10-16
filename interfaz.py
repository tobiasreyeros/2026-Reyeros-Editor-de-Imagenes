"""
Módulo de Interfaz Gráfica (Tkinter)
-----------------------------------
Implementa la interfaz visual del Editor de Imágenes cumpliendo con los
requisitos 3.1 a 3.10 del PDF:
- Menú gráfico estructurado (Archivo, Editar, Imagen, Filtros, Ajustes, Ayuda).
- Carga y guardado de archivos con manejo de errores y compatibilidad de formatos.
- Visualización de imagen original vs resultado en Vista Previa (Antes / Después) con Confirmación.
- Recorte interactivo con ratón y por ingreso de coordenadas.
- Sliders interactivos de Brillo, Contraste, Saturación y Umbral de Binarización.
- Historial con Deshacer y Rehacer.
- Sonido en transformaciones sin congelar la interfaz.

Autor: Proyecto Editor de Imágenes (5.º Año - IPETyM N° 246)
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional
from PIL import Image, ImageTk

from procesador import ProcesadorImagen
from historial import HistorialManager
from sonido import SonidoManager


def obtener_ruta_recurso(ruta_relativa: str) -> str:
    """
    Función utilitaria de compatibilidad (vista en TP ENVIAR_EMAIL y e21.py):
    Permite ubicar recursos tanto en ejecución de desarrollo como cuando
    el proyecto sea compilado a .exe con PyInstaller / auto-py-to-exe.
    """
    try:
        ruta_base = sys._MEIPASS
    except Exception:
        ruta_base = os.path.abspath(".")
    return os.path.join(ruta_base, ruta_relativa)


class EditorApp:
    """
    Clase principal que encapsula la lógica de la interfaz gráfica y los eventos de usuario.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Editor de Imágenes - IPETyM N° 246")
        self.root.geometry("1100x720")
        self.root.minsize(800, 500)

        # Gestores auxiliares
        self.historial = HistorialManager(limite_maximo=25)

        # Estado de imágenes
        self.imagen_original: Optional[Image.Image] = None  # Imagen tal como se cargó
        self.imagen_actual: Optional[Image.Image] = None    # Imagen base confirmada
        self.imagen_previa: Optional[Image.Image] = None    # Imagen temporal de vista previa
        self.ruta_archivo_actual: Optional[str] = None
        self.operacion_pendiente: Optional[str] = None      # Nombre de la transformación en curso

        # Variables de estado para recorte interactivo con mouse
        self.modo_recorte_activo = False
        self.crop_x_inicio = 0
        self.crop_y_inicio = 0
        self.crop_rect_id = None
        self.escala_visualizacion = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Referencias de PhotoImage para evitar garbage collection de Tkinter
        self._tk_img_normal = None
        self._tk_img_antes = None
        self._tk_img_despues = None

        # Construcción de la interfaz
        self._crear_menu()
        self._crear_barra_herramientas()
        self._crear_barra_confirmacion()
        self._crear_area_visualizacion()
        self._crear_barra_estado()

        # Atajos de teclado
        self._configurar_atajos()

        # Actualizar estado inicial de controles
        self._actualizar_estado_controles()

    # -------------------------------------------------------------
    # 3.1 INTERFAZ Y MENÚ GRÁFICO
    # -------------------------------------------------------------

    def _crear_menu(self):
        """Crea la barra superior de menú con todas las opciones organizadas."""
        self.barra_menu = tk.Menu(self.root)
        self.root.config(menu=self.barra_menu)

        # Menú Archivo
        self.menu_archivo = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Archivo", menu=self.menu_archivo)
        self.menu_archivo.add_command(label="Abrir imagen... (Ctrl+O)", command=self.abrir_imagen)
        self.menu_archivo.add_command(label="Guardar como... (Ctrl+S)", command=self.guardar_como)
        self.menu_archivo.add_separator()
        self.menu_archivo.add_command(label="Cerrar imagen", command=self.cerrar_imagen)
        self.menu_archivo.add_separator()
        self.menu_archivo.add_command(label="Salir", command=self.root.quit)

        # Menú Editar
        self.menu_editar = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Editar", menu=self.menu_editar)
        self.menu_editar.add_command(label="Deshacer (Ctrl+Z)", command=self.accion_deshacer)
        self.menu_editar.add_command(label="Rehacer (Ctrl+Y)", command=self.accion_rehacer)
        self.menu_editar.add_separator()
        self.menu_editar.add_command(label="Confirmar cambio (Enter)", command=self.confirmar_vista_previa)
        self.menu_editar.add_command(label="Cancelar vista previa (Esc)", command=self.cancelar_vista_previa)
        self.menu_editar.add_separator()
        self.menu_editar.add_command(label="Restablecer a original", command=self.restablecer_original)

        # Menú Imagen (Transformaciones)
        self.menu_imagen = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Imagen", menu=self.menu_imagen)
        
        # Volteos (e15.py)
        self.menu_imagen.add_command(label="Voltear horizontal (Espejo)", command=self.transformar_volteo_h)
        self.menu_imagen.add_command(label="Voltear vertical", command=self.transformar_volteo_v)
        self.menu_imagen.add_separator()
        
        # Rotaciones (e17.py)
        self.menu_imagen.add_command(label="Rotar 90° a la derecha", command=self.transformar_rotar_90_der)
        self.menu_imagen.add_command(label="Rotar 90° a la izquierda", command=self.transformar_rotar_90_izq)
        self.menu_imagen.add_command(label="Rotar 180°", command=self.transformar_rotar_180)
        self.menu_imagen.add_separator()
        
        # Color y Tonalidad (e16.py)
        self.menu_imagen.add_command(label="Convertir a escala de grises", command=self.transformar_grises)
        self.menu_imagen.add_command(label="Binarizar (Blanco y Negro ajustable)...", command=self.abrir_panel_binarizar)
        self.menu_imagen.add_separator()
        
        # Recorte
        self.menu_imagen.add_command(label="Recortar con el mouse", command=self.activar_herramienta_recorte)
        self.menu_imagen.add_command(label="Recortar por coordenadas...", command=self.abrir_dialogo_recorte_coords)

        # Menú Filtros (Punto 3.5)
        self.menu_filtros = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Filtros", menu=self.menu_filtros)
        self.menu_filtros.add_command(label="Desenfoque (Blur)", command=self.aplicar_filtro_desenfoque)
        self.menu_filtros.add_command(label="Nitidez (Sharpen)", command=self.aplicar_filtro_nitidez)
        self.menu_filtros.add_command(label="Detección de bordes", command=self.aplicar_filtro_bordes)
        self.menu_filtros.add_command(label="Negativo (Invertir colores)", command=self.aplicar_filtro_negativo)
        self.menu_filtros.add_command(label="Sepia (Vintage)", command=self.aplicar_filtro_sepia)

        # Menú Ajustes (Brillo, Contraste, Saturación - Punto 3.7)
        self.menu_ajustes = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Ajustes", menu=self.menu_ajustes)
        self.menu_ajustes.add_command(label="Brillo, Contraste y Saturación...", command=self.abrir_panel_ajustes)

        # Menú Ayuda
        self.menu_ayuda = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Ayuda", menu=self.menu_ayuda)
        self.menu_ayuda.add_command(label="Guía de atajos de teclado", command=self.mostrar_atajos)
        self.menu_ayuda.add_command(label="Acerca del Editor", command=self.mostrar_acerca_de)

    def _crear_barra_herramientas(self):
        """Barra de botones de acceso rápido debajo del menú."""
        self.frame_toolbar = tk.Frame(self.root, bg="#EAEAEA", relief=tk.RAISED, bd=1)
        self.frame_toolbar.pack(side=tk.TOP, fill=tk.X)

        self.btn_abrir = tk.Button(self.frame_toolbar, text="📂 Abrir", relief=tk.GROOVE, padx=6, pady=2, command=self.abrir_imagen)
        self.btn_abrir.pack(side=tk.LEFT, padx=3, pady=3)

        self.btn_guardar = tk.Button(self.frame_toolbar, text="💾 Guardar", relief=tk.GROOVE, padx=6, pady=2, command=self.guardar_como)
        self.btn_guardar.pack(side=tk.LEFT, padx=3, pady=3)

        tk.Frame(self.frame_toolbar, width=2, bg="#CCCCCC", height=22).pack(side=tk.LEFT, padx=5)

        self.btn_deshacer = tk.Button(self.frame_toolbar, text="↶ Deshacer", relief=tk.GROOVE, padx=6, pady=2, command=self.accion_deshacer)
        self.btn_deshacer.pack(side=tk.LEFT, padx=3, pady=3)

        self.btn_rehacer = tk.Button(self.frame_toolbar, text="↷ Rehacer", relief=tk.GROOVE, padx=6, pady=2, command=self.accion_rehacer)
        self.btn_rehacer.pack(side=tk.LEFT, padx=3, pady=3)

        tk.Frame(self.frame_toolbar, width=2, bg="#CCCCCC", height=22).pack(side=tk.LEFT, padx=5)

        self.btn_recortar_mouse = tk.Button(self.frame_toolbar, text="✂ Recortar Mouse", relief=tk.GROOVE, padx=6, pady=2, command=self.activar_herramienta_recorte)
        self.btn_recortar_mouse.pack(side=tk.LEFT, padx=3, pady=3)

        self.btn_ajustes_color = tk.Button(self.frame_toolbar, text="🎚 Brillo/Contraste", relief=tk.GROOVE, padx=6, pady=2, command=self.abrir_panel_ajustes)
        self.btn_ajustes_color.pack(side=tk.LEFT, padx=3, pady=3)

        self.btn_binarizar = tk.Button(self.frame_toolbar, text="🌓 Binarizar", relief=tk.GROOVE, padx=6, pady=2, command=self.abrir_panel_binarizar)
        self.btn_binarizar.pack(side=tk.LEFT, padx=3, pady=3)

    # -------------------------------------------------------------
    # 3.8 VISTA PREVIA ANTES/DESPUÉS Y CONFIRMACIÓN
    # -------------------------------------------------------------

    def _crear_barra_confirmacion(self):
        """
        Barra de confirmación que se muestra cuando una vista previa está activa.
        Permite al usuario Confirmar o Cancelar la transformación.
        """
        self.frame_confirmacion = tk.Frame(self.root, bg="#2C3E50", pady=5)
        
        self.lbl_info_preview = tk.Label(
            self.frame_confirmacion, 
            text="VISTA PREVIA ACTIVA: Revise el resultado antes de confirmar",
            bg="#2C3E50", 
            fg="#ECF0F1", 
            font=("Arial", 10, "bold")
        )
        self.lbl_info_preview.pack(side=tk.LEFT, padx=15)

        self.btn_confirmar = tk.Button(
            self.frame_confirmacion, 
            text="✓ Confirmar Cambio", 
            bg="#27AE60", 
            fg="white", 
            font=("Arial", 9, "bold"),
            padx=10, 
            relief=tk.RAISED,
            command=self.confirmar_vista_previa
        )
        self.btn_confirmar.pack(side=tk.RIGHT, padx=10)

        self.btn_cancelar = tk.Button(
            self.frame_confirmacion, 
            text="✕ Cancelar", 
            bg="#C0392B", 
            fg="white", 
            font=("Arial", 9, "bold"),
            padx=10, 
            relief=tk.RAISED,
            command=self.cancelar_vista_previa
        )
        self.btn_cancelar.pack(side=tk.RIGHT, padx=5)

        # Oculta por defecto hasta que se active una vista previa
        # Se muestra mediante self.frame_confirmacion.pack()

    def _crear_area_visualizacion(self):
        """
        Contenedor central que alterna entre:
        1. Vista Normal: un único lienzo centrado.
        2. Vista Previa Dividida: dos paneles lado a lado comparando "Antes" y "Después".
        """
        self.frame_central = tk.Frame(self.root, bg="#333333")
        self.frame_central.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 1. Modo Normal (Canvas único)
        self.canvas_normal = tk.Canvas(self.frame_central, bg="#252526", highlightthickness=0)
        
        # Enlaces de eventos de ratón para recorte sobre el canvas
        self.canvas_normal.bind("<ButtonPress-1>", self._on_mouse_press)
        self.canvas_normal.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas_normal.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas_normal.bind("<Configure>", lambda e: self._redibujar_imagen())

        # 2. Modo Vista Previa Dividida (Dos paneles Antes / Después)
        self.frame_dividido = tk.Frame(self.frame_central, bg="#252526")
        
        # Panel Izquierdo: ANTES
        self.frame_antes = tk.Frame(self.frame_dividido, bg="#252526")
        self.frame_antes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.lbl_titulo_antes = tk.Label(self.frame_antes, text="ORIGINAL (Antes)", bg="#1E1E1E", fg="#A0A0A0", font=("Arial", 10, "bold"), pady=3)
        self.lbl_titulo_antes.pack(side=tk.TOP, fill=tk.X)
        self.canvas_antes = tk.Canvas(self.frame_antes, bg="#1E1E1E", highlightthickness=0)
        self.canvas_antes.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Panel Derecho: DESPUÉS
        self.frame_despues = tk.Frame(self.frame_dividido, bg="#252526")
        self.frame_despues.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.lbl_titulo_despues = tk.Label(self.frame_despues, text="VISTA PREVIA (Después)", bg="#1E1E1E", fg="#2ECC71", font=("Arial", 10, "bold"), pady=3)
        self.lbl_titulo_despues.pack(side=tk.TOP, fill=tk.X)
        self.canvas_despues = tk.Canvas(self.frame_despues, bg="#1E1E1E", highlightthickness=0)
        self.canvas_despues.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Mostrar por defecto el canvas normal
        self.canvas_normal.pack(fill=tk.BOTH, expand=True)

    def _crear_barra_estado(self):
        """Barra de estado inferior informativa."""
        self.frame_estado = tk.Frame(self.root, bg="#007ACC", height=24)
        self.frame_estado.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_estado = tk.Label(
            self.frame_estado, 
            text="Listo. Abra una imagen para comenzar.", 
            bg="#007ACC", 
            fg="white", 
            font=("Arial", 9),
            anchor=tk.W,
            padx=8
        )
        self.lbl_estado.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lbl_dimensiones = tk.Label(
            self.frame_estado, 
            text="0 x 0 px", 
            bg="#007ACC", 
            fg="white", 
            font=("Arial", 9),
            anchor=tk.E,
            padx=12
        )
        self.lbl_dimensiones.pack(side=tk.RIGHT)

    def _configurar_atajos(self):
        """Asocia atajos de teclado estándar para agilidad de uso."""
        self.root.bind("<Control-o>", lambda e: self.abrir_imagen())
        self.root.bind("<Control-O>", lambda e: self.abrir_imagen())
        self.root.bind("<Control-s>", lambda e: self.guardar_como())
        self.root.bind("<Control-S>", lambda e: self.guardar_como())
        self.root.bind("<Control-z>", lambda e: self.accion_deshacer())
        self.root.bind("<Control-Z>", lambda e: self.accion_deshacer())
        self.root.bind("<Control-y>", lambda e: self.accion_rehacer())
        self.root.bind("<Control-Y>", lambda e: self.accion_rehacer())
        self.root.bind("<Return>", lambda e: self.confirmar_vista_previa())
        self.root.bind("<Escape>", lambda e: self.cancelar_vista_previa())

    # -------------------------------------------------------------
    # 3.2 ABRIR IMAGEN
    # -------------------------------------------------------------

    def abrir_imagen(self):
        """
        Carga una imagen en tiempo de ejecución desde un cuadro de diálogo del SO.
        No admite rutas fijas (hardcodeadas). Valida formatos (JPG, PNG, BMP) y maneja errores.
        """
        tipos_archivos = [
            ("Archivos de imagen admitidos", "*.jpg;*.jpeg;*.png;*.bmp"),
            ("JPEG (*.jpg, *.jpeg)", "*.jpg;*.jpeg"),
            ("PNG (*.png)", "*.png"),
            ("BMP (*.bmp)", "*.bmp"),
            ("Todos los archivos", "*.*")
        ]

        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen para editar",
            filetypes=tipos_archivos
        )

        if not ruta:
            # El usuario canceló el diálogo de selección
            return

        try:
            # Carga y validación con Pillow
            img = Image.open(ruta)
            img.verify()  # Verifica integridad básica del archivo
            
            # Reabrimos porque verify() deja la imagen en estado de lectura consumido
            img = Image.open(ruta)

            self.ruta_archivo_actual = ruta
            self.imagen_original = img.copy()
            self.imagen_actual = img.copy()
            self.imagen_previa = None
            self.operacion_pendiente = None

            # Reiniciar historial y herramientas
            self.historial.reiniciar()
            self.modo_recorte_activo = False

            # Quitar barra de confirmación si estaba visible
            self.frame_confirmacion.pack_forget()
            self.frame_dividido.pack_forget()
            self.canvas_normal.pack(fill=tk.BOTH, expand=True)

            nombre_archivo = os.path.basename(ruta)
            self._set_estado(f"Imagen '{nombre_archivo}' cargada correctamente.")
            self._actualizar_info_dimensiones()
            self._redibujar_imagen()
            self._actualizar_estado_controles()

        except Exception as e:
            messagebox.showerror(
                "Error al abrir imagen",
                f"No se pudo cargar el archivo seleccionado.\n"
                f"Asegúrese de que el formato sea admitido (JPG, PNG, BMP) y no esté dañado.\n\n"
                f"Detalle técnico: {e}"
            )

    # -------------------------------------------------------------
    # 3.3 GUARDAR COMO
    # -------------------------------------------------------------

    def guardar_como(self):
        """
        Permite guardar la imagen procesada en el SO, eligiendo nombre, ubicación y formato.
        Asegura que si el formato no admite características (ej: transparencia en JPG),
        la aplicación no falle (convierte a RGB con fondo blanco).
        """
        if not self.imagen_actual:
            messagebox.showwarning("Atención", "No hay ninguna imagen cargada para guardar.")
            return

        tipos_guardado = [
            ("PNG (*.png)", "*.png"),
            ("JPEG (*.jpg)", "*.jpg"),
            ("BMP (*.bmp)", "*.bmp")
        ]

        nombre_sugerido = "imagen_editada.png"
        if self.ruta_archivo_actual:
            base, ext = os.path.splitext(os.path.basename(self.ruta_archivo_actual))
            nombre_sugerido = f"{base}_editada{ext}"

        ruta_destino = filedialog.asksaveasfilename(
            title="Guardar imagen procesada como",
            defaultextension=".png",
            initialfile=nombre_sugerido,
            filetypes=tipos_guardado
        )

        if not ruta_destino:
            return  # Cancelado por el usuario

        try:
            # Preparamos la imagen con nuestro procesador para garantizar compatibilidad
            img_guardar, opciones = ProcesadorImagen.preparar_para_guardar(self.imagen_actual, ruta_destino)
            img_guardar.save(ruta_destino, **opciones)

            self._set_estado(f"Imagen guardada con éxito en: {ruta_destino}")
            messagebox.showinfo("Guardado exitoso", f"La imagen se guardó correctamente en:\n{ruta_destino}")

        except Exception as e:
            messagebox.showerror(
                "Error al guardar",
                f"Ocurrió un error al intentar guardar la imagen:\n{e}"
            )

    def cerrar_imagen(self):
        """Cierra la imagen actual y limpia el área de trabajo."""
        self.imagen_original = None
        self.imagen_actual = None
        self.imagen_previa = None
        self.ruta_archivo_actual = None
        self.operacion_pendiente = None
        self.modo_recorte_activo = False

        self.historial.reiniciar()
        self.frame_confirmacion.pack_forget()
        self.frame_dividido.pack_forget()
        self.canvas_normal.pack(fill=tk.BOTH, expand=True)
        self.canvas_normal.delete("all")

        self._set_estado("Imagen cerrada.")
        self.lbl_dimensiones.config(text="0 x 0 px")
        self._actualizar_estado_controles()

    def restablecer_original(self):
        """Restaura la imagen al estado original en que fue abierta."""
        if not self.imagen_original:
            return

        if messagebox.askyesno("Restablecer", "¿Desea descartar todos los cambios y volver a la imagen original?"):
            self.historial.registrar_cambio(self.imagen_actual)
            self.imagen_actual = self.imagen_original.copy()
            self.cancelar_vista_previa()
            self._set_estado("Imagen restablecida a su estado original.")
            self._actualizar_info_dimensiones()
            self._redibujar_imagen()
            self._actualizar_estado_controles()
            SonidoManager.emitir_sonido_transformacion()

    # -------------------------------------------------------------
    # GESTIÓN DE VISTA PREVIA (ANTES / DESPUÉS) Y CONFIRMACIÓN
    # -------------------------------------------------------------

    def iniciar_vista_previa(self, imagen_resultado: Image.Image, nombre_operacion: str):
        """
        Activa el modo de vista previa comparativa (Punto 3.8 del PDF):
        - Muestra lado a lado: 'Original (Antes)' vs 'Resultado (Después)'.
        - Despliega la barra de confirmación con los botones [Confirmar] y [Cancelar].
        """
        if not self.imagen_actual:
            return

        self.imagen_previa = imagen_resultado
        self.operacion_pendiente = nombre_operacion

        # Mostramos la barra de confirmación
        self.lbl_info_preview.config(text=f"VISTA PREVIA: {nombre_operacion}. ¿Desea aplicar el cambio?")
        self.frame_confirmacion.pack(side=tk.TOP, fill=tk.X, before=self.frame_central)

        # Conmutamos al modo dividido (Antes / Después)
        self.canvas_normal.pack_forget()
        self.frame_dividido.pack(fill=tk.BOTH, expand=True)

        self._dibujar_comparativa()
        self._set_estado(f"Vista previa: {nombre_operacion}. Presione [Confirmar] o [Cancelar].")

    def confirmar_vista_previa(self):
        """
        Aplica definitivamente la transformación previsualizada:
        - Registra la imagen anterior en el historial para permitir Deshacer.
        - Actualiza la imagen actual con el resultado.
        - Reproduce el sonido de confirmación sin congelar la interfaz (Punto 3.10).
        - Vuelve al modo de visualización normal.
        """
        if self.imagen_previa is None or self.imagen_actual is None:
            return

        # 1. Registrar en historial
        self.historial.registrar_cambio(self.imagen_actual)

        # 2. Asignar resultado
        self.imagen_actual = self.imagen_previa.copy()
        operacion = self.operacion_pendiente or "Transformación"

        # 3. Limpiar variables de vista previa
        self.imagen_previa = None
        self.operacion_pendiente = None
        self.modo_recorte_activo = False

        # 4. Restaurar vista normal
        self.frame_confirmacion.pack_forget()
        self.frame_dividido.pack_forget()
        self.canvas_normal.pack(fill=tk.BOTH, expand=True)

        # 5. Reproducir sonido en segundo plano (Requisito 3.10)
        SonidoManager.emitir_sonido_transformacion()

        # 6. Actualizar pantalla y estado
        self._set_estado(f"Aplicado: {operacion} con éxito.")
        self._actualizar_info_dimensiones()
        self._redibujar_imagen()
        self._actualizar_estado_controles()

    def cancelar_vista_previa(self):
        """
        Descarta la vista previa en curso y conserva la imagen anterior sin modificaciones.
        """
        if self.imagen_previa is None:
            return

        self.imagen_previa = None
        self.operacion_pendiente = None
        self.modo_recorte_activo = False

        self.frame_confirmacion.pack_forget()
        self.frame_dividido.pack_forget()
        self.canvas_normal.pack(fill=tk.BOTH, expand=True)

        self._set_estado("Vista previa cancelada. Imagen conservada sin cambios.")
        self._redibujar_imagen()
        self._actualizar_estado_controles()

    # -------------------------------------------------------------
    # 3.9 HISTORIAL (DESHACER Y REHACER)
    # -------------------------------------------------------------

    def accion_deshacer(self):
        """Retrocede un cambio en el historial."""
        if not self.imagen_actual:
            return

        # Si hay vista previa activa, primero se cancela
        if self.imagen_previa is not None:
            self.cancelar_vista_previa()
            return

        nueva_imagen = self.historial.deshacer(self.imagen_actual)
        if nueva_imagen is not None:
            self.imagen_actual = nueva_imagen
            self._set_estado("Operación deshecha.")
            self._actualizar_info_dimensiones()
            self._redibujar_imagen()
            self._actualizar_estado_controles()
            SonidoManager.emitir_sonido_transformacion()
        else:
            self._set_estado("No hay más acciones para deshacer.")
            messagebox.showinfo("Historial", "Se encuentra en el principio del historial. No hay más acciones para deshacer.")

    def accion_rehacer(self):
        """Avanza un cambio en el historial."""
        if not self.imagen_actual:
            return

        if self.imagen_previa is not None:
            self.cancelar_vista_previa()
            return

        nueva_imagen = self.historial.rehacer(self.imagen_actual)
        if nueva_imagen is not None:
            self.imagen_actual = nueva_imagen
            self._set_estado("Operación rehecha.")
            self._actualizar_info_dimensiones()
            self._redibujar_imagen()
            self._actualizar_estado_controles()
            SonidoManager.emitir_sonido_transformacion()
        else:
            self._set_estado("No hay más acciones para rehacer.")
            messagebox.showinfo("Historial", "Se encuentra en el final del historial. No hay más acciones para rehacer.")

    # -------------------------------------------------------------
    # DISPARADORES DE TRANSFORMACIONES (Punto 3.4)
    # -------------------------------------------------------------

    def transformar_volteo_h(self):
        """Volteo horizontal utilizando el método de e15.py."""
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.voltear_horizontal(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Voltear Horizontal (Espejo - e15.py)")

    def transformar_volteo_v(self):
        """Volteo vertical."""
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.voltear_vertical(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Voltear Vertical")

    def transformar_rotar_90_der(self):
        """Rotar 90° horario utilizando el método de e17.py."""
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.rotar_90_derecha(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Rotar 90° Derecha (e17.py)")

    def transformar_rotar_90_izq(self):
        """Rotar 90° antihorario."""
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.rotar_90_izquierda(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Rotar 90° Izquierda")

    def transformar_rotar_180(self):
        """Rotar 180° utilizando el método de e17.py."""
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.rotar_180(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Rotar 180° (e17.py)")

    def transformar_grises(self):
        """Conversión a escala de grises con fórmula de luminancia de e16.py."""
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.convertir_a_grises(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Escala de Grises (Luminancia perceptiva - e16.py)")

    def abrir_panel_binarizar(self):
        """Abre ventana modal interactiva para seleccionar el umbral de binarización."""
        if not self._validar_imagen_cargada(): return

        ventana_bin = tk.Toplevel(self.root)
        ventana_bin.title("Binarización (Blanco y Negro)")
        ventana_bin.geometry("380x180")
        ventana_bin.resizable(False, False)
        ventana_bin.transient(self.root)
        ventana_bin.grab_set()

        lbl_instruccion = tk.Label(
            ventana_bin, 
            text="Ajuste el umbral de binarización [0 - 255]:\n(Observe la vista previa en tiempo real)",
            font=("Arial", 9, "bold"),
            pady=5
        )
        lbl_instruccion.pack()

        val_umbral = tk.IntVar(value=128)
        lbl_val = tk.Label(ventana_bin, text="Umbral: 128", font=("Arial", 10))
        lbl_val.pack()

        def actualizar_bin(val):
            u = int(val)
            lbl_val.config(text=f"Umbral: {u}")
            resultado = ProcesadorImagen.binarizar(self.imagen_actual, u)
            self.iniciar_vista_previa(resultado, f"Binarizar (Umbral {u})")

        slider = tk.Scale(
            ventana_bin, 
            from_=0, 
            to=255, 
            orient=tk.HORIZONTAL, 
            variable=val_umbral, 
            length=300,
            command=actualizar_bin
        )
        slider.pack(pady=5)

        # Generar vista inicial
        actualizar_bin(128)

        frame_btns = tk.Frame(ventana_bin)
        frame_btns.pack(pady=10)

        def confirmar_y_cerrar():
            ventana_bin.destroy()
            self.confirmar_vista_previa()

        def cancelar_y_cerrar():
            ventana_bin.destroy()
            self.cancelar_vista_previa()

        tk.Button(frame_btns, text="✓ Aplicar", bg="#27AE60", fg="white", font=("Arial", 9, "bold"), width=10, command=confirmar_y_cerrar).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="✕ Cancelar", bg="#C0392B", fg="white", font=("Arial", 9, "bold"), width=10, command=cancelar_y_cerrar).pack(side=tk.LEFT, padx=5)

    # -------------------------------------------------------------
    # DISPARADORES DE FILTROS (Punto 3.5)
    # -------------------------------------------------------------

    def aplicar_filtro_desenfoque(self):
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.filtro_desenfoque(self.imagen_actual, radio=2.0)
        self.iniciar_vista_previa(resultado, "Filtro: Desenfoque (Blur / Gaussiano)")

    def aplicar_filtro_nitidez(self):
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.filtro_nitidez(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Filtro: Nitidez (Sharpen)")

    def aplicar_filtro_bordes(self):
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.filtro_bordes(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Filtro: Detección de Bordes")

    def aplicar_filtro_negativo(self):
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.filtro_negativo(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Filtro: Negativo (Inversión)")

    def aplicar_filtro_sepia(self):
        if not self._validar_imagen_cargada(): return
        resultado = ProcesadorImagen.filtro_sepia(self.imagen_actual)
        self.iniciar_vista_previa(resultado, "Filtro: Tono Sepia (Vintage)")

    # -------------------------------------------------------------
    # AJUSTES DE BRILLO, CONTRASTE Y SATURACIÓN (Punto 3.7)
    # -------------------------------------------------------------

    def abrir_panel_ajustes(self):
        """Ventana modal interactiva con sliders para ajustar Brillo, Contraste y Saturación."""
        if not self._validar_imagen_cargada(): return

        ventana_ajustes = tk.Toplevel(self.root)
        ventana_ajustes.title("Ajustes de Imagen")
        ventana_ajustes.geometry("400x320")
        ventana_ajustes.resizable(False, False)
        ventana_ajustes.transient(self.root)
        ventana_ajustes.grab_set()

        lbl_titulo = tk.Label(
            ventana_ajustes, 
            text="Ajustes de Imagen en tiempo real\n(1.0 = Valor original)", 
            font=("Arial", 10, "bold"),
            pady=5
        )
        lbl_titulo.pack()

        # Variables
        var_brillo = tk.DoubleVar(value=1.0)
        var_contraste = tk.DoubleVar(value=1.0)
        var_saturacion = tk.DoubleVar(value=1.0)

        # Función de actualización en tiempo real
        def refrescar_ajustes(*args):
            b = var_brillo.get()
            c = var_contraste.get()
            s = var_saturacion.get()
            lbl_b.config(text=f"Brillo: {b:.2f}")
            lbl_c.config(text=f"Contraste: {c:.2f}")
            lbl_s.config(text=f"Saturación: {s:.2f}")

            resultado = ProcesadorImagen.ajustar_propiedades(
                self.imagen_actual, brillo=b, contraste=c, saturacion=s
            )
            self.iniciar_vista_previa(resultado, f"Ajustes (B:{b:.2f}, C:{c:.2f}, S:{s:.2f})")

        # Slider Brillo
        lbl_b = tk.Label(ventana_ajustes, text="Brillo: 1.00", font=("Arial", 9))
        lbl_b.pack()
        s_b = tk.Scale(ventana_ajustes, from_=0.0, to=2.0, resolution=0.05, orient=tk.HORIZONTAL, variable=var_brillo, length=320, command=lambda v: refrescar_ajustes())
        s_b.pack()

        # Slider Contraste
        lbl_c = tk.Label(ventana_ajustes, text="Contraste: 1.00", font=("Arial", 9))
        lbl_c.pack()
        s_c = tk.Scale(ventana_ajustes, from_=0.0, to=2.0, resolution=0.05, orient=tk.HORIZONTAL, variable=var_contraste, length=320, command=lambda v: refrescar_ajustes())
        s_c.pack()

        # Slider Saturación
        lbl_s = tk.Label(ventana_ajustes, text="Saturación: 1.00", font=("Arial", 9))
        lbl_s.pack()
        s_s = tk.Scale(ventana_ajustes, from_=0.0, to=2.0, resolution=0.05, orient=tk.HORIZONTAL, variable=var_saturacion, length=320, command=lambda v: refrescar_ajustes())
        s_s.pack()

        def resetear_sliders():
            var_brillo.set(1.0)
            var_contraste.set(1.0)
            var_saturacion.set(1.0)
            refrescar_ajustes()

        frame_btns = tk.Frame(ventana_ajustes)
        frame_btns.pack(pady=12)

        def confirmar_y_salir():
            ventana_ajustes.destroy()
            self.confirmar_vista_previa()

        def cancelar_y_salir():
            ventana_ajustes.destroy()
            self.cancelar_vista_previa()

        tk.Button(frame_btns, text="✓ Confirmar", bg="#27AE60", fg="white", font=("Arial", 9, "bold"), width=10, command=confirmar_y_salir).pack(side=tk.LEFT, padx=4)
        tk.Button(frame_btns, text="Restablecer", bg="#7F8C8D", fg="white", font=("Arial", 9), width=10, command=resetear_sliders).pack(side=tk.LEFT, padx=4)
        tk.Button(frame_btns, text="✕ Cancelar", bg="#C0392B", fg="white", font=("Arial", 9, "bold"), width=10, command=cancelar_y_salir).pack(side=tk.LEFT, padx=4)

    # -------------------------------------------------------------
    # 3.6 RECORTAR (CROP) - MOUSE Y COORDENADAS
    # -------------------------------------------------------------

    def activar_herramienta_recorte(self):
        """Activa el modo de selección interactiva con el mouse sobre el lienzo."""
        if not self._validar_imagen_cargada(): return

        if self.imagen_previa is not None:
            self.cancelar_vista_previa()

        self.modo_recorte_activo = True
        self.canvas_normal.config(cursor="crosshair")
        self._set_estado("HERRAMIENTA RECORTE: Haga clic y arrastre con el ratón sobre la imagen para seleccionar el área.")

    def _on_mouse_press(self, event):
        """Inicio del arrastre del cuadro de selección."""
        if not self.modo_recorte_activo or not self.imagen_actual:
            return

        self.crop_x_inicio = event.x
        self.crop_y_inicio = event.y

        if self.crop_rect_id:
            self.canvas_normal.delete(self.crop_rect_id)
            self.crop_rect_id = None

        self.crop_rect_id = self.canvas_normal.create_rectangle(
            self.crop_x_inicio, self.crop_y_inicio, self.crop_x_inicio, self.crop_y_inicio,
            outline="#E74C3C", width=2, dash=(4, 4)
        )

    def _on_mouse_drag(self, event):
        """Actualización del cuadro delimitador mientras se mueve el mouse."""
        if not self.modo_recorte_activo or not self.crop_rect_id:
            return

        self.canvas_normal.coords(
            self.crop_rect_id,
            self.crop_x_inicio, self.crop_y_inicio, event.x, event.y
        )

    def _on_mouse_release(self, event):
        """Fin del arrastre: cálculo de coordenadas reales de la imagen y apertura de vista previa."""
        if not self.modo_recorte_activo or not self.crop_rect_id:
            return

        x_fin = event.x
        y_fin = event.y

        # Eliminar el rectángulo punteado del lienzo
        self.canvas_normal.delete(self.crop_rect_id)
        self.crop_rect_id = None
        self.canvas_normal.config(cursor="")
        self.modo_recorte_activo = False

        # Convertir de coordenadas del canvas a píxeles reales de la imagen
        # según la escala y desplazamiento visual
        c_x1 = min(self.crop_x_inicio, x_fin) - self.offset_x
        c_y1 = min(self.crop_y_inicio, y_fin) - self.offset_y
        c_x2 = max(self.crop_x_inicio, x_fin) - self.offset_x
        c_y2 = max(self.crop_y_inicio, y_fin) - self.offset_y

        if self.escala_visualizacion <= 0:
            return

        img_x1 = int(round(c_x1 / self.escala_visualizacion))
        img_y1 = int(round(c_y1 / self.escala_visualizacion))
        img_x2 = int(round(c_x2 / self.escala_visualizacion))
        img_y2 = int(round(c_y2 / self.escala_visualizacion))

        ancho, alto = self.imagen_actual.size
        img_x1 = max(0, min(ancho, img_x1))
        img_y1 = max(0, min(alto, img_y1))
        img_x2 = max(0, min(ancho, img_x2))
        img_y2 = max(0, min(alto, img_y2))

        # Validar tamaño mínimo de recorte (ej. al menos 5x5 px)
        if (img_x2 - img_x1) < 5 or (img_y2 - img_y1) < 5:
            self._set_estado("Selección de recorte descartada (área demasiado pequeña).")
            return

        try:
            resultado = ProcesadorImagen.recortar(self.imagen_actual, img_x1, img_y1, img_x2, img_y2)
            self.iniciar_vista_previa(resultado, f"Recorte ({img_x2 - img_x1}x{img_y2 - img_y1} px)")
        except Exception as e:
            messagebox.showerror("Error en recorte", str(e))

    def abrir_dialogo_recorte_coords(self):
        """Permite recortar la imagen ingresando coordenadas numéricas exactas."""
        if not self._validar_imagen_cargada(): return

        ancho, alto = self.imagen_actual.size

        ventana_coords = tk.Toplevel(self.root)
        ventana_coords.title("Recortar por Coordenadas")
        ventana_coords.geometry("340x260")
        ventana_coords.resizable(False, False)
        ventana_coords.transient(self.root)
        ventana_coords.grab_set()

        lbl_info = tk.Label(
            ventana_coords, 
            text=f"Dimensiones actuales: {ancho} x {alto} px\nIngrese el área a recortar:", 
            font=("Arial", 9, "bold"),
            pady=6
        )
        lbl_info.pack()

        frame_entradas = tk.Frame(ventana_coords)
        frame_entradas.pack(pady=5)

        tk.Label(frame_entradas, text="X1 (Izq):").grid(row=0, column=0, sticky=tk.E, padx=5, pady=4)
        e_x1 = tk.Entry(frame_entradas, width=10)
        e_x1.insert(0, "0")
        e_x1.grid(row=0, column=1, padx=5, pady=4)

        tk.Label(frame_entradas, text="Y1 (Arriba):").grid(row=1, column=0, sticky=tk.E, padx=5, pady=4)
        e_y1 = tk.Entry(frame_entradas, width=10)
        e_y1.insert(0, "0")
        e_y1.grid(row=1, column=1, padx=5, pady=4)

        tk.Label(frame_entradas, text="X2 (Der):").grid(row=2, column=0, sticky=tk.E, padx=5, pady=4)
        e_x2 = tk.Entry(frame_entradas, width=10)
        e_x2.insert(0, str(ancho // 2))
        e_x2.grid(row=2, column=1, padx=5, pady=4)

        tk.Label(frame_entradas, text="Y2 (Abajo):").grid(row=3, column=0, sticky=tk.E, padx=5, pady=4)
        e_y2 = tk.Entry(frame_entradas, width=10)
        e_y2.insert(0, str(alto // 2))
        e_y2.grid(row=3, column=1, padx=5, pady=4)

        def procesar_coords():
            try:
                x1 = int(e_x1.get().strip())
                y1 = int(e_y1.get().strip())
                x2 = int(e_x2.get().strip())
                y2 = int(e_y2.get().strip())

                resultado = ProcesadorImagen.recortar(self.imagen_actual, x1, y1, x2, y2)
                ventana_coords.destroy()
                self.iniciar_vista_previa(resultado, f"Recorte por Coordenadas ({abs(x2-x1)}x{abs(y2-y1)} px)")
            except ValueError as ve:
                messagebox.showerror("Coordenadas inválidas", f"Ingrese valores numéricos válidos dentro del rango.\n{ve}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        frame_btns = tk.Frame(ventana_coords)
        frame_btns.pack(pady=10)

        tk.Button(frame_btns, text="✓ Vista Previa", bg="#27AE60", fg="white", font=("Arial", 9, "bold"), width=12, command=procesar_coords).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_btns, text="✕ Cancelar", bg="#C0392B", fg="white", font=("Arial", 9, "bold"), width=10, command=ventana_coords.destroy).pack(side=tk.LEFT, padx=5)

    # -------------------------------------------------------------
    # RENDERIZADO Y DIBUJADO DE IMÁGENES EN PANTALLA
    # -------------------------------------------------------------

    def _redibujar_imagen(self):
        """Dibuja la imagen actual centrada y escalada proporcionalmente en el canvas normal."""
        if not self.imagen_actual or self.frame_dividido.winfo_ismapped():
            return

        c_w = self.canvas_normal.winfo_width()
        c_h = self.canvas_normal.winfo_height()

        if c_w <= 1 or c_h <= 1:
            return  # Ventana aún no inicializada

        img_w, img_h = self.imagen_actual.size

        # Calcular factor de escala preservando relación de aspecto
        escala = min((c_w - 20) / img_w, (c_h - 20) / img_h, 1.0)
        escala = max(escala, 0.01)
        self.escala_visualizacion = escala

        nuevo_w = max(1, int(img_w * escala))
        nuevo_h = max(1, int(img_h * escala))

        # Redimensionar para pantalla con interpolación BILINEAR
        img_resample = self.imagen_actual.resize((nuevo_w, nuevo_h), Image.Resampling.BILINEAR)
        self._tk_img_normal = ImageTk.PhotoImage(img_resample)

        self.canvas_normal.delete("all")
        self.offset_x = (c_w - nuevo_w) // 2
        self.offset_y = (c_h - nuevo_h) // 2

        self.canvas_normal.create_image(
            self.offset_x, self.offset_y,
            anchor=tk.NW,
            image=self._tk_img_normal
        )

    def _dibujar_comparativa(self):
        """Dibuja en simultáneo el 'Antes' y el 'Después' en sus respectivos paneles."""
        if not self.imagen_actual or not self.imagen_previa:
            return

        self.root.update_idletasks()

        for canvas, img, es_antes in [
            (self.canvas_antes, self.imagen_actual, True),
            (self.canvas_despues, self.imagen_previa, False)
        ]:
            c_w = canvas.winfo_width()
            c_h = canvas.winfo_height()

            if c_w <= 1 or c_h <= 1:
                c_w, c_h = 350, 400

            img_w, img_h = img.size
            escala = min((c_w - 20) / img_w, (c_h - 20) / img_h, 1.0)
            escala = max(escala, 0.01)

            nuevo_w = max(1, int(img_w * escala))
            nuevo_h = max(1, int(img_h * escala))

            img_resample = img.resize((nuevo_w, nuevo_h), Image.Resampling.BILINEAR)
            tk_img = ImageTk.PhotoImage(img_resample)

            canvas.delete("all")
            off_x = (c_w - nuevo_w) // 2
            off_y = (c_h - nuevo_h) // 2

            canvas.create_image(off_x, off_y, anchor=tk.NW, image=tk_img)

            if es_antes:
                self._tk_img_antes = tk_img
            else:
                self._tk_img_despues = tk_img

    # -------------------------------------------------------------
    # MÉTODOS AUXILIARES DE ESTADO Y CONTROL
    # -------------------------------------------------------------

    def _validar_imagen_cargada(self) -> bool:
        """Verifica si hay una imagen lista para procesar."""
        if self.imagen_actual is None:
            messagebox.showwarning("Atención", "Primero debe abrir una imagen desde el menú Archivo -> Abrir.")
            return False
        return True

    def _actualizar_estado_controles(self):
        """Habilita o deshabilita botones del menú y toolbar según el contexto."""
        hay_imagen = self.imagen_actual is not None
        estado_img = tk.NORMAL if hay_imagen else tk.DISABLED

        # Menús
        for m in [self.menu_imagen, self.menu_filtros, self.menu_ajustes]:
            for i in range(m.index(tk.END) + 1):
                try:
                    m.entryconfig(i, state=estado_img)
                except Exception:
                    pass

        # Deshacer y Rehacer
        estado_deshacer = tk.NORMAL if self.historial.puede_deshacer() else tk.DISABLED
        estado_rehacer = tk.NORMAL if self.historial.puede_rehacer() else tk.DISABLED

        self.menu_editar.entryconfig("Deshacer (Ctrl+Z)", state=estado_deshacer)
        self.menu_editar.entryconfig("Rehacer (Ctrl+Y)", state=estado_rehacer)
        self.btn_deshacer.config(state=estado_deshacer)
        self.btn_rehacer.config(state=estado_rehacer)

        # Botones de herramientas
        self.btn_guardar.config(state=estado_img)
        self.btn_recortar_mouse.config(state=estado_img)
        self.btn_ajustes_color.config(state=estado_img)
        self.btn_binarizar.config(state=estado_img)

    def _set_estado(self, mensaje: str):
        """Actualiza el texto de la barra de estado inferior."""
        self.lbl_estado.config(text=mensaje)

    def _actualizar_info_dimensiones(self):
        """Muestra dimensiones y modo de color en la barra de estado."""
        if self.imagen_actual:
            w, h = self.imagen_actual.size
            modo = self.imagen_actual.mode
            self.lbl_dimensiones.config(text=f"{w} x {h} px | {modo}")
        else:
            self.lbl_dimensiones.config(text="0 x 0 px")

    def mostrar_atajos(self):
        """Muestra ventana con la lista de atajos de teclado."""
        texto = (
            "Atajos de teclado del Editor:\n\n"
            "• Ctrl + O : Abrir imagen\n"
            "• Ctrl + S : Guardar imagen procesada\n"
            "• Ctrl + Z : Deshacer cambio\n"
            "• Ctrl + Y : Rehacer cambio\n"
            "• Enter    : Confirmar vista previa activa\n"
            "• Escape   : Cancelar vista previa activa\n"
        )
        messagebox.showinfo("Atajos de teclado", texto)

    def mostrar_acerca_de(self):
        """Información del proyecto."""
        texto = (
            "Editor de Imágenes - TPL3\n"
            "Programación II · 5.º año\n"
            "IPETyM N° 246 'Dr. Amadeo Sabattini'\n\n"
            "Docente: Ing. Federico Coronati\n"
            "Desarrollado en Python con Tkinter, Pillow y NumPy.\n"
            "Incluye métodos matriciales de e15, e16, e17 y e18."
        )
        messagebox.showinfo("Acerca del Editor", texto)
