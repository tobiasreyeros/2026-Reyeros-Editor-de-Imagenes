"""
Módulo de Gestión de Sonido
---------------------------
Cumple con el Requisito 3.10 del PDF:
"Cada vez que se aplique una transformación se debe reproducir un sonido.
Puede ser un beep del sistema o un sonido personalizado. El sonido no debe congelar la interfaz."

Utiliza winsound en entornos Windows y ejecuta la emisión en un hilo secundario
(threading.Thread) para que la interfaz gráfica permanezca completamente fluida.
"""

import sys
import threading


class SonidoManager:
    """
    Controlador para la reproducción de sonidos del sistema sin congelar la interfaz.
    """

    @staticmethod
    def _reproducir_beep():
        """Función interna que emite el sonido."""
        try:
            if sys.platform == "win32":
                import winsound
                # Emite un sonido de notificación del sistema o un tono suave
                winsound.MessageBeep(winsound.MB_OK)
            else:
                # Fallback para otros sistemas operativos
                print("\a", end="", flush=True)
        except Exception:
            # En caso de no haber dispositivo de sonido, no interrumpe el programa
            pass

    @classmethod
    def emitir_sonido_transformacion(cls):
        """
        Lanza la reproducción del sonido en un hilo secundario independiente (daemon),
        asegurando que la interfaz de usuario no sufra ningún bloqueo ni congelamiento.
        """
        hilo = threading.Thread(target=cls._reproducir_beep, daemon=True)
        hilo.start()
