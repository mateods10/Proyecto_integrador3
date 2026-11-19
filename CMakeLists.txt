cmake_minimum_required(VERSION 4.3)
project(Proyecto_integrador)

set(CMAKE_CXX_STANDARD 20)

add_executable(Proyecto_integrador
        cpp_datos/main.cpp
        cpp_datos/ranking.cpp
        cpp_datos/nodo.h
)