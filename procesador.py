"""
Módulo de Procesamiento de Imágenes
----------------------------------
Implementa todas las transformaciones matemáticas, matriciales y filtros
solicitados en las especificaciones del TP (Puntos 3.4, 3.5, 3.6 y 3.7),
integrando los métodos vistos en clase en los archivos e15.py, e16.py, e17.py y e18.py.

Autor: Proyecto Editor de Imágenes (5.º Año - IPETyM N° 246)
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class ProcesadorImagen:
    """
    Clase encargada de realizar las transformaciones y filtros sobre imágenes
    utilizando NumPy y Pillow.
    """

    # -------------------------------------------------------------
    # 3.4 TRANSFORMACIONES
    # -------------------------------------------------------------

    @staticmethod
    def voltear_horizontal(imagen: Image.Image) -> Image.Image:
        """
        Invierte la imagen en el eje horizontal (espejo).
        
        MÉTODO BASADO EN e15.py:
        En e15.py se recorre cada fila y se intercambian los píxeles de las
        columnas exteriores hacia el centro:
            for i in range(filas):
                for j in range(columnas // 2):
                    aux = array[i][j]
                    array[i][j] = array[i][col - 1 - j]
                    array[i][col - 1 - j] = aux
        
        En NumPy, la operación vectorizada equivalente e instantánea es
        la inversión del eje de columnas: arr[:, ::-1].
        """
        arr = np.array(imagen)
        # Invertimos el orden de las columnas (eje 1), idéntico al algoritmo de e15.py
        arr_espejado = arr[:, ::-1]
        return Image.fromarray(arr_espejado)

    @staticmethod
    def voltear_vertical(imagen: Image.Image) -> Image.Image:
        """
        Invierte la imagen en el eje vertical (de arriba hacia abajo).
        Aplica la inversión de filas (eje 0): arr[::-1, :].
        """
        arr = np.array(imagen)
        arr_invertido = arr[::-1, :]
        return Image.fromarray(arr_invertido)

    @staticmethod
    def rotar_90_derecha(imagen: Image.Image) -> Image.Image:
        """
        Rota la imagen 90° en sentido horario (hacia la derecha).
        
        MÉTODO BASADO EN e17.py:
        En e17.py, la rotación de 90° se logra recorriendo las columnas de izquierda
        a derecha y las filas de abajo hacia arriba:
            for j in range(colum):
                for i in range(filas - 1, -1, -1):
                    nueva_fila.append(imagen[i][j])
        
        En álgebra matricial con NumPy, esto equivale a rotar 90 grados en sentido horario
        (k=-1 en np.rot90 sobre los ejes 0 y 1).
        """
        arr = np.array(imagen)
        # Rotación horaria de 90°
        arr_rotado = np.rot90(arr, k=-1, axes=(0, 1))
        return Image.fromarray(arr_rotado)

    @staticmethod
    def rotar_90_izquierda(imagen: Image.Image) -> Image.Image:
        """
        Rota la imagen 90° en sentido antihorario (hacia la izquierda / 270°).
        Equivale a k=1 en np.rot90.
        """
        arr = np.array(imagen)
        arr_rotado = np.rot90(arr, k=1, axes=(0, 1))
        return Image.fromarray(arr_rotado)

    @staticmethod
    def rotar_180(imagen: Image.Image) -> Image.Image:
        """
        Rota la imagen 180°.
        
        MÉTODO BASADO EN e17.py:
        En e17.py, la rotación de 180° se implementa recorriendo simultáneamente
        las filas y columnas en orden inverso:
            for i in range(filas - 1, -1, -1):
                for j in range(colum - 1, -1, -1):
                    nueva_fila.append(imagen[i][j])
        
        En NumPy equivale a invertir tanto filas como columnas: arr[::-1, ::-1].
        """
        arr = np.array(imagen)
        arr_rotado = arr[::-1, ::-1]
        return Image.fromarray(arr_rotado)

    @staticmethod
    def convertir_a_grises(imagen: Image.Image) -> Image.Image:
        """
        Convierte la imagen a escala de grises mediante ponderación perceptiva.
        
        MÉTODO BASADO EN e16.py:
        No se utiliza un promedio aritmético simple ((R+G+B)/3) porque el ojo humano
        no percibe los tres colores con el mismo brillo (sensibilidad mayor al verde).
        Se emplea la fórmula estándar de luminancia ITU-R BT.601:
            gris = (R * 0.2989) + (G * 0.5870) + (B * 0.1140)
        """
        # Aseguramos modo RGB para el cálculo
        img_rgb = imagen.convert("RGB")
        arr = np.array(img_rgb, dtype=np.float32)
        
        # Aplicamos la fórmula exacta de e16.py
        r = arr[:, :, 0]
        g = arr[:, :, 1]
        b = arr[:, :, 2]
        grises = (r * 0.2989) + (g * 0.5870) + (b * 0.1140)
        
        # Redondeamos y limitamos a rango uint8 [0, 255]
        grises_uint8 = np.clip(grises, 0, 255).astype(np.uint8)
        return Image.fromarray(grises_uint8, mode="L")

    @staticmethod
    def binarizar(imagen: Image.Image, umbral: int = 128) -> Image.Image:
        """
        Binariza la imagen (blanco y negro puro) en base a un umbral ajustable [0, 255].
        Píxeles con intensidad >= umbral se vuelven 255 (blanco), y menores se vuelven 0 (negro).
        """
        # Primero convertimos a escala de grises utilizando nuestro método de luminancia
        img_gris = ProcesadorImagen.convertir_a_grises(imagen)
        arr_gris = np.array(img_gris, dtype=np.uint8)
        
        # Binarización por comparación con el umbral seleccionado por el usuario
        arr_binario = np.where(arr_gris >= umbral, 255, 0).astype(np.uint8)
        return Image.fromarray(arr_binario, mode="L")

    # -------------------------------------------------------------
    # 3.5 FILTROS (Mínimo 3 requeridos, se proveen 5)
    # -------------------------------------------------------------

    @staticmethod
    def filtro_desenfoque(imagen: Image.Image, radio: float = 2.0) -> Image.Image:
        """
        Filtro de desenfoque gaussiano suave (Smooth / Blur).
        Basado en el concepto de convolución con kernel gaussiano de e18.py.
        """
        return imagen.filter(ImageFilter.GaussianBlur(radius=radio))

    @staticmethod
    def filtro_nitidez(imagen: Image.Image) -> Image.Image:
        """
        Filtro de nitidez (Sharpen / Realce de detalles).
        Acentúa los contrastes en las transiciones de color.
        """
        return imagen.filter(ImageFilter.SHARPEN)

    @staticmethod
    def filtro_bordes(imagen: Image.Image) -> Image.Image:
        """
        Filtro de detección de bordes (Find Edges / Gradiente).
        Destaca los contornos y transiciones bruscas de intensidad.
        """
        return imagen.filter(ImageFilter.FIND_EDGES)

    @staticmethod
    def filtro_negativo(imagen: Image.Image) -> Image.Image:
        """
        Filtro de negativo fotográfico (Inversión de color).
        Resta cada canal al valor máximo (255 - valor).
        """
        if imagen.mode == "RGBA":
            # Para RGBA invertimos los canales RGB pero conservamos el canal Alfa intacto
            r, g, b, a = imagen.split()
            r_inv = ImageOps.invert(r)
            g_inv = ImageOps.invert(g)
            b_inv = ImageOps.invert(b)
            return Image.merge("RGBA", (r_inv, g_inv, b_inv, a))
        elif imagen.mode == "RGB":
            return ImageOps.invert(imagen)
        elif imagen.mode == "L":
            return ImageOps.invert(imagen)
        else:
            return ImageOps.invert(imagen.convert("RGB"))

    @staticmethod
    def filtro_sepia(imagen: Image.Image) -> Image.Image:
        """
        Filtro de tono Sepia tradicional (efecto vintage).
        Aplica la matriz de transformación cromática estándar:
            R' = 0.393*R + 0.769*G + 0.189*B
            G' = 0.349*R + 0.686*G + 0.168*B
            B' = 0.272*R + 0.534*G + 0.131*B
        """
        img_rgb = imagen.convert("RGB")
        arr = np.array(img_rgb, dtype=np.float32)

        r = arr[:, :, 0]
        g = arr[:, :, 1]
        b = arr[:, :, 2]

        r_sepia = (r * 0.393) + (g * 0.769) + (b * 0.189)
        g_sepia = (r * 0.349) + (g * 0.686) + (b * 0.168)
        b_sepia = (r * 0.272) + (g * 0.534) + (b * 0.131)

        # Clampeamos valores a [0, 255]
        r_sepia = np.clip(r_sepia, 0, 255)
        g_sepia = np.clip(g_sepia, 0, 255)
        b_sepia = np.clip(b_sepia, 0, 255)

        arr_sepia = np.stack([r_sepia, g_sepia, b_sepia], axis=2).astype(np.uint8)
        resultado = Image.fromarray(arr_sepia, mode="RGB")

        # Si la imagen original tenía transparencia, la restauramos
        if imagen.mode == "RGBA":
            resultado = resultado.convert("RGBA")
            resultado.putalpha(imagen.split()[3])

        return resultado

    # -------------------------------------------------------------
    # 3.6 RECORTAR (CROP)
    # -------------------------------------------------------------

    @staticmethod
    def recortar(imagen: Image.Image, x1: int, y1: int, x2: int, y2: int) -> Image.Image:
        """
        Recorta la imagen a partir de una caja delimitadora (Bounding Box):
        (x1, y1, x2, y2).
        Valida que las coordenadas estén dentro de los límites de la imagen.
        """
        ancho, alto = imagen.size
        # Normalizar para que x1 < x2 e y1 < y2
        izq = max(0, min(x1, x2))
        arr = max(0, min(y1, y2))
        der = min(ancho, max(x1, x2))
        aba = min(alto, max(y1, y2))

        if izq >= der or arr >= aba:
            raise ValueError("El área de recorte seleccionada es inválida o tiene tamaño nulo.")

        return imagen.crop((izq, arr, der, aba))

    # -------------------------------------------------------------
    # 3.7 BRILLO, CONTRASTE Y SATURACIÓN
    # -------------------------------------------------------------

    @staticmethod
    def ajustar_propiedades(imagen: Image.Image, brillo: float = 1.0, 
                           contraste: float = 1.0, saturacion: float = 1.0) -> Image.Image:
        """
        Ajusta secuencialmente brillo, contraste y saturación con factores multiplicativos:
        1.0 representa el estado original sin alteraciones.
        """
        img_ajustada = imagen

        # Ajuste de Brillo
        if brillo != 1.0:
            potenciador_brillo = ImageEnhance.Brightness(img_ajustada)
            img_ajustada = potenciador_brillo.enhance(max(0.0, brillo))

        # Ajuste de Contraste
        if contraste != 1.0:
            potenciador_contraste = ImageEnhance.Contrast(img_ajustada)
            img_ajustada = potenciador_contraste.enhance(max(0.0, contraste))

        # Ajuste de Saturación / Color (solo si no es escala de grises pura)
        if saturacion != 1.0 and img_ajustada.mode != "L":
            potenciador_color = ImageEnhance.Color(img_ajustada)
            img_ajustada = potenciador_color.enhance(max(0.0, saturacion))

        return img_ajustada

    # -------------------------------------------------------------
    # 3.3 GUARDAR COMO (Manejo de incompatibilidad de formatos)
    # -------------------------------------------------------------

    @staticmethod
    def preparar_para_guardar(imagen: Image.Image, ruta_destino: str) -> tuple[Image.Image, dict]:
        """
        Prepara la imagen para ser guardada según el formato elegido.
        
        REQUISITO 3.3 DEL PDF:
        "Si el formato elegido no admite alguna característica de la imagen
        (por ejemplo, transparencia en JPG), la aplicación no debe fallar."
        
        Si se guarda en JPEG y la imagen posee transparencia (modo RGBA o P),
        se crea un fondo blanco de destino y se compone la imagen sobre este,
        evitando errores de guardado.
        """
        extension = ruta_destino.lower().split(".")[-1]
        opciones = {}
        img_final = imagen

        if extension in ["jpg", "jpeg"]:
            opciones["quality"] = 95
            if img_final.mode in ("RGBA", "LA") or (img_final.mode == "P" and "transparency" in img_final.info):
                # Crear fondo blanco para reemplazar transparencia
                img_rgba = img_final.convert("RGBA")
                fondo_blanco = Image.new("RGB", img_rgba.size, (255, 255, 255))
                fondo_blanco.paste(img_rgba, mask=img_rgba.split()[3])
                img_final = fondo_blanco
            elif img_final.mode != "RGB":
                img_final = img_final.convert("RGB")
        elif extension == "bmp":
            if img_final.mode == "RGBA":
                # BMP tradicional estándar prefiere RGB
                img_final = img_final.convert("RGB")

        return img_final, opciones
