#ifndef NODO_H
#define NODO_H
using namespace std;
#include <string>

struct Partida {
    int id_partida;
    string j1;
    int puntaje1;
    string j2;
    int puntaje2;
    string ganador;
    string fecha;
};

struct NodoPartida {
    Partida datos;
    NodoPartida* siguiente = nullptr;
};

struct Jugador {
    string jugador;
    int partidas = 0;
    int victorias = 0;
    int puntos_totales = 0;
};

struct NodoJugador {
    Jugador datos;
    NodoJugador* siguiente = nullptr;
};


#endif