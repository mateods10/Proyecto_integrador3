# ===== IMPORTACIONES =====
import csv
import math
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
import random
import pygame


# ===== CONFIGURACION DEL JUEGO =====
pygame.init()

# Ventana y fuentes
pygame.display.set_caption("Color Battle")
screen = pygame.display.set_mode((1040, 880))
clock = pygame.time.Clock()
fuente = pygame.font.SysFont("Arial", 32)
fuenteG = pygame.font.SysFont("Arial", 100)
texto_ganador = fuenteG.render("", True, (255, 255, 255))

# Tablero y margenes
celdas = 60
filas = 12
columnas = 16
margen = 40
altura_hud = 120
origen_x = margen
origen_y = altura_hud

# Colores
fondo = (35, 40, 50)
grid = (90, 95, 105)
color_obstaculo = (35, 200, 50)

# Posiciones iniciales: Rojo y Azul
jugador1_x = 30
jugador1_y = 30
jugador1_angulo = 0
jugador2_x = 930
jugador2_y = 690
jugador2_angulo = 180

radio = 25
rojo = (255, 60, 60)
azul = (60, 120, 255)
celda_rojo = (255, 100, 100)
celda_azul = (100, 150, 255)

# Movimiento y duracion
velocidad = 400
velocidad_giro1 = 300
velocidad_giro2 = 300
duracion = 30
tiempo_restante = duracion
terminado = False

# Botones de la pantalla final
boton_reiniciar = pygame.Rect(370, 540, 300, 70)
boton_score = pygame.Rect(370, 630, 300, 70)
mostrando_score = False
datos_score =[]
error_score = ""

boton_volver =  pygame.Rect(370, 670, 300, 60)
fuente_score = pygame.font.SysFont("Arial",26)
# ===== MAPA Y OBSTACULOS =====

# ===== GENERAR MAPA ALEATORIO =====
def generar_mapa():
    nuevo_mapa = []

    for fila in range(filas):
        nueva_fila = ""

        for columna in range(columnas):
            celda = random.choice(["0", "1"])
            nueva_fila += celda

        nuevo_mapa.append(nueva_fila)

    # Las posiciones iniciales siempre se pueden pintar.
    nuevo_mapa[0] = "1" + nuevo_mapa[0][1:]
    nuevo_mapa[-1] = nuevo_mapa[-1][:-1] + "1"

    return nuevo_mapa
# Casillas: 0 = no pintable, 1 = libre, 2 = Rojo, 3 = Azul.
mapa = generar_mapa()

# ===== GENERAR OBSTACULOS ALEATORIOS =====
def generar_obstaculos():
    formas = [
        [(0, 0), (150, 0), (150, 150), (0, 150)],
        [(50, 0), (200, 150), (0, 150)],
        [(20, 30), (120, 0), (180, 80), (100, 160), (0, 120)]
    ]

    random.shuffle(formas)

    # Cada obstaculo ocupa una zona diferente del tablero.
    zonas = [
        (100, 120, 300, 220),
        (540, 100, 300, 240),
        (260, 440, 450, 230)
    ]

    nuevos_obstaculos = []

    for forma, (zx, zy, ancho, alto) in zip(formas, zonas):
        ancho_forma = max(x for x, y in forma)
        alto_forma = max(y for x, y in forma)

        x = random.randint(zx, zx + ancho - ancho_forma)
        y = random.randint(zy, zy + alto - alto_forma)

        obstaculo = [
            (x + px, y + py)
            for px, py in forma
        ]

        nuevos_obstaculos.append(obstaculo)

    return nuevos_obstaculos

obstaculos = generar_obstaculos()

# Convertir el mapa de texto en una matriz de numeros
tablero = []
for fila in mapa:
    nueva_fila = []
    for celda in fila:
        nueva_fila.append(int(celda))
    tablero.append(nueva_fila)


# ===== COLISIONES ENTRE JUGADORES =====
def detectar_colision_jugadores(x1, y1, x2, y2, radio):
    dx = x2 - x1
    dy = y2 - y1
    distancia = math.hypot(dx, dy)

    if distancia < 2 * radio and distancia != 0:
        nx = dx / distancia
        ny = dy / distancia
        profundidad = 2 * radio - distancia
        return nx, ny, profundidad

    return None


def resolver_colision_jugadores(x1, y1, x2, y2, radio):
    colision = detectar_colision_jugadores(x1, y1, x2, y2, radio)

    if colision is not None:
        nx, ny, profundidad = colision
        correccion = profundidad / 2
        x1 -= nx * correccion
        y1 -= ny * correccion
        x2 += nx * correccion
        y2 += ny * correccion

    return x1, y1, x2, y2


# ===== COLISIONES CON OBSTACULOS =====
def detectar_colision_obstaculos(px1, py1, a, b, radio):
    ax, ay = a
    bx, by = b
    vx = bx - ax
    vy = by - ay
    x = px1 - ax
    y = py1 - ay

    t = (x * vx + y * vy) / (vx ** 2 + vy ** 2)
    t = max(0, min(1, t))
    cx = ax + t * vx
    cy = ay + t * vy

    dx = px1 - cx
    dy = py1 - cy
    distancia = math.hypot(dx, dy)

    if distancia < radio and distancia != 0:
        nx = dx / distancia
        ny = dy / distancia
        profundidad = radio - distancia
        return nx, ny, profundidad

    return None


def resolver_colision_obstaculos(px1, py1, a, b, radio):
    colision = detectar_colision_obstaculos(px1, py1, a, b, radio)

    if colision is not None:
        nx, ny, profundidad = colision
        px1 += nx * profundidad
        py1 += ny * profundidad

    return px1, py1


# ===== GUARDAR RESULTADOS EN CSV =====
def guardar_resultado(puntaje1, puntaje2):
    ruta = (
            Path(__file__).resolve().parent.parent / "data" / "historial.csv"
    )
    ruta.parent.mkdir(parents=True, exist_ok=True)

    encabezado = [
        "id_partida", "jugador1", "puntaje1", "jugador2",
        "puntaje2", "ganador", "fecha"
    ]

    if puntaje1 > puntaje2:
        ganador = "Rojo"
    elif puntaje2 > puntaje1:
        ganador = "Azul"
    else:
        ganador = "EMPATE"

    # Obtener el ultimo identificador registrado
    ultimo_id = 0
    if ruta.exists():
        with ruta.open("r", newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                try:
                    id_actual = int(fila["id_partida"])
                    ultimo_id = max(ultimo_id, id_actual)
                except (ValueError, KeyError, TypeError):
                    continue

    nuevo_id = ultimo_id + 1
    fecha = datetime.now().strftime("%Y-%m-%d")
    archivo_nuevo = not ruta.exists() or ruta.stat().st_size == 0

    # Agregar la partida sin borrar las anteriores
    with ruta.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        if archivo_nuevo:
            escritor.writerow(encabezado)
        escritor.writerow([
            nuevo_id, "Rojo", puntaje1, "Azul", puntaje2, ganador, fecha
        ])

    print(f"Partida {nuevo_id} guardada correctamente.")
    return nuevo_id


# ===== EJECUTAR RANKING DE C++ =====
def ejecutar_ranking():
    carpeta_proyecto = Path(__file__).resolve().parent.parent
    ejecutable = (
            carpeta_proyecto / "cmake-build-debug" / "Proyecto_integrador.exe"
    )
    carpeta_mingw = Path(
        r"C:\Program Files\JetBrains\CLion 2026.2.2\bin\mingw\bin"
    )

    if not ejecutable.is_file():
        print(f"No se encontro el ejecutable: {ejecutable}")
        print("Compila primero Proyecto_integrador en CLion.")
        return

    # Indicar donde estan las DLL de MinGW
    entorno = os.environ.copy()
    entorno["PATH"] = (
            str(carpeta_mingw) + os.pathsep + entorno.get("PATH", "")
    )

    try:
         resultado = subprocess.run(
            [str(ejecutable)],
            cwd=str(carpeta_proyecto),
            env=entorno,
            check=True,
            capture_output = True,
            text = True,
            errors = "replace"

        )
         print(resultado.stdout, end = "")
         return resultado.stdout
    except (OSError, subprocess.CalledProcessError) as error:
        print (f"No se pudo ejecutar el ranking: {error}")
        return None


# ===== EXTRAER DATOS DEL RANKING DE C++ =====

def extraer_ranking(salida):
     if salida is None:
         return[],"No se pudo ejecutar el ranking de C++"
     jugadores = []
     leyendo_ranking = False

     for linea in salida.splitlines():
         linea = linea.strip()

         if linea == "Ranking:":
             leyendo_ranking = True
             continue

         if not leyendo_ranking or not linea:
            continue

         partes = linea.split("|")

         if len(partes) != 4:
             return[], "El formato no es es el esperado"

         nombre = partes[0].strip()
         # Quitar una numeracion como "1. Rojo", si existe
         numero, separador, resto = nombre.partition (". ")
         if separador and numero.isdigit():
             nombre = resto

         try:
             partidas = int(partes[1].split(":", 1)[1].strip())
             victorias = int(partes[2].split(":", 1)[1].strip())
             puntos = int(partes[3].split(":", 1)[1].strip())
         except (ValueError, IndexError):
            return[], "No se pudieron interpretar los resultados"

         jugadores.append({
            "posicion": len(jugadores) + 1,
            "jugador": nombre,
            "partidas": partidas,
            "victorias": victorias,
            "puntos": puntos

         })
     if not jugadores:
         return[],"Todavia no hay resultados para mostrar"

     return jugadores, ""


# ===== CARGAR SCORE DESDE C++ =====
def abrir_score():
    salida = ejecutar_ranking()
    return extraer_ranking(salida)
# ===== DIBUJAR PANTALLA SCORE =====
def dibujar_score():
    screen.fill(fondo)

    # Fondo del panel
    pygame.draw.rect(
        screen,
        (45, 50, 65),
        (80, 120, 880, 640),
        border_radius=20
    )

    # Titulo
    titulo = fuente.render("SCORE GENERAL", True, (255, 255, 255))
    screen.blit(titulo, titulo.get_rect(center=(520, 180)))

    if error_score:
        mensaje = fuente_score.render(
            error_score, True, (255, 180, 120)
        )
        screen.blit(mensaje, mensaje.get_rect(center=(520, 360)))

    else:
        # Posiciones horizontales de las cinco columnas
        columnas_x = (115, 235, 440, 600, 790)
        encabezados = (
            "Puesto", "Jugador", "Partidas", "Victorias", "Puntos"
        )

        for x, encabezado in zip(columnas_x, encabezados):
            texto = fuente_score.render(
                encabezado, True, (170, 195, 255)
            )
            screen.blit(texto, (x, 280))

        # Una fila por jugador
        for i, jugador in enumerate(datos_score):
            y = 340 + i * 55

            valores = (
                jugador["posicion"],
                jugador["jugador"],
                jugador["partidas"],
                jugador["victorias"],
                jugador["puntos"]
            )

            for x, valor in zip(columnas_x, valores):
                texto = fuente_score.render(
                    str(valor), True, (255, 255, 255)
                )
                screen.blit(texto, (x, y))

    # Boton para regresar
    pygame.draw.rect(
        screen, (40, 30, 100), boton_volver, border_radius=15
    )

    texto_volver = fuente.render("VOLVER", True, (255, 255, 255))
    screen.blit(
        texto_volver,
        texto_volver.get_rect(center=boton_volver.center)
    )
# ===== BUCLE PRINCIPAL =====
while True:

    # EVENTOS: cerrar ventana, soltar teclas y pulsar botones
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            # Controles exclusivos de la pantalla SCORE
        if mostrando_score:
            if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                mostrando_score = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if boton_volver.collidepoint(event.pos):
                       mostrando_score = False

            continue

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                velocidad_giro1 = -velocidad_giro1
            if event.key == pygame.K_RETURN:
                velocidad_giro2 = -velocidad_giro2

        if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and terminado
                and boton_score.collidepoint(event.pos)
        ):
            datos_score, error_score = abrir_score()
            print("DATOS SCORE:", datos_score)
            print("ERROR SCORE:", repr(error_score))
            mostrando_score = True

        # REINICIAR PARTIDA
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and terminado:
                if boton_reiniciar.collidepoint(event.pos):
                    jugador1_x = 30
                    jugador1_y = 30
                    jugador1_angulo = 0
                    jugador2_x = 930
                    jugador2_y = 690
                    jugador2_angulo = 180
                    velocidad_giro1 = 300
                    velocidad_giro2 = 300
                    tiempo_restante = duracion
                    mapa = generar_mapa()
                    obstaculos = generar_obstaculos()
                    tablero = [
                        [int(celda) for celda in fila] for fila in mapa
                    ]
                    terminado = False

    # TIEMPO ENTRE ACTUALIZACIONES
    dt = clock.tick(60) / 1000

    if not terminado:
        tiempo_restante -= dt
        tecla = pygame.key.get_pressed()

        # MOVIMIENTO DEL JUGADOR ROJO
        anterior1_x = jugador1_x
        anterior1_y = jugador1_y
        if tecla[pygame.K_SPACE]:
            vx1 = math.cos(math.radians(jugador1_angulo)) * velocidad
            vy1 = math.sin(math.radians(jugador1_angulo)) * velocidad
            jugador1_x += vx1 * dt
            jugador1_y += vy1 * dt
        else:
            jugador1_angulo = (
                                      jugador1_angulo + velocidad_giro1 * dt
                              ) % 360

        # MOVIMIENTO DEL JUGADOR AZUL
        anterior2_x = jugador2_x
        anterior2_y = jugador2_y
        if tecla[pygame.K_RETURN]:
            vx2 = math.cos(math.radians(jugador2_angulo)) * velocidad
            vy2 = math.sin(math.radians(jugador2_angulo)) * velocidad
            jugador2_x += vx2 * dt
            jugador2_y += vy2 * dt
        else:
            jugador2_angulo = (
                                      jugador2_angulo + velocidad_giro2 * dt
                              ) % 360

        # APLICAR COLISIONES
        jugador1_x, jugador1_y, jugador2_x, jugador2_y = (
            resolver_colision_jugadores(
                jugador1_x, jugador1_y, jugador2_x, jugador2_y, radio
            )
        )

        for obstaculo in obstaculos:
            for i in range(len(obstaculo)):
                a = obstaculo[i]
                b = obstaculo[(i + 1) % len(obstaculo)]
                jugador1_x, jugador1_y = resolver_colision_obstaculos(
                    jugador1_x, jugador1_y, a, b, radio
                )
                jugador2_x, jugador2_y = resolver_colision_obstaculos(
                    jugador2_x, jugador2_y, a, b, radio
                )

        # LIMITES DEL TABLERO
        jugador1_x = max(radio, min(jugador1_x, 960 - radio))
        jugador1_y = max(radio, min(jugador1_y, 720 - radio))
        jugador2_x = max(radio, min(jugador2_x, 960 - radio))
        jugador2_y = max(radio, min(jugador2_y, 720 - radio))

        # PINTAR CASILLAS
        columna1 = int(jugador1_x // celdas)
        fila1 = int(jugador1_y // celdas)
        if tablero[fila1][columna1] != 0:
            tablero[fila1][columna1] = 2

        columna2 = int(jugador2_x // celdas)
        fila2 = int(jugador2_y // celdas)
        if tablero[fila2][columna2] != 0:
            tablero[fila2][columna2] = 3

        # FINALIZAR PARTIDA: contar, guardar y ejecutar C++
        if tiempo_restante <= 0:
            tiempo_restante = 0
            terminado = True
            puntaje1_final = sum(
                celda == 2 for fila in tablero for celda in fila
            )
            puntaje2_final = sum(
                celda == 3 for fila in tablero for celda in fila
            )
            guardar_resultado(puntaje1_final, puntaje2_final)
            ejecutar_ranking()

    # ===== DIBUJADO DE LA PANTALLA =====
    screen.fill(fondo)

    # TABLERO Y CONTEO DE PUNTOS
    puntaje1 = 0
    puntaje2 = 0
    for row in range(filas):
        for col in range(columnas):
            x = col * celdas + origen_x
            y = row * celdas + origen_y

            if tablero[row][col] == 0:
                color = fondo
            elif tablero[row][col] == 1:
                color = grid
            elif tablero[row][col] == 2:
                color = celda_rojo
                puntaje1 += 1
            elif tablero[row][col] == 3:
                color = celda_azul
                puntaje2 += 1

            pygame.draw.rect(screen, color, (x, y, celdas, celdas))

    pygame.draw.rect(
        screen, grid,
        (origen_x, origen_y, columnas * celdas, filas * celdas),
        3
    )

    # MARCADORES
    texto = fuente.render(f"Rojo: {puntaje1}", True, grid)
    screen.blit(texto, (20, 20))
    texto = fuente.render(f"Azul: {puntaje2}", True, grid)
    screen.blit(texto, (400, 20))

    # OBSTACULOS
    for obstaculo in obstaculos:
        puntos_pantalla = []
        for x, y in obstaculo:
            puntos_pantalla.append((x + origen_x, y + origen_y))
        pygame.draw.polygon(screen, color_obstaculo, puntos_pantalla)

    # JUGADORES Y DIRECCIONES
    pygame.draw.circle(
        screen, rojo,
        (jugador1_x + origen_x, jugador1_y + origen_y), radio
    )
    pygame.draw.circle(
        screen, azul,
        (jugador2_x + origen_x, jugador2_y + origen_y), radio
    )

    punta1_x = jugador1_x + math.cos(math.radians(jugador1_angulo)) * 30
    punta1_y = jugador1_y + math.sin(math.radians(jugador1_angulo)) * 30
    pygame.draw.line(
        screen, (255, 255, 255),
        (jugador1_x + origen_x, jugador1_y + origen_y),
        (punta1_x + origen_x, punta1_y + origen_y), 4
    )

    punta2_x = jugador2_x + math.cos(math.radians(jugador2_angulo)) * 30
    punta2_y = jugador2_y + math.sin(math.radians(jugador2_angulo)) * 30
    pygame.draw.line(
        screen, (255, 255, 255),
        (jugador2_x + origen_x, jugador2_y + origen_y),
        (punta2_x + origen_x, punta2_y + origen_y), 4
    )

    # TIEMPO RESTANTE
    texto_tiempo = fuente.render(
        f"Tiempo: {math.ceil(tiempo_restante)}", True, grid
    )
    screen.blit(texto_tiempo, (540, 20))

    # PANTALLA FINAL: ganador y botones
    if terminado:
        if puntaje1 > puntaje2:
            texto_ganador = fuenteG.render(
                "Ganador: Rojo", True, (255, 255, 255)
            )
        elif puntaje2 > puntaje1:
            texto_ganador = fuenteG.render(
                "Ganador: Azul", True, (255, 255, 255)
            )
        else:
            texto_ganador = fuenteG.render(
                "Empate", True, (255, 255, 255)
            )

        rect_texto = texto_ganador.get_rect(center=(520, 440))
        screen.blit(texto_ganador, rect_texto)

        # Boton PLAY AGAIN
        pygame.draw.rect(
            screen, (40, 30, 100), boton_reiniciar, border_radius=15
        )
        texto_boton = fuente.render("PLAY AGAIN", True, (255, 255, 255))
        screen.blit(
            texto_boton,
            texto_boton.get_rect(center=boton_reiniciar.center)
        )

        # Boton SCORE
        pygame.draw.rect(
            screen, (40, 30, 100), boton_score, border_radius=15
        )
        texto_score = fuente.render("SCORE", True, (255, 255, 255))
        screen.blit(
            texto_score,
            texto_score.get_rect(center=boton_score.center)
        )
        if mostrando_score:
            dibujar_score()

    pygame.display.update()


    pygame.display.update()
