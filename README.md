## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta los términos a continuación:

MIT License

Copyright (c) 2026 dmvall3, teyo15, raul

# Color Battle — Proyecto Integrador de Programación

## Descripción del proyecto

Color Battle es un juego para dos jugadores desarrollado en Python con Pygame e integrado con un módulo de procesamiento de datos en C++.

Los jugadores, identificados con los colores Rojo y Azul, compiten por pintar las casillas habilitadas del tablero durante un tiempo determinado. Al finalizar cada partida, Python guarda los resultados en un archivo CSV y ejecuta el programa de C++, que procesa el historial y muestra un ranking acumulado.

El proyecto aplica conceptos de programación modular, matrices, movimiento mediante vectores, manejo de archivos, listas enlazadas, punteros y algoritmos de ordenamiento.

## Integrantes

**Equipo 3**

- Matías Valle
- Raúl Granada
- Mateo Sánchez

## Funcionamiento del juego

- El tablero se representa mediante una matriz de 12 filas y 16 columnas.
- Cada jugador controla un personaje que gira cuando su tecla está libre y avanza cuando la mantiene presionada.
- Los personajes pueden pintar las casillas habilitadas y cambiar la propiedad de las casillas del rival.
- El juego contempla límites del tablero y colisiones entre jugadores y con obstáculos.
- En la configuración actual, cada partida dura 30 segundos.
- Al terminar, gana quien tenga más casillas pintadas. Si ambos tienen el mismo puntaje, se registra un empate.
- El botón **PLAY AGAIN** permite iniciar otra partida conservando el historial anterior.

### Controles

| Jugador | Tecla para avanzar |
|---|---|
| Rojo | Barra espaciadora |
| Azul | Enter |

## Tecnologías utilizadas

- **Python:** lógica del juego, registro de resultados e integración con C++.
- **Pygame 2.6.1:** ventana, gráficos, eventos de teclado y temporización.
- **C++20:** lectura del historial y generación del ranking.
- **CSV:** intercambio de información entre los dos programas.
- **CMake:** configuración y compilación del módulo de C++.
- **CLion y MinGW:** entorno de desarrollo y compilación utilizado en Windows.
- **Git y GitHub:** control de versiones y alojamiento del repositorio.

## Arquitectura e integración

El sistema está compuesto por dos programas que comparten el archivo `data/historial.csv`.

### Módulo Python

Se encarga de:

- Gestionar la ventana y los eventos del juego.
- Actualizar el movimiento de los jugadores.
- Resolver colisiones.
- Registrar la propiedad de las casillas.
- Controlar el tiempo y calcular los puntajes.
- Añadir una fila al CSV al terminar cada partida.
- Ejecutar el programa compilado de C++ para consultar el ranking actualizado.

### Módulo C++

Se encarga de:

- Leer las partidas del CSV.
- Comprobar campos vacíos, conversiones numéricas, rangos de puntaje y coherencia del ganador.
- Omitir los registros que no superen esas validaciones.
- Guardar las partidas válidas en una lista enlazada.
- Construir otra lista enlazada con los resultados acumulados de cada jugador.
- Ordenar a los jugadores mediante el algoritmo de inserción.
- Mostrar el historial y el ranking en la terminal.
- Liberar la memoria reservada para los nodos.

## Estructura del proyecto

| Ruta | Contenido |
|---|---|
| `python_juego/main.py` | Juego en Pygame, guardado del CSV y llamada al ejecutable de C++. |
| `cpp_datos/main.cpp` | Punto de entrada del programa de C++. |
| `cpp_datos/ranking.cpp` | Lectura, validación, listas enlazadas, acumulación y ordenamiento. |
| `cpp_datos/nodo.h` | Estructuras de partidas, jugadores y nodos. |
| `data/historial.csv` | Historial compartido entre Python y C++. |
| `CMakeLists.txt` | Configuración de compilación del módulo C++. |
| `requirements.txt` | Dependencias externas de Python. |
| `.gitignore` | Reglas para excluir archivos temporales y de compilación. |
| `README.md` | Documentación del proyecto. |
| `LICENSE` | Texto de la licencia del código del proyecto. |

Los ejecutables y la carpeta `cmake-build-debug` se generan localmente y no se incluyen en el repositorio.

## Formato del historial

Cada fila representa una partida terminada y contiene siete campos:

```csv
id_partida,jugador1,puntaje1,jugador2,puntaje2,ganador,fecha
1,Rojo,30,Azul,9,Rojo,2026-11-18
```

- `id_partida`: identificador de la partida.
- `jugador1` y `jugador2`: identificadores de los jugadores.
- `puntaje1` y `puntaje2`: cantidad de casillas pintadas por cada jugador.
- `ganador`: identificador del vencedor o `EMPATE`.
- `fecha`: fecha de finalización de la partida.

Python añade los resultados sin borrar las partidas anteriores y calcula el siguiente identificador a partir del historial existente.

## Criterios del ranking

Cada jugador aparece una sola vez, con estos datos acumulados:

- Partidas jugadas.
- Victorias.
- Puntos totales.

El ranking se ordena siguiendo estos criterios:

1. Mayor cantidad de victorias.
2. Mayor cantidad de puntos acumulados, si hay empate en victorias.
3. Orden por identificador del jugador, si los dos valores anteriores coinciden.

En una partida empatada, ambos jugadores acumulan sus puntos y una partida jugada, pero ninguno suma una victoria.

## Requisitos de ejecución

El entorno utilizado durante el desarrollo fue Windows con:

- Python 3.13.
- Pygame 2.6.1.
- Compilador de C++ compatible con C++20.
- CMake 4.3 o superior, según la configuración del proyecto.
- CLion con MinGW para compilar el programa de C++.

## Instalación y ejecución

Las instrucciones siguientes se ejecutan desde la carpeta principal del proyecto.

### 1. Instalar las dependencias de Python

```powershell
py -m pip install -r requirements.txt
```

### 2. Compilar el módulo de C++

1. Abrir la carpeta principal del proyecto en CLion.
2. Cargar o recargar `CMakeLists.txt`.
3. Seleccionar la configuración Debug.
4. Compilar el objetivo `Proyecto_integrador`.

La integración de Python espera encontrar el ejecutable en:

```text
cmake-build-debug/Proyecto_integrador.exe
```

Para ejecutar C++ directamente desde CLion, el directorio de trabajo debe ser la carpeta principal del proyecto, donde está la carpeta `data`.

### 3. Revisar la ubicación de MinGW

La función `ejecutar_ranking()` de Python utiliza la variable `carpeta_mingw` para localizar las DLL del compilador.

Esta ruta debe ajustarse a la instalación de MinGW del equipo donde se ejecutará el proyecto. También debe revisarse la ruta del ejecutable si se utiliza una carpeta de compilación diferente.

### 4. Iniciar el juego

```powershell
py python_juego/main.py
```

Al finalizar una partida:

1. Se añade el resultado a `data/historial.csv`.
2. Python ejecuta el módulo de C++.
3. El historial y el ranking actualizado aparecen en la misma terminal desde la que se inició el juego.

El ranking se presenta en la terminal; el resultado de la partida se muestra también en la ventana del juego.

## Código fuente

El código del juego se encuentra en `python_juego` y el módulo de procesamiento de resultados en `cpp_datos`.

El repositorio permite consultar los archivos fuente y los cambios registrados durante el desarrollo mediante Git.

## Video explicativo

**Enlace:** https://drive.google.com/file/d/1ULVloo8ZfUTmkujW6ZYSCxwrXdnmRnOs/view?usp=sharing

El video debe mostrar el funcionamiento del juego, el registro de una partida en el CSV y la generación del ranking mediante C++.

## Declaración de autoría

El presente proyecto fue desarrollado por los integrantes del Equipo 3 como parte de sus actividades académicas.

Se reconocen las bibliotecas, herramientas y apoyos externos utilizados durante su elaboración. El equipo asume la responsabilidad de revisar, comprender y validar el código y la documentación presentados.

## Uso de inteligencia artificial

Durante el desarrollo se utilizó **ChatGPT, de OpenAI**, como herramienta de apoyo para:

- Explicar conceptos de C++, estructuras, punteros y listas enlazadas.
- Guiar la construcción del módulo de historial y ranking.
- Generar y adaptar fragmentos de código en Python y C++.
- Apoyar la implementación del ordenamiento por inserción.
- Identificar y corregir errores de compilación e integración.
- Ajustar las rutas del CSV y del ejecutable.
- Orientar la configuración de CMake y la ejecución con las DLL de MinGW.
- Apoyar la organización del repositorio y la elaboración de documentación.

La asistencia de inteligencia artificial forma parte del proceso documentado de desarrollo. Su uso no sustituye la responsabilidad académica del equipo sobre el contenido entregado.

**Herramienta:** [ChatGPT — OpenAI](https://chatgpt.com/).

## Créditos y referencias

### Python y biblioteca estándar

Se utilizan módulos de la biblioteca estándar de Python, entre ellos `csv`, `math`, `datetime`, `pathlib`, `subprocess`, `sys` y `os`.

- Responsable: Python Software Foundation y colaboradores.
- Documentación: https://docs.python.org/3/
- Información de licencias: https://docs.python.org/3/license.html

### Pygame

Se utiliza Pygame para gestionar la ventana, los gráficos, las entradas del teclado y el tiempo del juego.

- Autores: comunidad y colaboradores de Pygame.
- Versión utilizada: 2.6.1.
- Licencia: GNU LGPL 2.1.
- Documentación: https://www.pygame.org/docs/
- Código fuente y licencia: https://github.com/pygame/pygame

### Herramientas de desarrollo

- CMake: https://cmake.org/
- CLion, de JetBrains: https://www.jetbrains.com/clion/
- Git: https://git-scm.com/
- GitHub: https://github.com/

### Recursos visuales

En la versión descrita, el tablero, los jugadores, los obstáculos y los botones se representan mediante figuras geométricas dibujadas con Pygame. No se incorporan archivos externos de imágenes o audio.

Cualquier recurso o fragmento de terceros añadido posteriormente deberá registrarse en esta sección con su autor, procedencia y licencia.

## Licencia

El código propio del proyecto se distribuye bajo la **licencia MIT**. Su texto completo debe incluirse en el archivo `LICENSE` de la carpeta principal.

Las bibliotecas y herramientas de terceros conservan sus respectivas licencias. La licencia MIT del proyecto no reemplaza las licencias de sus dependencias.

## Finalidad académica

Proyecto elaborado con fines educativos para aplicar conocimientos de programación, estructuras de datos e integración entre lenguajes como parte de la formación universitaria.