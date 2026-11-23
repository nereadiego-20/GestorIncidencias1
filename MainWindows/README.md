# README - Diseño de la interfaz con PySide6

## Creación de la pantalla principal

Para hacer la interfaz del gestor de incidencias hemos utilizado **Qt Designer**, que viene con PySide6 y permite diseñar ventanas arrastrando componentes sin tener que programarlos directamente.

### 1. Crear la ventana

Primero abrimos Qt Designer y creamos una ventana de tipo `Main Window`.

Le cambiamos el título a **Gestor de incidencias** y le pusimos un tamaño de 1100 x 700 píxeles.

Después añadimos un layout vertical (`QVBoxLayout`) para organizar los elementos de la ventana.

### 2. Crear los botones superiores

En la parte superior añadimos un layout horizontal (`QHBoxLayout`) con tres botones (`QPushButton`):

- Incidencias
- Crear nueva incidencia
- Filtrar incidencias

Los colocamos uno al lado del otro y les cambiamos el color de fondo a azul con el texto blanco.

### 3. Crear la bandeja de incidencias

Debajo de los botones dividimos la pantalla en dos partes.

En la parte izquierda añadimos un `QFrame` que contiene:

- Un `QLabel` con el título "Bandeja de incidencias".
- Un `QListWidget` para mostrar las incidencias.
- Un `QLabel` en la parte inferior para indicar cuántas incidencias hay.

También añadimos cuatro incidencias de ejemplo para que se pudiera ver cómo quedaría la lista.

### 4. Crear el panel de detalles

En la parte derecha colocamos otro `QFrame` para mostrar la información de una incidencia.

Primero añadimos el título "Detalle de la incidencia" y dos botones: **Editar** y **Eliminar**.

Después fuimos colocando etiquetas (`QLabel`) para mostrar los diferentes datos:

- Nombre de la incidencia
- ID
- Motivo de la incidencia
- Estado
- Prioridad
- Fecha
- Categoría
- Responsable

Debajo de cada etiqueta pusimos otra con un valor de ejemplo.

### 5. Dar estilo a la interfaz

Una vez colocados todos los componentes, modificamos su apariencia utilizando la propiedad `styleSheet` de Qt Designer.

Pusimos el fondo general de color azul muy claro, los paneles de color blanco y los encabezados de color azul claro.

También ajustamos los bordes, los espacios y el tamaño de las letras para que todo quedara más ordenado.

### 6. Guardar el archivo .ui

Cuando terminamos el diseño, guardamos la ventana en el archivo `MainWindow.ui`.

Este archivo contiene todos los componentes y sus propiedades, por lo que podemos volver a abrirlo desde Qt Designer para modificar la pantalla.

## Resultado

Al terminar tenemos la pantalla principal del gestor de incidencias, con una lista a la izquierda y los detalles de una incidencia a la derecha.

De momento solamente hemos hecho la parte visual. Los botones aparecen en la ventana, pero todavía no tienen ninguna funcionalidad programada.
