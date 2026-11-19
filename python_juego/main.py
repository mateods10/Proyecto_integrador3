import sys
import pygame
import math
import csv
import subprocess
from datetime import datetime
from pathlib import Path
import os

pygame.init()

pygame.display.set_caption("Color Battle")
screen = pygame.display.set_mode((1040, 880))
clock = pygame.time.Clock()

fuente = pygame.font.SysFont("Arial", 32)
fuenteG = pygame.font.SysFont("Arial", 100)
texto_ganador = fuenteG.render("", True, (255, 255, 255))

# Configuracion del tablero
celdas = 60
filas = 12
columnas = 16
margen = 40
altura_hud = 120

origen_x = margen
origen_y = altura_hud

fondo = (35, 40, 50)
grid = (90, 95, 105)
color_obstaculo = (35, 200, 50)

# Jugador 1: Rojo
jugador1_x = 30
jugador1_y = 30
jugador1_angulo = 0

# Jugador 2: Azul
jugador2_x = 930
jugador2_y = 690
jugador2_angulo = 180

# Configuracion de jugadores
radio = 25
rojo = (255, 60, 60)
azul = (60, 120, 255)
celda_rojo = (255, 100, 100)
celda_azul = (100, 150, 255)

# Configuracion del movimiento
velocidad = 400
velocidad_giro1 = 300
velocidad_giro2 = 300

# Tiempo
duracion = 30
tiempo_restante = duracion
terminado = False

boton_reiniciar = pygame.Rect(370, 540, 300, 70)

# Tablero de 12 filas y 16 columnas
mapa = [
    "0000000000000000",
    "0011111111110000",
    "0011100000110110",
    "0011100000000110",
    "0000000000000000",
    "0000000000000000",
    "0001100000000000",
    "0001100000111100",
    "0000000000111100",
    "0110000111111100",
    "0110000111111100",
    "0000000000000000"
]

tablero = []

for fila in mapa:
    nueva_fila = []

    for celda in fila:
        nueva_fila.append(int(celda))

    tablero.append(nueva_fila)


# Colision entre jugadores
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
    colision = detectar_colision_jugadores(
        x1, y1, x2, y2, radio
    )

    if colision is not None:
        nx, ny, profundidad = colision
        correccion = profundidad / 2

        x1 -= nx * correccion
        y1 -= ny * correccion

        x2 += nx * correccion
        y2 += ny * correccion

    return x1, y1, x2, y2


# Obstaculos
obstaculos = [
    [
        (350, 250),
        (500, 250),
        (500, 400),
        (350, 400)
    ],
    [
        (650, 200),
        (800, 350),
        (600, 350)
    ],
    [
        (200, 500),
        (300, 470),
        (360, 550),
        (280, 630),
        (180, 590)
    ]
]


# Colision con obstaculos
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
    colision = detectar_colision_obstaculos(
        px1, py1, a, b, radio
    )

    if colision is not None:
        nx, ny, profundidad = colision

        px1 += nx * profundidad
        py1 += ny * profundidad

    return px1, py1


# Guardar el resultado en el CSV compartido con C++
def guardar_resultado(puntaje1, puntaje2):
    ruta = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "historial.csv"
    )

    ruta.parent.mkdir(parents=True, exist_ok=True)

    encabezado = [
        "id_partida",
        "jugador1",
        "puntaje1",
        "jugador2",
        "puntaje2",
        "ganador",
        "fecha"
    ]

    if puntaje1 > puntaje2:
        ganador = "Rojo"
    elif puntaje2 > puntaje1:
        ganador = "Azul"
    else:
        ganador = "EMPATE"

    ultimo_id = 0

    if ruta.exists():
        with ruta.open(
                "r",
                newline="",
                encoding="utf-8"
        ) as archivo:
            lector = csv.DictReader(archivo)

            for fila in lector:
                try:
                    id_actual = int(fila["id_partida"])
                    ultimo_id = max(ultimo_id, id_actual)
                except (ValueError, KeyError, TypeError):
                    continue

    nuevo_id = ultimo_id + 1

    fecha = datetime.now().strftime("%Y-%m-%d")

    archivo_nuevo = (
            not ruta.exists()
            or ruta.stat().st_size == 0
    )

    with ruta.open(
            "a",
            newline="",
            encoding="utf-8"
    ) as archivo:
        escritor = csv.writer(archivo)

        if archivo_nuevo:
            escritor.writerow(encabezado)

        escritor.writerow([
            nuevo_id,
            "Rojo",
            puntaje1,
            "Azul",
            puntaje2,
            ganador,
            fecha
        ])

    print(f"Partida {nuevo_id} guardada correctamente.")

    return nuevo_id


# Ejecutar el programa C++ despues de guardar la partida
def ejecutar_ranking():
    carpeta_proyecto = Path(__file__).resolve().parent.parent

    ejecutable = (
            carpeta_proyecto
            / "cmake-build-debug"
            / "Proyecto_integrador.exe"
    )

    carpeta_mingw = Path(
        r"C:\Program Files\JetBrains\CLion 2026.2.2\bin\mingw\bin"
    )

    if not ejecutable.is_file():
        print(f"No se encontro el ejecutable: {ejecutable}")
        print("Compila primero Proyecto_integrador en CLion.")
        return

    entorno = os.environ.copy()

    entorno["PATH"] = (
            str(carpeta_mingw)
            + os.pathsep
            + entorno.get("PATH", "")
    )

    try:
        subprocess.run(
            [str(ejecutable)],
            cwd=str(carpeta_proyecto),
            env=entorno,
            check=True
        )
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"No se pudo ejecutar el ranking: {error}")


# Bucle principal del juego
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                velocidad_giro1 = -velocidad_giro1

            if event.key == pygame.K_RETURN:
                velocidad_giro2 = -velocidad_giro2

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

                    tablero = [
                        [int(celda) for celda in fila]
                        for fila in mapa
                    ]

                    terminado = False

    dt = clock.tick(60) / 1000

    if not terminado:
        tiempo_restante -= dt

        tecla = pygame.key.get_pressed()

        # Movimiento del jugador 1
        anterior1_x = jugador1_x
        anterior1_y = jugador1_y

        if tecla[pygame.K_SPACE]:
            vx1 = (
                    math.cos(math.radians(jugador1_angulo))
                    * velocidad
            )
            vy1 = (
                    math.sin(math.radians(jugador1_angulo))
                    * velocidad
            )

            jugador1_x += vx1 * dt
            jugador1_y += vy1 * dt
        else:
            jugador1_angulo = (
                                      jugador1_angulo + velocidad_giro1 * dt
                              ) % 360

        # Movimiento del jugador 2
        anterior2_x = jugador2_x
        anterior2_y = jugador2_y

        if tecla[pygame.K_RETURN]:
            vx2 = (
                    math.cos(math.radians(jugador2_angulo))
                    * velocidad
            )
            vy2 = (
                    math.sin(math.radians(jugador2_angulo))
                    * velocidad
            )

            jugador2_x += vx2 * dt
            jugador2_y += vy2 * dt
        else:
            jugador2_angulo = (
                                      jugador2_angulo + velocidad_giro2 * dt
                              ) % 360

        # Colision entre jugadores
        (
            jugador1_x,
            jugador1_y,
            jugador2_x,
            jugador2_y
        ) = resolver_colision_jugadores(
            jugador1_x,
            jugador1_y,
            jugador2_x,
            jugador2_y,
            radio
        )

        # Colision con obstaculos
        for obstaculo in obstaculos:
            for i in range(len(obstaculo)):
                a = obstaculo[i]
                b = obstaculo[(i + 1) % len(obstaculo)]

                jugador1_x, jugador1_y = (
                    resolver_colision_obstaculos(
                        jugador1_x,
                        jugador1_y,
                        a,
                        b,
                        radio
                    )
                )

                jugador2_x, jugador2_y = (
                    resolver_colision_obstaculos(
                        jugador2_x,
                        jugador2_y,
                        a,
                        b,
                        radio
                    )
                )

        # Limites del tablero
        jugador1_x = max(
            radio,
            min(jugador1_x, 960 - radio)
        )
        jugador1_y = max(
            radio,
            min(jugador1_y, 720 - radio)
        )

        jugador2_x = max(
            radio,
            min(jugador2_x, 960 - radio)
        )
        jugador2_y = max(
            radio,
            min(jugador2_y, 720 - radio)
        )

        # Celda actual del jugador 1
        columna1 = int(jugador1_x // celdas)
        fila1 = int(jugador1_y // celdas)

        if tablero[fila1][columna1] != 0:
            tablero[fila1][columna1] = 2

        # Celda actual del jugador 2
        columna2 = int(jugador2_x // celdas)
        fila2 = int(jugador2_y // celdas)

        if tablero[fila2][columna2] != 0:
            tablero[fila2][columna2] = 3

        # Final de la partida
        if tiempo_restante <= 0:
            tiempo_restante = 0
            terminado = True

            puntaje1_final = sum(
                celda == 2
                for fila in tablero
                for celda in fila
            )

            puntaje2_final = sum(
                celda == 3
                for fila in tablero
                for celda in fila
            )

            guardar_resultado(
                puntaje1_final,
                puntaje2_final
            )

            ejecutar_ranking()

    screen.fill(fondo)

    # Dibujar tablero y contar puntos
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

            pygame.draw.rect(
                screen,
                color,
                (x, y, celdas, celdas)
            )

    # Dibujar borde del tablero
    pygame.draw.rect(
        screen,
        grid,
        (
            origen_x,
            origen_y,
            columnas * celdas,
            filas * celdas
        ),
        3
    )

    # Mostrar puntos
    texto = fuente.render(
        f"Rojo: {puntaje1}",
        True,
        grid
    )
    screen.blit(texto, (20, 20))

    texto = fuente.render(
        f"Azul: {puntaje2}",
        True,
        grid
    )
    screen.blit(texto, (400, 20))

    # Dibujar obstaculos
    for obstaculo in obstaculos:
        puntos_pantalla = []

        for x, y in obstaculo:
            puntos_pantalla.append(
                (x + origen_x, y + origen_y)
            )

        pygame.draw.polygon(
            screen,
            color_obstaculo,
            puntos_pantalla
        )

    # Dibujar jugadores
    pygame.draw.circle(
        screen,
        rojo,
        (
            jugador1_x + origen_x,
            jugador1_y + origen_y
        ),
        radio
    )

    pygame.draw.circle(
        screen,
        azul,
        (
            jugador2_x + origen_x,
            jugador2_y + origen_y
        ),
        radio
    )

    # Direccion del jugador 1
    punta1_x = (
            jugador1_x
            + math.cos(math.radians(jugador1_angulo)) * 30
    )
    punta1_y = (
            jugador1_y
            + math.sin(math.radians(jugador1_angulo)) * 30
    )

    pygame.draw.line(
        screen,
        (255, 255, 255),
        (
            jugador1_x + origen_x,
            jugador1_y + origen_y
        ),
        (
            punta1_x + origen_x,
            punta1_y + origen_y
        ),
        4
    )

    # Direccion del jugador 2
    punta2_x = (
            jugador2_x
            + math.cos(math.radians(jugador2_angulo)) * 30
    )
    punta2_y = (
            jugador2_y
            + math.sin(math.radians(jugador2_angulo)) * 30
    )

    pygame.draw.line(
        screen,
        (255, 255, 255),
        (
            jugador2_x + origen_x,
            jugador2_y + origen_y
        ),
        (
            punta2_x + origen_x,
            punta2_y + origen_y
        ),
        4
    )

    # Mostrar tiempo
    texto_tiempo = fuente.render(
        f"Tiempo: {math.ceil(tiempo_restante)}",
        True,
        grid
    )
    screen.blit(texto_tiempo, (540, 20))

    # Pantalla de resultados
    if terminado:
        if puntaje1 > puntaje2:
            texto_ganador = fuenteG.render(
                "Ganador: Rojo",
                True,
                (255, 255, 255)
            )
        elif puntaje2 > puntaje1:
            texto_ganador = fuenteG.render(
                "Ganador: Azul",
                True,
                (255, 255, 255)
            )
        else:
            texto_ganador = fuenteG.render(
                "Empate",
                True,
                (255, 255, 255)
            )

        rect_texto = texto_ganador.get_rect(
            center=(520, 440)
        )
        screen.blit(texto_ganador, rect_texto)

        # Boton para reiniciar
        pygame.draw.rect(
            screen,
            (40, 30, 100),
            boton_reiniciar,
            border_radius=15
        )

        texto_boton = fuente.render(
            "PLAY AGAIN",
            True,
            (255, 255, 255)
        )

        screen.blit(
            texto_boton,
            texto_boton.get_rect(
                center=boton_reiniciar.center
            )
        )

    pygame.display.update()