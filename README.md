# 2026-Reyeros-Editor-de-Imagenes

Aplicación de escritorio para procesamiento, edición interactiva y despacho de imágenes por correo electrónico vía SMTP desarrollada en Python con Tkinter, Pillow y NumPy para la asignatura **Programación II** (5.º año - IPETyM N° 246 "Dr. Amadeo Sabattini").

---

## 1. Descripción del Proyecto y Capturas de Pantalla

### Descripción
El proyecto consiste en un editor de imágenes integral para Windows diseñado bajo una arquitectura modular y orientada a objetos (POO). Permite al usuario:
- Cargar imágenes desde el sistema de archivos en tiempo de ejecución validando formatos (`.jpg`, `.jpeg`, `.png`, `.bmp`).
- Aplicar transformaciones matriciales y filtros basados en algoritmos desarrollados en clase (`e15.py`, `e16.py`, `e17.py`, `e18.py`).
- Previsualizar los cambios en modo comparativo obligatorio ("Original / Antes" vs "Vista Previa / Después") con botones de confirmación y cancelación previa.
- Gestionar un historial completo de deshacer y rehacer con retroalimentación sonora no bloqueante mediante subprocesos (`threading` + `winsound`).
- Enviar la imagen resultante como archivo adjunto a través del protocolo SMTP seguro de Gmail (con fallback automático entre puertos 465 SSL y 587 STARTTLS) con compresión automática adaptativa ante el límite de 25 MB.
- Ejecutar la aplicación de forma autónoma sin necesidad de tener Python instalado mediante un ejecutable compilado (`.exe`).

### Capturas de Pantalla
> *Nota: Para visualizar las interfaces de la aplicación:*

<img width="1098" height="738" alt="image" src="https://github.com/user-attachments/assets/88c887dd-0cb9-4811-8d05-d0c046e611a2" />


<img width="476" height="588" alt="image" src="https://github.com/user-attachments/assets/e03b3ec0-3480-46fd-a412-49d06aeaf42b" />

## 2. Guía de Instalación

### 2.1 Cómo ejecutar la aplicación desde el código fuente
1. **Requisitos de entorno:**
   - Python 3.10 o superior (compatible con Python 3.10.x, 3.11.x, 3.12.x y 3.13.x en Windows).
   - Entorno Thonny IDE o terminal de comandos estándar.
2. **Instalación de dependencias:**
   Abra una terminal en la raíz del proyecto y ejecute:
   ```bash
   pip install -r requirements.txt
   ```
   *Dependencias necesarias:* `pillow>=10.0.0`, `numpy>=1.24.0`, `python-dotenv>=1.0.0`.
3. **Ejecución del programa:**
   ```bash
   python main.py
   ```
   O bien abra `main.py` desde **Thonny** y presione `F5` (o el botón verde de reproducir).

### 2.2 Cómo ejecutar el archivo .exe
1. Ingrese a la carpeta `dist/` en el directorio del proyecto.
2. Localice el archivo binario **`EditorDeImagenes.exe`**.
3. Haga doble clic para iniciarlo directamente.
   - **No requiere instalación previa de Python ni paquetes adicionales:** el archivo empaqueta de forma autónoma el intérprete, bibliotecas gráficas (`Tkinter`), librerías matriciales (`NumPy`, `Pillow`) y componentes de red (`smtplib`, `ssl`).

### 2.3 Cómo configurar las credenciales / variables de entorno para el correo
La aplicación está configurada para conectarse a través del protocolo SMTP seguro de Google utilizando una **Contraseña de Aplicación de Gmail (App Password)** de 16 caracteres:
1. **Configuración en el código:**
   Abra el archivo `correo.py` y verifique la variable `GMAIL_APP_PASSWORD`:
   ```python
   GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
   ```
   *(La función interna `.replace(" ", "").strip()` remueve automáticamente los espacios en blanco, admitiendo tanto el formato espaciado de 16 caracteres de Google como la cadena continua).*
2. **Configuración mediante archivo `.env` o variables de entorno del sistema:**
   Si desea desacoplar la contraseña del código fuente, defina en un archivo `.env` o en las variables de entorno de Windows:
   ```env
   GMAIL_APP_PASS=xxxx xxxx xxxx xxxx
   GMAIL_USER=tobiastrabajo2@gmail.com
   ```

---

## 3. Guía de Uso Paso a Paso

### 3.1 Abrir una imagen
1. Vaya a **Archivo** -> **Abrir imagen...** o presione el atajo `Ctrl + O` (o el botón **📂 Abrir** en la barra de herramientas).
2. Seleccione un archivo compatible (`.jpg`, `.jpeg`, `.png`, `.bmp`).
3. La aplicación valida el archivo con `Image.verify()` y lo muestra ajustado proporcionalmente al Canvas principal.

### 3.2 Aplicar Transformaciones y Filtros
1. Seleccione una operación en el menú **Imagen** (volteos, rotaciones, grises, binarización) o **Filtros** (desenfoque, nitidez, bordes, negativo, sepia).
2. Se activará la **Vista Previa Dividida**:
   - Panel izquierdo: **ORIGINAL (Antes)**.
   - Panel derecho: **VISTA PREVIA (Después)**.
3. En la barra superior de confirmación:
   - Pulse **✓ Confirmar Cambio** (o tecla `Enter`) para aplicar definitivamente la transformación al historial (reproducirá un sonido en segundo plano).
   - Pulse **✕ Cancelar** (o tecla `Escape`) para descartar el resultado.

### 3.3 Recorte de Imagen (Crop)
- **Con el mouse:**
  1. Pulse **✂ Recortar Mouse** o elija **Imagen** -> **Recortar con el mouse**.
  2. Arrastre sobre el lienzo con clic izquierdo presionado formando un recuadro punteado.
  3. Al soltar, se abrirá la vista previa del recorte para confirmar o cancelar.
- **Por coordenadas:**
  1. Seleccione **Imagen** -> **Recortar por coordenadas...**.
  2. Ingrese los valores numéricos $X_1, Y_1, X_2, Y_2$ y presione **Vista Previa**.

### 3.4 Ajustes de Brillo, Contraste, Saturación y Binarización
- **Brillo, Contraste y Saturación:**  
  Vaya a **Ajustes** -> **Brillo, Contraste y Saturación...** o use el botón **🎚 Brillo/Contraste**. Mueva los sliders entre `0.0` y `2.0` para ver el efecto en tiempo real.
- **Binarización:**  
  Vaya a **Imagen** -> **Binarizar (Blanco y Negro ajustable)...**. Calibre el umbral numérico entre `0` y `255`.

### 3.5 Historial: Deshacer y Rehacer
- Presione `Ctrl + Z` o **↶ Deshacer** para revertir una acción.
- Presione `Ctrl + Y` o **↷ Rehacer** para restablecerla.

### 3.6 Guardar la imagen procesada
1. Seleccione **Archivo** -> **Guardar como...** o presione `Ctrl + S`.
2. Elija nombre, ruta y formato (`.png`, `.jpg`, `.bmp`). Si una imagen con transparencia se guarda en JPEG, el sistema la compone automáticamente sobre fondo blanco para evitar errores.

### 3.7 Enviar imagen por correo electrónico (Gmail)
1. Presione **📧 Enviar Correo**, vaya a **Archivo** -> **Enviar por correo...** o presione `Ctrl + M`.
2. En la ventana modal:
   - Verifique el correo remitente (`tobiastrabajo2@gmail.com`).
   - Seleccione el destinatario en el menú desplegable o escriba uno nuevo.
   - Complete el asunto, mensaje y el formato del adjunto (`PNG` o `JPEG`).
3. Haga clic en **📤 ENVIAR POR GMAIL**.
4. El correo se despacha de forma asíncrona mediante sockets seguros sin congelar la ventana principal.

---

## 4. Descripción de cada Función de la Aplicación

### Módulo de Interfaz Gráfica (`interfaz.py` y `main.py`)
- **`EditorApp.__init__()`**: Inicializa la ventana principal Tkinter, gestores de historial/sonido, barras de herramientas, atajos y lienzo de renderizado.
- **`abrir_imagen()`**: Abre el cuadro de diálogo del SO y valida la integridad del archivo mediante Pillow.
- **`guardar_como()`**: Controla la exportación en disco y asegura compatibilidad de formatos.
- **`abrir_dialogo_correo()`**: Despliega la ventana modal de correo con formulario completo, botones inferiores fijos y scrollbar para evitar recortes en pantallas de cualquier resolución.
- **`iniciar_vista_previa()`, `confirmar_vista_previa()`, `cancelar_vista_previa()`**: Gestionan la vista previa comparativa obligatoria antes/después (Requisito 3.8).
- **`activar_herramienta_recorte()`, `_on_mouse_press()`, `_on_mouse_drag()`, `_on_mouse_release()`**: Coordinan la selección visual interactiva sobre el canvas y traducen las coordenadas a escala real de la imagen.
- **`abrir_panel_ajustes()` / `abrir_panel_binarizar()`**: Ventanas modales interactivas con actualización en tiempo real.
- **`accion_deshacer()` / `accion_rehacer()`**: Integración con las pilas LIFO del historial.

### Módulo de Procesamiento Matricial (`procesador.py`)
- **`voltear_horizontal(imagen)`**: Invierte el eje de columnas (`arr[:, ::-1]`) implementando el método de intercambio de columnas de `e15.py`.
- **`voltear_vertical(imagen)`**: Invierte el eje de filas (`arr[::-1, :]`).
- **`rotar_90_derecha(imagen)`**: Rota 90° horario mediante transposición e inversión de filas según la lógica de `e17.py`.
- **`rotar_90_izquierda(imagen)`**: Rota 90° antihorario (270°).
- **`rotar_180(imagen)`**: Rota 180° invirtiendo simultáneamente ambos ejes según `e17.py`.
- **`convertir_a_grises(imagen)`**: Aplica la fórmula de luminancia perceptiva de `e16.py`:
  $$\text{gris} = (R \times 0.2989) + (G \times 0.5870) + (B \times 0.1140)$$
- **`binarizar(imagen, umbral)`**: Segmenta la matriz de grises en blanco (255) o negro (0) en base a un corte paramétrico.
- **`filtro_desenfoque(imagen, radio)`**: Suavizado gaussiano basado en convolución (concepto de `e18.py`).
- **`filtro_nitidez(imagen)`**: Realce de detalles finos (Sharpen).
- **`filtro_bordes(imagen)`**: Detección de contornos y gradientes espaciales.
- **`filtro_negativo(imagen)`**: Inversión tonal matemática ($255 - x$).
- **`filtro_sepia(imagen)`**: Transformación de color cromática para efecto vintage.
- **`recortar(imagen, x1, y1, x2, y2)`**: Recorte por coordenadas rectangulares delimitadas.
- **`ajustar_propiedades(imagen, brillo, contraste, saturacion)`**: Calibración multiplicativa de brillo, contraste y saturación con ImageEnhance.
- **`preparar_para_guardar(imagen, ruta)`**: Acondicionamiento de imágenes con canal alfa sobre fondos neutros para formatos incompatibles (JPEG).

### Módulo de Historial (`historial.py`)
- **`HistorialManager`**: Implementa dos pilas LIFO (`pila_deshacer` y `pila_rehacer`) con aislamiento de copias de memoria (`.copy()`), limitando la memoria a 25 estados.

### Módulo de Sonido (`sonido.py`)
- **`SonidoManager.emitir_sonido_transformacion()`**: Emite `winsound.MessageBeep(winsound.MB_OK)` en un hilo secundario (`threading.Thread` en modo `daemon=True`) cumpliendo con el requisito 3.10 de no congelar la GUI.

### Módulo de Correo (`correo.py`)
- **`GestorCorreo.validar_formato_correo(correo)`**: Validación con expresión regular para direcciones válidas.
- **`GestorCorreo.preparar_adjunto_con_limite(imagen, formato)`**: Serialización en memoria y compresión progresiva adaptativa ante el límite de 25 MB.
- **`GestorCorreo.enviar_correo(...)`**: Construcción del mensaje MIME y despacho seguro con conmutación redundante entre puertos 465 (SSL) y 587 (STARTTLS).

---

## 5. Prueba de Envío por Correo y Cómo se Resolvió el Límite de 25 MB

### 5.1 Resolución técnica del límite de 25 MB
1. **Impacto de la codificación Base64:**  
   Los protocolos de correo electrónico (MIME) transmiten archivos binarios codificados en caracteres ASCII usando Base64. Esta codificación convierte cada 3 bytes binarios en 4 caracteres de texto, produciendo un **incremento de tamaño del 33% al 35%**:
   $$\text{Tamaño MIME} \approx \text{Tamaño Binario} \times 1.35$$
   Por esta razón, un adjunto que en disco pesa 20 MB alcanzará aproximadamente ~27 MB codificado, superando el límite de 25 MB del servidor SMTP de Gmail.

2. **Algoritmo de compresión adaptativo:**  
   En `correo.py`, el método `preparar_adjunto_con_limite()` calcula el peso codificado en memoria. Si la imagen proyectada supera el umbral de seguridad de 24.5 MB:
   - Se convierte automáticamente a formato JPEG optimizado.
   - Si persiste el exceso, se reduce gradualmente el factor de compresión (calidad desde 85% hasta 40%).
   - Si aún sobrepasa el límite, se aplica un reescalado proporcional de resolución (algoritmo LANCZOS al 80%) de forma iterativa hasta garantizar un tamaño estrictamente menor a 25 MB.
   - El sistema notifica al usuario que la imagen fue optimizada automáticamente al emitir el mensaje de éxito.

3. **Conexión robusta y redundante:**  
   Se utiliza un contexto SSL explícito (`ssl.create_default_context()`) que opera en puerto 465 (SMTPS directo) con conmutación automática al puerto 587 (STARTTLS), solucionando cualquier cierre de socket en redes escolares y en el ejecutable `.exe`.

---

## 6. Limitaciones, Errores Conocidos y Autor

### Limitaciones y errores conocidos
- **Formatos de imagen admitidos:** La aplicación está diseñada para imágenes fijas (`.jpg`, `.jpeg`, `.png`, `.bmp`). Formatos animados (GIF multicapa) o vectoriales (SVG) no son procesados en esta versión.
- **Área mínima de recorte:** Para evitar errores accidentales por clics aislados del ratón, el área mínima permitida de recorte es de 5x5 píxeles.
- **Dependencia de credenciales de Google:** El envío de correos requiere que la cuenta emisora tenga activa la verificación en dos pasos y una contraseña de aplicación generada por Google.

### Autor
- **Estudiante:** Tobias Reyeros
- **Curso:** 5.º año
- **Asignatura:** Programación II
- **Institución:** IPETyM N° 246 "Dr. Amadeo Sabattini"
- **Docente:** Ing. Federico Coronati
