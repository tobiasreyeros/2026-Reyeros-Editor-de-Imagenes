"""
Módulo de Gestión de Historial (Deshacer y Rehacer)
---------------------------------------------------
Cumple con el Requisito 3.9 del PDF:
"La aplicación debe mantener un historial de cambios que permita deshacer
y rehacer las operaciones aplicadas, tantas veces como sea posible.
Se debe controlar qué ocurre al llegar al principio o al final del historial."
"""

from typing import Optional
from PIL import Image


class HistorialManager:
    """
    Gestiona dos pilas (stacks) LIFO para Deshacer (Undo) y Rehacer (Redo),
    almacenando copias independientes de las imágenes para evitar efectos secundarios.
    """

    def __init__(self, limite_maximo: int = 30):
        self.pila_deshacer: list[Image.Image] = []
        self.pila_rehacer: list[Image.Image] = []
        self.limite_maximo = limite_maximo

    def registrar_cambio(self, imagen_actual: Image.Image):
        """
        Guarda el estado actual en la pila de deshacer antes de aplicar una nueva transformación.
        Limpia la pila de rehacer ya que se inicia una nueva línea temporal de cambios.
        """
        # Guardamos una copia exacta para aislar modificaciones
        self.pila_deshacer.append(imagen_actual.copy())
        
        # Limitamos el tamaño para optimizar el uso de memoria RAM
        if len(self.pila_deshacer) > self.limite_maximo:
            self.pila_deshacer.pop(0)

        # Cualquier nueva acción descarta el camino de rehacer
        self.pila_rehacer.clear()

    def deshacer(self, imagen_actual: Image.Image) -> Optional[Image.Image]:
        """
        Retrocede un paso en el historial:
        - Envía el estado actual a la pila de rehacer.
        - Extrae y retorna el estado previo de la pila de deshacer.
        Retorna None si ya se encuentra al inicio del historial.
        """
        if not self.puede_deshacer():
            return None

        # El estado actual pasa a rehacer
        self.pila_rehacer.append(imagen_actual.copy())
        # Recuperamos el último estado guardado
        return self.pila_deshacer.pop()

    def rehacer(self, imagen_actual: Image.Image) -> Optional[Image.Image]:
        """
        Avanza un paso en el historial:
        - Envía el estado actual a la pila de deshacer.
        - Extrae y retorna el estado siguiente de la pila de rehacer.
        Retorna None si ya se encuentra al final del historial.
        """
        if not self.puede_rehacer():
            return None

        # El estado actual vuelve a deshacer
        self.pila_deshacer.append(imagen_actual.copy())
        # Recuperamos el estado adelantado
        return self.pila_rehacer.pop()

    def puede_deshacer(self) -> bool:
        """Indica si existen estados previos disponibles para deshacer."""
        return len(self.pila_deshacer) > 0

    def puede_rehacer(self) -> bool:
        """Indica si existen estados posteriores disponibles para rehacer."""
        return len(self.pila_rehacer) > 0

    def reiniciar(self):
        """Limpia ambas pilas al abrir una nueva imagen o reiniciar el proyecto."""
        self.pila_deshacer.clear()
        self.pila_rehacer.clear()
