#include <iostream>
using namespace std;
#include "nodo.h"
#include <fstream>
#include <sstream>
#include <exception>
#include <cstddef>

using namespace std;

void mostrarHistorial(NodoPartida* head) {
    NodoPartida* actual = head;

    cout << "\nHistorial de partidas:\n";

    while (actual != nullptr) {
        cout << "Partida " << actual->datos.id_partida << ": "
             << actual->datos.j1 << " "
             << actual->datos.puntaje1 << " - "
             << actual->datos.j2 << " "
             << actual->datos.puntaje2 << "\n";

        actual = actual->siguiente;
    }
}

NodoJugador* buscarJugador(NodoJugador* head, string nombre) {
    NodoJugador* actual = head;

    while (actual != nullptr) {
        if (actual->datos.jugador == nombre) {
            return actual;
        }

        actual = actual->siguiente;
    }

    return nullptr;
}

void actualizarJugador(NodoJugador*& head,
                       string nombre,
                       int puntos,
                       bool gano) {
    NodoJugador* jugador = buscarJugador(head, nombre);

    if (jugador == nullptr) {
        jugador = new NodoJugador{};
        jugador->datos.jugador = nombre;

        jugador->siguiente = head;
        head = jugador;
    }

    jugador->datos.partidas++;
    jugador->datos.puntos_totales += puntos;

    if (gano) {
        jugador->datos.victorias++;
    }
}

bool vaAntes(const Jugador& a, const Jugador& b) {
    if (a.victorias != b.victorias) {
        return a.victorias > b.victorias;
    }

    if (a.puntos_totales != b.puntos_totales) {
        return a.puntos_totales > b.puntos_totales;
    }

    return a.jugador < b.jugador;
}

void ordenarRanking(NodoJugador*& head) {
    NodoJugador* ordenada = nullptr;

    while (head != nullptr) {
        NodoJugador* nodo = head;
        head = head->siguiente;

        if (ordenada == nullptr ||
            vaAntes(nodo->datos, ordenada->datos)) {

            nodo->siguiente = ordenada;
            ordenada = nodo;
            }
        else {
            NodoJugador* actual = ordenada;

            while (actual->siguiente != nullptr &&
                   !vaAntes(nodo->datos,
                            actual->siguiente->datos)) {

                actual = actual->siguiente;
                            }

            nodo->siguiente = actual->siguiente;
            actual->siguiente = nodo;
        }
    }

    head = ordenada;
}
void leerArchivo() {
    ifstream archivo("data/historial.csv");

    if (!archivo.is_open()) {
        cout << "No se pudo abrir el archivo\n";
        return;
    }

    string linea;

    // Saltar el encabezado
    getline(archivo, linea);

    NodoPartida* historial = nullptr;
    NodoPartida* ultimo = nullptr;

    while (getline(archivo, linea)) {
        stringstream fila(linea);

        string id;
        string jugador1;
        string puntos1;
        string jugador2;
        string puntos2;
        string ganador;
        string fecha;

        getline(fila, id, ',');
        getline(fila, jugador1, ',');
        getline(fila, puntos1, ',');
        getline(fila, jugador2, ',');
        getline(fila, puntos2, ',');
        getline(fila, ganador, ',');
        getline(fila, fecha);

        // Comprobar que todos los campos tengan datos
        if (id.empty() || jugador1.empty() || puntos1.empty() ||
            jugador2.empty() || puntos2.empty() ||
            ganador.empty() || fecha.empty()) {
            cout << "Se omitio una fila con campos vacios\n";
            continue;
        }

        Partida partidaLeida{};

        // Convertir los campos numericos
        try {
            size_t posicionId = 0;
            size_t posicionPuntos1 = 0;
            size_t posicionPuntos2 = 0;

            partidaLeida.id_partida = stoi(id, &posicionId);
            partidaLeida.puntaje1 = stoi(puntos1, &posicionPuntos1);
            partidaLeida.puntaje2 = stoi(puntos2, &posicionPuntos2);

            if (posicionId != id.size() ||
                posicionPuntos1 != puntos1.size() ||
                posicionPuntos2 != puntos2.size()) {

                cout << "Se omitio una fila con un campo numerico incorrecto\n";
                continue;
                }
        }
        catch (const exception&) {
            cout << "Se omitio una fila por un error numerico\n";
            continue;
        }

        partidaLeida.j1 = jugador1;
        partidaLeida.j2 = jugador2;
        partidaLeida.ganador = ganador;
        partidaLeida.fecha = fecha;

        // Comprobar los rangos permitidos
        if (partidaLeida.id_partida <= 0 ||
            partidaLeida.puntaje1 < 0 ||
            partidaLeida.puntaje1 > 192 ||
            partidaLeida.puntaje2 < 0 ||
            partidaLeida.puntaje2 > 192 ||
            partidaLeida.puntaje1 + partidaLeida.puntaje2 > 192) {
            cout << "Se omitio una fila con valores fuera de rango\n";
            continue;
        }

        // Calcular quien deberia haber ganado
        string ganadorEsperado;

        if (partidaLeida.puntaje1 > partidaLeida.puntaje2) {
            ganadorEsperado = partidaLeida.j1;
        }
        else if (partidaLeida.puntaje2 > partidaLeida.puntaje1) {
            ganadorEsperado = partidaLeida.j2;
        }
        else {
            ganadorEsperado = "EMPATE";
        }

        // Comparar con el ganador escrito en el CSV
        if (partidaLeida.ganador != ganadorEsperado) {
            cout << "Se omitio la partida "
                 << partidaLeida.id_partida
                 << ": ganador incorrecto\n";
            continue;
        }

        // Crear y conectar el nodo de la partida
        NodoPartida* nuevo = new NodoPartida{};
        nuevo->datos = partidaLeida;

        if (historial == nullptr) {
            historial = nuevo;
        }
        else {
            ultimo->siguiente = nuevo;
        }

        ultimo = nuevo;
    }

    if (historial == nullptr) {
        cout << "Todavia no hay partidas validas\n";
        return;
    }

    mostrarHistorial(historial);

    // Crear la lista de jugadores a partir del historial
    NodoJugador* jugadores = nullptr;
    NodoPartida* partidaActual = historial;

    while (partidaActual != nullptr) {
        actualizarJugador(
            jugadores,
            partidaActual->datos.j1,
            partidaActual->datos.puntaje1,
            partidaActual->datos.ganador == partidaActual->datos.j1
        );

        actualizarJugador(
            jugadores,
            partidaActual->datos.j2,
            partidaActual->datos.puntaje2,
            partidaActual->datos.ganador == partidaActual->datos.j2
        );

        partidaActual = partidaActual->siguiente;
    }

    ordenarRanking(jugadores);

    cout << "\nRanking:\n";

    while (jugadores != nullptr) {
        cout << jugadores->datos.jugador
             << " | Partidas: " << jugadores->datos.partidas
             << " | Victorias: " << jugadores->datos.victorias
             << " | Puntos: " << jugadores->datos.puntos_totales
             << "\n";

        NodoJugador* borrar = jugadores;
        jugadores = jugadores->siguiente;
        delete borrar;
    }

    // Liberar los nodos de partidas
    while (historial != nullptr) {
        NodoPartida* borrar = historial;
        historial = historial->siguiente;
        delete borrar;
    }
}
