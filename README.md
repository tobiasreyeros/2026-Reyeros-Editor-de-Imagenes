# 2026-Reyeros-Editor-de-Imagenes

Aplicación de escritorio para procesamiento y edición interactiva de imágenes desarrollada en Python con Tkinter, Pillow y NumPy para la asignatura **Programación II** (5.º año - IPETyM N° 246 "Dr. Amadeo Sabattini").

---

## 1. Descripción del Proyecto

El proyecto es un editor de imágenes de escritorio diseñado bajo una arquitectura modular y orientada a objetos (POO). Permite al usuario cargar imágenes en formatos estándar (JPG, PNG, BMP) desde el sistema operativo en tiempo de ejecución, aplicar transformaciones geométricas y filtros con algoritmos matriciales propios (basados en los trabajos prácticos previos `e15.py`, `e16.py`, `e17.py` y `e18.py`), comparar cambios en una vista previa comparativa obligatoria ("Antes / Después") antes de confirmar y gestionar un historial multinivel de deshacer/rehacer con retroalimentación sonora no bloqueante.

---

## 2. Guía de Uso Paso a Paso

### 2.1 Abrir una imagen
1. Vaya al menú superior **Archivo** -> **Abrir imagen...** o presione el atajo de teclado `Ctrl + O` (o el botón **📂 Abrir** en la barra de herramientas).
2. Seleccione un archivo de imagen compatible (`.jpg`, `.jpeg`, `.png`, `.bmp`) mediante el cuadro de diálogo.
3. La imagen se centrará y escalará proporcionalmente en el área de trabajo, mostrando sus dimensiones y modo de color en la barra de estado inferior.

### 2.2 Aplicar Transformaciones o Filtros
1. Seleccione la operación deseada desde los menús **Imagen**, **Filtros** o la barra de herramientas (por ejemplo: rotar 90°, escala de grises o sepia).
2. La interfaz activará el **Modo Vista Previa Dividida**:
   * A la izquierda verá el panel **ORIGINAL (Antes)**.
   * A la derecha verá el panel **VISTA PREVIA (Después)** con el resultado del filtro.
3. En la barra superior de confirmación:
   * Haga clic en **✓ Confirmar Cambio** (o presione `Enter`) para aplicar la operación de forma definitiva. Se emitirá un sonido de confirmación y el cambio pasará al historial.
   * Haga clic en **✕ Cancelar** (o presione `Escape`) para descartar el resultado y regresar a la imagen sin alteraciones.

### 2.3 Recortar una imagen (Crop)
* **Con el mouse:**
  1. Haga clic en el botón **✂ Recortar Mouse** o elija **Imagen** -> **Recortar con el mouse**.
  2. El cursor cambiará a cruz (`crosshair`). Mantenga presionado el botón izquierdo sobre la imagen y arrastre hasta formar el área deseada (se visualizará un rectángulo punteado en tiempo real).
  3. Al soltar el mouse, se abrirá la vista previa del recorte. Presione **Confirmar** para fijarlo o **Cancelar** para anularlo.
* **Por coordenadas numéricas:**
  1. Ingrese a **Imagen** -> **Recortar por coordenadas...**.
  2. Introduzca los valores numéricos correspondientes a $X_1$ (izquierda), $Y_1$ (arriba), $X_2$ (derecha) e $Y_2$ (abajo) dentro de los límites de la resolución.
  3. Presione **✓ Vista Previa** y confirme el resultado.

### 2.4 Ajustar Brillo, Contraste, Saturación y Binarización
* **Brillo, Contraste y Saturación:**
  1. Haga clic en **🎚 Brillo/Contraste** o elija **Ajustes** -> **Brillo, Contraste y Saturación...**.
  2. Mueva los deslizadores en un rango de `0.0` a `2.0` (donde `1.0` es el valor base original). La vista previa a la derecha se actualiza en tiempo real.
  3. Puede pulsar **Restablecer** para reiniciar los valores o **✓ Confirmar** para fijar la edición.
* **Binarización (Blanco y Negro con umbral graduable):**
  1. Haga clic en **🌓 Binarizar** o **Imagen** -> **Binarizar (Blanco y Negro ajustable)...**.
  2. Ajuste el control deslizante del umbral entre `0` y `255`. Los píxeles con intensidad mayor o igual al umbral se transformarán a blanco (255) y los menores a negro (0).
  3. Confirme o cancele según el resultado buscado.

### 2.5 Historial: Deshacer y Rehacer
* Presione `Ctrl + Z` o el botón **↶ Deshacer** para retroceder al estado previo.
* Presione `Ctrl + Y` o el botón **↷ Rehacer** para avanzar si se deshizo una acción.
* Si se alcanza el inicio o fin del historial, el sistema deshabilita los controles e informa mediante un aviso emergente.

### 2.6 Guardar la imagen procesada
1. Seleccione **Archivo** -> **Guardar como...** o presione `Ctrl + S`.
2. Elija la ubicación, nombre de archivo y formato de salida (`.png`, `.jpg`, `.bmp`).
3. El sistema valida automáticamente las incompatibilidades de canal alfa: si guarda una imagen con transparencia en formato JPEG, la fusiona sobre un fondo blanco para evitar fallas o corrupción del archivo.

---

## 3. Descripción de cada Función de la Aplicación

### Módulo de Interfaz y Control (`interfaz.py` y `main.py`)
* **`abrir_imagen()`:** Despliega el cuadro de selección de archivos del sistema operativo y valida mediante `Image.verify()` la integridad y compatibilidad del archivo cargado.
* **`guardar_como()`:** Gestiona el guardado en disco con manejo seguro de formatos.
* **`abrir_dialogo_correo()`:** Abre la ventana modal para redactar y enviar la imagen procesada por correo vía Gmail SMTP (acceso desde la barra de herramientas, menú Archivo o atajo `Ctrl + M`).
* **`iniciar_vista_previa()` / `confirmar_vista_previa()` / `cancelar_vista_previa()`:** Controlan el ciclo de vida del requisito 3.8 del PDF. Permiten evaluar lado a lado el estado "Antes" y "Después", aplicando o descartando el cambio.
* **`activar_herramienta_recorte()` / `_on_mouse_press()` / `_on_mouse_drag()` / `_on_mouse_release()`:** Capturan los eventos del ratón para proyectar la caja delimitadora en coordenadas del Canvas y calcular la correspondencia exacta con los píxeles reales de la imagen.
* **`abrir_dialogo_recorte_coords()`:** Ventana modal que valida y ejecuta el recorte matemático según coordenadas ingresadas por el usuario.
* **`abrir_panel_ajustes()`:** Panel interactivo para calibración simultánea de brillo, contraste y saturación con refresco dinámico.
* **`abrir_panel_binarizar()`:** Panel con control de umbral numérico interactivo.
* **`accion_deshacer()` / `accion_rehacer()`:** Conexión con el gestor de historial de cambios.

### Módulo de Procesamiento Matricial (`procesador.py`)
* **`voltear_horizontal(imagen)`:** Invierte las columnas de la matriz en el eje horizontal. Aplica el método del archivo de clase `e15.py` mediante la inversión matricial `arr[:, ::-1]`.
* **`voltear_vertical(imagen)`:** Invierte las filas de la matriz en el eje vertical (`arr[::-1, :]`).
* **`rotar_90_derecha(imagen)`:** Realiza una rotación horaria de 90°. Basado en el algoritmo de transposición y lectura inversa de filas de `e17.py`.
* **`rotar_90_izquierda(imagen)`:** Realiza una rotación antihoraria de 90° (270° horaria).
* **`rotar_180(imagen)`:** Rota la imagen 180° invirtiendo simultáneamente ejes de filas y columnas, tal como se implementó en `e17.py`.
* **`convertir_a_grises(imagen)`:** Transforma la imagen aplicando la fórmula de luminancia perceptiva de `e16.py`:
  $$\text{gris} = (R \times 0.2989) + (G \times 0.5870) + (B \times 0.1140)$$
* **`binarizar(imagen, umbral)`:** Convierte a escala de grises y segmenta la matriz con NumPy según el valor de corte definido por el usuario.
* **`filtro_desenfoque(imagen, radio)`:** Aplica un suavizado gaussiano basado en convolución (fundamentos de `e18.py`).
* **`filtro_nitidez(imagen)`:** Resalta bordes y contrastes finos (Sharpen).
* **`filtro_bordes(imagen)`:** Filtro de detección de contornos y gradientes de intensidad.
* **`filtro_negativo(imagen)`:** Invierte matemáticamente cada canal de color ($255 - \text{valor}$), preservando el canal alfa si existe.
* **`filtro_sepia(imagen)`:** Aplica la matriz de transformación cromática clásica para producir una tonalidad cálida de estilo vintage.
* **`recortar(imagen, x1, y1, x2, y2)`:** Extrae la submatriz rectangular delimitada, validando que no posea área nula ni exceda los límites de la imagen.
* **`ajustar_propiedades(imagen, brillo, contraste, saturacion)`:** Ajusta los factores multiplicativos de luminosidad, contraste y saturación tonal.
* **`preparar_para_guardar(imagen, ruta_destino)`:** Preprocesa la imagen antes de escribir en disco, evitando excepciones al guardar imágenes con transparencia en formatos que no la admiten como JPEG.

### Módulo de Historial (`historial.py`)
* **`HistorialManager`:** Administra dos pilas LIFO (`pila_deshacer` y `pila_rehacer`) con clonado independiente de imágenes (`.copy()`), limitando la profundidad de memoria para optimizar el consumo de memoria RAM.

### Módulo de Audio (`sonido.py`)
* **`SonidoManager`:** Utiliza `winsound.MessageBeep` en Windows. Dispara la reproducción en un hilo separado (`threading.Thread`) como proceso demonio (`daemon=True`) para garantizar que la interfaz gráfica no sufra congelamientos.

### Módulo de Correo Electrónico (`correo.py`)
* **`GestorCorreo`:** Implementa la lógica para el envío de imágenes procesadas mediante el protocolo SMTP_SSL (`smtp.gmail.com:465`) utilizando las librerías estándar `smtplib` y `email`.
  * **`validar_formato_correo(correo)`:** Valida sintácticamente la dirección de correo ingresada mediante una expresión regular.
  * **`preparar_adjunto_con_limite(imagen, formato)`:** Codifica la imagen adjunta en memoria y controla que el mensaje MIME completo en Base64 no sobrepase el límite estricto de 25 MB de Gmail. Aplica compresión progresiva en calidad y reescalado automático en caso de superar el umbral permitido.
  * **`enviar_correo(...)`:** Gestiona la autenticación segura, construcción del mensaje y despacho en hilo asíncrono, manejando fallas de conexión a internet, credenciales inválidas y rechazos del servidor.

---

## 4. Limitaciones y Errores Conocidos

* **Envío de correos temporalmente inactivo (estado incompleto):** Aunque el nuevo módulo `correo.py` y la interfaz de redacción están plenamente integrados en el código principal, los envíos de correo aún no se pueden realizar debido a que la contraseña de aplicación de Google (`GMAIL_APP_PASSWORD`) aún no ha sido configurada en el código.
* **Formatos de archivo admitidos:** La aplicación está optimizada para archivos JPEG, PNG y BMP. Formatos vectoriales (SVG) o de animación (GIF con múltiples cuadros) no están contemplados en esta etapa.
* **Recorte mínimo:** No se permite realizar recortes menores a 5x5 píxeles para evitar selecciones accidentales por clics aislados.
* **Empaquetado a ejecutable (.exe):** La generación del binario ejecutable independiente para Windows corresponde a la etapa final del proyecto.

---

## 5. Autor

* **Estudiante:** Tobias Reyeros
* **Materia:** Programación II · 5.º año
* **Institución:** IPETyM N° 246 "Dr. Amadeo Sabattini"
* **Docente:** Ing. Federico Coronati
