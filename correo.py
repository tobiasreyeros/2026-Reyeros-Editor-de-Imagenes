"""
Módulo de Envío de Correo Electrónico (SMTP Gmail)
--------------------------------------------------
Cumple con los Requisitos 3.11 y 4 del PDF:
- Envío de la imagen procesada como archivo adjunto mediante protocolo SMTP con SSL.
- Utiliza la biblioteca estándar smtplib y email.
- Validación estricta del formato de correo de destino.
- Control del límite técnico de 25 MB del mensaje completo codificado en Base64.
- Compresión y optimización automática si la imagen excede el límite permitido,
  notificando al usuario.
- Manejo exhaustivo de excepciones: sin conexión a internet, credenciales inválidas,
  dirección rechazada o fallos de conexión.

Autor: Proyecto Editor de Imágenes (5.º Año - IPETyM N° 246)
"""

import io
import os
import re
import smtplib
import socket
from email.message import EmailMessage
from typing import Optional, Tuple
from PIL import Image

# =============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN GMAIL (HARDCODEADA)
# =============================================================================
# Escribe aquí tu contraseña de aplicación de 16 caracteres generada en Google:
GMAIL_APP_PASSWORD = "ESCRIBE_AQUI_TU_CONTRASENA_DE_APLICACION"

# Correo remitente por defecto (cuenta utilizada en el TP)
REMITENTE_DEFAULT = "tobiastrabajo2@gmail.com"

# Lista de destinatarios frecuentes (profesores y compañeros de clase)
DESTINATARIOS_PREDEFINIDOS = [
    "fjcoronati@gmail.com",     # Docente 1 (Profesor del TP)
    "lafortaleza246@gmail.com", # Docente 2
    "mfedullo@gmail.com",       # Docente 3
    "elcrack35158@gmail.com",   # Compañero
    "tobiastrabajo2@gmail.com", # Correo propio
]

# Límite máximo estándar para Gmail en bytes (25 MB = 25 * 1024 * 1024)
# Se establece un margen de seguridad de 24.5 MB para garantizar aceptación por el servidor
LIMITE_MENSAJE_BYTES = int(24.5 * 1024 * 1024)

# Expresión regular estándar para validación sintáctica de direcciones de email
PATRON_EMAIL = re.compile(r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,}$")


class GestorCorreo:
    """
    Clase con la lógica de negocio para construir, validar, optimizar y despachar
    correos electrónicos con imágenes adjuntas a través de los servidores de Gmail.
    """

    @staticmethod
    def validar_formato_correo(correo: str) -> bool:
        """
        Valida que la dirección de correo tenga una estructura sintáctica válida (usuario@dominio.ext).
        """
        if not correo:
            return False
        return bool(PATRON_EMAIL.match(correo.strip()))

    @classmethod
    def preparar_adjunto_con_limite(
        cls, imagen: Image.Image, formato_salida: str = "PNG"
    ) -> Tuple[bytes, str, str, bool]:
        """
        Convierte la imagen a bytes y garantiza que el peso codificado no supere los 25 MB.
        
        Fundamento técnico (Punto 4 del PDF):
        La codificación Base64 requerida por el estándar MIME expande los datos en una
        relación de 4/3 (~33% de incremento de peso). Si el adjunto base64 excede el tope,
        este método aplica una compresión progresiva reduciendo dimensiones y calidad
        hasta encajar en el límite, retornando:
        (datos_bytes, nombre_archivo, subtipo_mime, fue_comprimida)
        """
        formato = formato_salida.upper()
        if formato not in ("JPEG", "JPG", "PNG"):
            formato = "PNG"

        subtipo = "jpeg" if formato in ("JPEG", "JPG") else "png"
        nombre_archivo = f"imagen_procesada.{'jpg' if subtipo == 'jpeg' else 'png'}"

        # 1. Intento inicial de exportación a memoria
        buffer = io.BytesIO()
        img_temp = imagen.copy()

        # Si es JPEG y viene con canal alfa (RGBA), convertir a fondo blanco
        if subtipo == "jpeg" and img_temp.mode in ("RGBA", "LA", "P"):
            fondo = Image.new("RGB", img_temp.size, (255, 255, 255))
            if img_temp.mode == "RGBA":
                fondo.paste(img_temp, mask=img_temp.split()[3])
            else:
                fondo.paste(img_temp.convert("RGB"))
            img_temp = fondo
        elif subtipo == "jpeg" and img_temp.mode != "RGB":
            img_temp = img_temp.convert("RGB")

        # Guardar en buffer en memoria
        if subtipo == "jpeg":
            img_temp.save(buffer, format="JPEG", quality=95)
        else:
            img_temp.save(buffer, format="PNG")

        datos_bytes = buffer.getvalue()
        peso_base64_estimado = len(datos_bytes) * 1.35  # Aproximación del peso MIME

        # Si no supera el límite de seguridad (aprox 18 MB binario -> 24.5 MB Base64), enviamos directo
        if peso_base64_estimado <= LIMITE_MENSAJE_BYTES:
            return datos_bytes, nombre_archivo, subtipo, False

        # 2. Si es demasiado pesada, iniciamos compresión y optimización progresiva
        fue_comprimida = True
        calidad = 85
        ancho, alto = img_temp.size

        # Forzamos conversión a JPEG para optimización de peso
        subtipo = "jpeg"
        nombre_archivo = "imagen_procesada_optimizada.jpg"
        if img_temp.mode != "RGB":
            fondo = Image.new("RGB", img_temp.size, (255, 255, 255))
            fondo.paste(img_temp.convert("RGB"))
            img_temp = fondo

        while True:
            buffer = io.BytesIO()
            img_temp.save(buffer, format="JPEG", quality=calidad, optimize=True)
            datos_bytes = buffer.getvalue()
            peso_base64_estimado = len(datos_bytes) * 1.35

            if peso_base64_estimado <= LIMITE_MENSAJE_BYTES:
                break

            # Reducir calidad gradualmente
            if calidad > 40:
                calidad -= 15
            else:
                # Si aún con baja calidad excede, reducir la resolución a un 80%
                ancho = int(ancho * 0.80)
                alto = int(alto * 0.80)
                if ancho < 100 or alto < 100:
                    break  # Evitar bucle infinito
                img_temp = img_temp.resize((ancho, alto), Image.Resampling.LANCZOS)
                calidad = 70

        return datos_bytes, nombre_archivo, subtipo, fue_comprimida

    @classmethod
    def enviar_correo(
        cls,
        remitente: str,
        destinatario: str,
        asunto: str,
        cuerpo_mensaje: str,
        imagen: Image.Image,
        formato_adjunto: str = "PNG",
    ) -> Tuple[bool, str, bool]:
        """
        Construye el mensaje MIME y lo transmite por el socket seguro SMTP_SSL de Gmail (puerto 465).
        
        Retorna una tupla: (exito: bool, mensaje_resultado: str, fue_comprimida: bool)
        """
        # Validar contraseña configurada
        password = GMAIL_APP_PASSWORD.strip()
        if not password or password == "ESCRIBE_AQUI_TU_CONTRASENA_DE_APLICACION":
            return (
                False,
                "No se ha configurado la contraseña de aplicación de Gmail.\n"
                "Por favor, edita la variable GMAIL_APP_PASSWORD en el archivo 'correo.py' "
                "con tu clave de 16 caracteres de Google.",
                False,
            )

        # Validaciones de entrada
        if not remitente or not cls.validar_formato_correo(remitente):
            return False, f"La dirección de correo del remitente '{remitente}' es inválida.", False

        if not destinatario or not cls.validar_formato_correo(destinatario):
            return False, f"La dirección de correo de destino '{destinatario}' no tiene un formato válido (ejemplo: usuario@correo.com).", False

        if not asunto.strip():
            return False, "Por favor, ingrese un asunto para el correo.", False

        # Preparar y codificar el adjunto con control estricto de 25 MB
        try:
            datos_bytes, nombre_adjunto, subtipo, fue_comprimida = cls.preparar_adjunto_con_limite(
                imagen, formato_salida=formato_adjunto
            )
        except Exception as e:
            return False, f"Error al procesar la imagen para adjuntar:\n{e}", False

        # Construir estructura del Email
        email = EmailMessage()
        email["From"] = remitente.strip()
        email["To"] = destinatario.strip()
        email["Subject"] = asunto.strip()
        email.set_content(cuerpo_mensaje)

        email.add_attachment(
            datos_bytes,
            maintype="image",
            subtype=subtipo,
            filename=nombre_adjunto,
        )

        # Verificar peso final exacto del mensaje codificado completo
        tamano_total_mime = len(email.as_bytes())
        if tamano_total_mime > (25 * 1024 * 1024):
            return (
                False,
                f"El mensaje completo codificado ({tamano_total_mime / (1024*1024):.2f} MB) "
                f"supera el límite permitido por Gmail de 25 MB.",
                fue_comprimida,
            )

        # Conectar y enviar vía SMTP_SSL
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as servidor:
                servidor.login(remitente.strip(), password)
                servidor.send_message(email)

            mensaje_exito = f"El correo se envió exitosamente a:\n{destinatario.strip()}"
            if fue_comprimida:
                mensaje_exito += (
                    "\n\n(Aviso técnico: la imagen fue optimizada y comprimida automáticamente "
                    "para no sobrepasar el límite de 25 MB de Gmail)."
                )

            return True, mensaje_exito, fue_comprimida

        except smtplib.SMTPAuthenticationError:
            return (
                False,
                "Error de autenticación: Las credenciales de Gmail son incorrectas.\n"
                "Verifica que el remitente y la contraseña de aplicación de 16 caracteres "
                "sean válidos y correspondan a la misma cuenta de Google.",
                fue_comprimida,
            )

        except (socket.gaierror, smtplib.SMTPConnectError, OSError) as e:
            return (
                False,
                f"Error de conexión: No se pudo conectar con el servidor 'smtp.gmail.com'.\n"
                f"Comprueba tu conexión a internet.\nDetalle: {e}",
                fue_comprimida,
            )

        except smtplib.SMTPRecipientsRefused:
            return (
                False,
                f"La dirección de correo de destino fue rechazada por el servidor: {destinatario}",
                fue_comprimida,
            )

        except Exception as e:
            return False, f"Ocurrió un error inesperado al enviar el correo:\n{e}", fue_comprimida
