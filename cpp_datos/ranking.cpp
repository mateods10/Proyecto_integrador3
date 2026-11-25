#include <iostream>
// Permite abrir y leer archivos mediante ifstream.
#include <fstream>
#include <string>
// Permite leer por partes el texto de una linea.
#include <sstream>
#include <exception>
// Permite utilizar size_t para tamaños y posiciones.
#include <cstddef>
#include "nodo.h"
using namespace std;


// ============================================================
// MOSTRAR EL HISTORIAL
// Recibe un puntero al primer nodo de la lista de partidas.
// Recorre la lista y muestra los datos de cada partida.
// ============================================================
void mostrarHistorial(NodoPartida* head) {

    // Creamos un puntero auxiliar para recorrer la lista.
    // Empieza apuntando al mismo nodo que head.
    // Asi conservamos el puntero de inicio.
    NodoPartida* actual = head;

    cout << "\nHistorial de partidas:\n";

    // Mientras actual apunte a un nodo, seguimos recorriendo.
    // nullptr indica que ya no hay otro nodo.
    while (actual != nullptr) {

        // -> permite acceder a los campos del nodo
        // al que apunta actual.
        //
        // actual->datos contiene una estructura Partida.
        cout << "Partida " << actual->datos.id_partida << ": "
             << actual->datos.j1 << " "
             << actual->datos.puntaje1 << " - "
             << actual->datos.j2 << " "
             << actual->datos.puntaje2 << "\n";

        // Avanzamos al siguiente nodo. para no repetir la misma partida siempre
        actual = actual->siguiente;
    }
}


// ============================================================
// BUSCAR UN JUGADOR
// Recibe el inicio de la lista y el identificador buscado.
//
// Devuelve:
// - La direccion del nodo, si encuentra al jugador.
// - nullptr, si no lo encuentra.
// ============================================================
NodoJugador* buscarJugador(NodoJugador* head, string nombre) {

    // Empezamos a buscar desde el primer nodo.
    NodoJugador* actual = head;

    // Revisamos los nodos hasta llegar al final.
    while (actual != nullptr) {

        // == compara los textos.
        // Por ejemplo: "Rojo" == "Rojo" produce true.
        if (actual->datos.jugador == nombre) {

            // Encontramos al jugador.
            // Devolvemos su nodo y terminamos la funcion.
            return actual;
        }

        // Si no coincide, revisamos el siguiente nodo.
        actual = actual->siguiente;
    }

    // Llegamos al final sin encontrar al jugador.
    return nullptr;
}


// ============================================================
// CREAR O ACTUALIZAR UN JUGADOR
//
// Parametros:
// head: inicio de la lista de jugadores.
// nombre: identificador del jugador, como "Rojo".
// puntos: puntos obtenidos en una partida.
// gano: true si gano esa partida; false si no gano.
//
// NodoJugador*& significa que recibimos el puntero head
// por referencia. Podemos cambiar el inicio de la lista
// y ese cambio tambien se vera desde donde llamaron la funcion.
// ============================================================
void actualizarJugador(NodoJugador*& head,
                       string nombre,
                       int puntos,
                       bool gano) {

    // Buscamos si el jugador ya tiene un nodo en la lista.
    NodoJugador* jugador = buscarJugador(head, nombre);

    // Si no existe, debemos crearlo.
    if (jugador == nullptr) {

        // new reserva memoria para un nuevo nodo.
        // {} inicializa sus datos.
        jugador = new NodoJugador{};

        // Guardamos el identificador del jugador.
        jugador->datos.jugador = nombre;

        // Insertamos el nodo al principio de la lista:
        // primero lo conectamos con el inicio anterior.
        jugador->siguiente = head;

        // Ahora el nuevo nodo pasa a ser el primero.
        head = jugador;
    }

    // Tanto si el jugador ya existia como si acabamos
    // de crearlo, actualizamos sus resultados.

    // ++ suma una partida jugada.
    jugador->datos.partidas++;

    // += suma los puntos recibidos al total anterior.
    // Ejemplo: 30 puntos anteriores + 25 nuevos = 55.
    jugador->datos.puntos_totales += puntos;

    // bool puede valer true o false.
    // Sumamos una victoria solamente cuando gano es true.
    if (gano) {
        jugador->datos.victorias++;
    }
}


// ============================================================
// COMPARAR DOS JUGADORES PARA EL RANKING
//
// Devuelve true si a debe aparecer antes que b.
//
// Prioridad:
// 1. Mas victorias.
// 2. Mas puntos acumulados.
// 3. Orden por identificador.
//
// const Jugador& permite consultar cada jugador
// sin copiarlo ni modificarlo.
// ============================================================
bool vaAntes(const Jugador& a, const Jugador& b) {

    // Si las victorias son distintas, decide quien tiene mas.
    if (a.victorias != b.victorias) {
        return a.victorias > b.victorias;
    }

    // Si llegamos aqui, ambos tienen las mismas victorias.
    // Si sus puntos son distintos, decide quien tiene mas.
    if (a.puntos_totales != b.puntos_totales) {
        return a.puntos_totales > b.puntos_totales;
    }

    // Si tambien tienen los mismos puntos, comparamos el texto.
    // Por ejemplo, "Azul" va antes que "Rojo".
    return a.jugador < b.jugador;
}


// ============================================================
// ORDENAR LA LISTA MEDIANTE INSERCION
//
// Toma los nodos de la lista original, uno por uno,
// y los coloca en su posicion dentro de una lista ordenada.
//
// Reutiliza los mismos nodos: cambia sus enlaces.
// No necesita crear nodos nuevos ni borrar los existentes.
// ============================================================
void ordenarRanking(NodoJugador*& head) {

    // La lista ordenada empieza vacia.
    NodoJugador* ordenada = nullptr;

    // head apunta a los nodos pendientes de ordenar.
    while (head != nullptr) {

        // Guardamos el primer nodo pendiente.
        NodoJugador* nodo = head;

        // Avanzamos el inicio de los pendientes.
        // El nodo guardado se insertara en ordenada.
        head = head->siguiente;

        // Colocamos el nodo al inicio si:
        // - La lista ordenada esta vacia, O
        // - El jugador debe ir antes que el primero.
        //
        // || significa "o".
        // Si ordenada es nullptr, no se evalua la segunda parte.
        if (ordenada == nullptr ||
            vaAntes(nodo->datos, ordenada->datos)) {

            // Conectamos el nodo con el inicio anterior.
            nodo->siguiente = ordenada;

            // El nodo pasa a ser el nuevo inicio.
            ordenada = nodo;
        }
        else {

            // Debemos encontrar una posicion mas adelante.
            NodoJugador* actual = ordenada;

            // Avanzamos mientras:
            // - Exista un siguiente nodo, Y
            // - El nodo que insertamos no deba ir antes de el.
            //
            // && significa "y".
            // ! niega el resultado de vaAntes().
            //
            // La primera condicion evita acceder a datos
            // de un puntero que sea nullptr.
            while (actual->siguiente != nullptr &&
                   !vaAntes(nodo->datos,
                            actual->siguiente->datos)) {

                actual = actual->siguiente;
            }

            // Insertamos nodo despues de actual.
            //
            // Primero conservamos la conexion con lo que sigue.
            nodo->siguiente = actual->siguiente;

            // Despues conectamos actual con el nodo insertado.
            actual->siguiente = nodo;
        }
    }

    // Todos los nodos ya estan ordenados.
    // Actualizamos el inicio de la lista recibida.
    head = ordenada;
}


// ============================================================
// LEER EL CSV Y PROCESAR LOS RESULTADOS
//
// Esta funcion coordina todo el proceso:
// 1. Abrir el archivo.
// 2. Leer y validar las partidas.
// 3. Construir la lista de partidas.
// 4. Acumular resultados por jugador.
// 5. Ordenar y mostrar el ranking.
// 6. Liberar la memoria de las dos listas.
// ============================================================
void leerArchivo() {

    // Intentamos abrir el archivo para lectura.
    // Esta ruta se busca desde el directorio de trabajo
    // con el que se ejecuta el programa.
    ifstream archivo("data/historial.csv");

    // is_open() indica si el archivo se abrio.
    // ! significa "no".
    if (!archivo.is_open()) {

        cout << "No se pudo abrir el archivo\n";

        // Salimos de esta funcion porque no podemos leerlo.
        return;
    }

    // Guardara el texto de cada linea del CSV.
    string linea;

    // Leemos una vez antes del bucle para saltar el encabezado:
    // id_partida,jugador1,puntaje1,...
    // Esto supone que el CSV contiene ese encabezado.
    getline(archivo, linea);

    // Inicio de la lista de partidas.
    // nullptr indica que todavia esta vacia.
    NodoPartida* historial = nullptr;

    // Apuntara al ultimo nodo para agregar partidas al final.
    NodoPartida* ultimo = nullptr;

    // Leemos una linea completa en cada vuelta.
    // El bucle termina cuando ya no puede leer otra linea.
    while (getline(archivo, linea)) {

        // Preparamos un lector para separar el texto
        // de esta linea en sus diferentes campos.
        stringstream fila(linea);

        // Todos los campos se reciben inicialmente como texto.
        string id;
        string jugador1;
        string puntos1;
        string jugador2;
        string puntos2;
        string ganador;
        string fecha;

        // Cada lectura toma el texto hasta la siguiente coma.
        // La siguiente lectura continua despues de esa coma.
        getline(fila, id, ',');
        getline(fila, jugador1, ',');
        getline(fila, puntos1, ',');
        getline(fila, jugador2, ',');
        getline(fila, puntos2, ',');
        getline(fila, ganador, ',');

        // La fecha es el ultimo campo:
        // leemos todo lo que queda de la linea.
        getline(fila, fecha);

        // .empty() comprueba si un texto esta vacio.
        // Si cualquiera de los campos esta vacio,
        // omitimos esta fila completa.
        if (id.empty() || jugador1.empty() || puntos1.empty() ||
            jugador2.empty() || puntos2.empty() ||
            ganador.empty() || fecha.empty()) {

            cout << "Se omitio una fila con campos vacios\n";

            // Saltamos el resto de esta vuelta
            // y pasamos a leer la siguiente fila del archivo.
            continue;
        }

        // Creamos una estructura para reunir los datos
        // de la partida que estamos leyendo.
        Partida partidaLeida{};

        // try intenta realizar las conversiones.
        // Algunas conversiones pueden lanzar excepciones.
        try {

            // Guardaran la posicion donde termino cada conversion.
            // size_t es un tipo usado para tamaños y posiciones.
            size_t posicionId = 0;
            size_t posicionPuntos1 = 0;
            size_t posicionPuntos2 = 0;

            // stoi convierte un texto en un numero entero.
            //
            // & permite que stoi escriba en la variable
            // la posicion donde termino de convertir.
            partidaLeida.id_partida = stoi(id, &posicionId);
            partidaLeida.puntaje1 = stoi(puntos1, &posicionPuntos1);
            partidaLeida.puntaje2 = stoi(puntos2, &posicionPuntos2);

            // Comprobamos que se haya convertido todo el campo.
            //
            // Ejemplo:
            // "83"    -> posicion 2 y tamaño 2: se acepta.
            // "83abc" -> posicion 2 y tamaño 5: se rechaza.
            if (posicionId != id.size() ||
                posicionPuntos1 != puntos1.size() ||
                posicionPuntos2 != puntos2.size()) {

                cout << "Se omitio una fila con un campo numerico incorrecto\n";

                // Pasamos a la siguiente fila.
                continue;
            }
        }
        catch (const exception&) {

            // Llegamos aqui si alguna conversion lanza
            // una excepcion, por ejemplo al convertir "hola"
            // o un numero demasiado grande para un int.
            //
            // const exception& recibe el error por referencia,
            // sin copiarlo y sin modificarlo.
            cout << "Se omitio una fila por un error numerico\n";

            continue;
        }

        // Estos campos ya son texto, por eso se asignan
        // directamente sin utilizar stoi.
        partidaLeida.j1 = jugador1;
        partidaLeida.j2 = jugador2;
        partidaLeida.ganador = ganador;
        partidaLeida.fecha = fecha;

        // Validamos los valores numericos:
        // - El identificador debe ser mayor que cero.
        // - Cada puntaje debe estar entre 0 y 192.
        // - La suma no puede superar las 192 casillas
        //   del tablero de 12 filas por 16 columnas.
        if (partidaLeida.id_partida <= 0 ||
            partidaLeida.puntaje1 < 0 ||
            partidaLeida.puntaje1 > 192 ||
            partidaLeida.puntaje2 < 0 ||
            partidaLeida.puntaje2 > 192 ||
            partidaLeida.puntaje1 + partidaLeida.puntaje2 > 192) {

            cout << "Se omitio una fila con valores fuera de rango\n";

            continue;
        }

        // Guardaremos quien deberia haber ganado
        // segun los puntajes de la partida.
        string ganadorEsperado;

        // Si el primer jugador tiene mas puntos, debe ganar.
        if (partidaLeida.puntaje1 > partidaLeida.puntaje2) {
            ganadorEsperado = partidaLeida.j1;
        }

        // En caso contrario, comprobamos al segundo jugador.
        else if (partidaLeida.puntaje2 > partidaLeida.puntaje1) {
            ganadorEsperado = partidaLeida.j2;
        }

        // Si ninguno tiene mas puntos, estan empatados.
        else {
            ganadorEsperado = "EMPATE";
        }

        // Comparamos el ganador del CSV con el calculado.
        // Los textos deben coincidir exactamente.
        if (partidaLeida.ganador != ganadorEsperado) {

            cout << "Se omitio la partida "
                 << partidaLeida.id_partida
                 << ": ganador incorrecto\n";

            continue;
        }

        // La partida supero las validaciones anteriores.
        // Reservamos memoria para guardarla en un nodo.
        NodoPartida* nuevo = new NodoPartida{};

        // Copiamos la estructura Partida dentro del nodo.
        nuevo->datos = partidaLeida;

        // Si la lista esta vacia, este sera su primer nodo.
        if (historial == nullptr) {
            historial = nuevo;
        }
        else {

            // Si ya hay partidas, conectamos el ultimo nodo
            // con el nodo nuevo.
            ultimo->siguiente = nuevo;
        }

        // Actualizamos cual es el ultimo nodo de la lista.
        ultimo = nuevo;
    }

    // Aqui ya terminamos de leer las filas del archivo.

    // Si no se agrego ningun nodo, no hay partidas validas.
    if (historial == nullptr) {

        cout << "Todavia no hay partidas validas\n";

        return;
    }

    // Mostramos todas las partidas validas guardadas.
    mostrarHistorial(historial);

    // Creamos otra lista: esta sera la de jugadores.
    // Cada jugador debe aparecer una sola vez.
    NodoJugador* jugadores = nullptr;

    // Recorremos el historial sin modificar su inicio.
    NodoPartida* partidaActual = historial;

    while (partidaActual != nullptr) {

        // Actualizamos los resultados del primer jugador.
        //
        // Enviamos:
        // 1. El inicio de la lista de jugadores.
        // 2. Su identificador.
        // 3. Los puntos que obtuvo.
        // 4. true si coincide con el ganador, o false si no.
        actualizarJugador(
            jugadores,
            partidaActual->datos.j1,
            partidaActual->datos.puntaje1,
            partidaActual->datos.ganador == partidaActual->datos.j1
        );

        // Hacemos lo mismo con el segundo jugador.
        // Si ya existe en la lista, se actualiza su nodo.
        actualizarJugador(
            jugadores,
            partidaActual->datos.j2,
            partidaActual->datos.puntaje2,
            partidaActual->datos.ganador == partidaActual->datos.j2
        );

        // Continuamos con la siguiente partida.
        partidaActual = partidaActual->siguiente;
    }

    // Ordenamos los jugadores cuando ya tienen
    // todos sus resultados acumulados.
    ordenarRanking(jugadores);

    cout << "\nRanking:\n";

    // Recorremos la lista ordenada.
    // En este mismo bucle mostramos y borramos cada nodo.
    while (jugadores != nullptr) {

        // Mostramos los resultados acumulados del jugador.
        cout << jugadores->datos.jugador
             << " | Partidas: " << jugadores->datos.partidas
             << " | Victorias: " << jugadores->datos.victorias
             << " | Puntos: " << jugadores->datos.puntos_totales
             << "\n";

        // Guardamos el nodo que vamos a eliminar.
        NodoJugador* borrar = jugadores;

        // Avanzamos ANTES de borrarlo para conservar
        // el acceso al resto de la lista.
        jugadores = jugadores->siguiente;

        // Liberamos la memoria reservada con new.
        delete borrar;
    }

    // La lista de jugadores ya fue liberada.
    // Ahora liberamos tambien la lista de partidas.
    while (historial != nullptr) {

        // Guardamos el nodo actual.
        NodoPartida* borrar = historial;

        // Avanzamos al siguiente.
        historial = historial->siguiente;

        // Eliminamos el nodo anterior.
        delete borrar;
    }

    // fin
}