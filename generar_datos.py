"""
Script para generar una tabla de datos dummy (ficticios).
Genera datos aleatorios de personas con nombre, edad, email, ciudad y salario.
"""

import random
import csv
import os

NOMBRES = [
    "Carlos", "María", "Juan", "Ana", "Pedro", "Laura", "Miguel", "Sofía",
    "Diego", "Valentina", "Andrés", "Camila", "Luis", "Isabella", "Jorge",
    "Daniela", "Fernando", "Paula", "Ricardo", "Gabriela",
]

APELLIDOS = [
    "García", "Rodríguez", "Martínez", "López", "González", "Hernández",
    "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez",
    "Díaz", "Cruz", "Morales", "Reyes", "Gutiérrez", "Ortiz", "Ramos",
]

CIUDADES = [
    "Buenos Aires", "Ciudad de México", "Madrid", "Bogotá", "Lima",
    "Santiago", "Caracas", "Quito", "Montevideo", "San José",
]

DEPARTAMENTOS = [
    "Ventas", "Marketing", "Ingeniería", "Recursos Humanos",
    "Finanzas", "Soporte", "Operaciones", "Legal",
]


def generar_email(nombre, apellido):
    dominio = random.choice(["gmail.com", "outlook.com", "yahoo.com", "empresa.com"])
    return f"{nombre.lower()}.{apellido.lower()}@{dominio}"


def generar_fila():
    nombre = random.choice(NOMBRES)
    apellido = random.choice(APELLIDOS)
    edad = random.randint(22, 65)
    email = generar_email(nombre, apellido)
    ciudad = random.choice(CIUDADES)
    departamento = random.choice(DEPARTAMENTOS)
    salario = round(random.uniform(25000, 120000), 2)
    return {
        "id": None,
        "nombre": nombre,
        "apellido": apellido,
        "edad": edad,
        "email": email,
        "ciudad": ciudad,
        "departamento": departamento,
        "salario": salario,
    }


def generar_tabla(n=50):
    datos = []
    for i in range(1, n + 1):
        fila = generar_fila()
        fila["id"] = i
        datos.append(fila)
    return datos


def mostrar_tabla(datos):
    encabezados = list(datos[0].keys())
    anchos = {col: max(len(col), max(len(str(fila[col])) for fila in datos)) for col in encabezados}

    linea = "+" + "+".join("-" * (anchos[col] + 2) for col in encabezados) + "+"
    encabezado = "|" + "|".join(f" {col:^{anchos[col]}} " for col in encabezados) + "|"

    print(linea)
    print(encabezado)
    print(linea)
    for fila in datos:
        row = "|" + "|".join(f" {str(fila[col]):^{anchos[col]}} " for col in encabezados) + "|"
        print(row)
    print(linea)
    print(f"\nTotal de registros: {len(datos)}")


def exportar_csv(datos, archivo="datos_dummy.csv"):
    encabezados = list(datos[0].keys())
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=encabezados)
        writer.writeheader()
        writer.writerows(datos)
    print(f"\nDatos exportados a: {os.path.abspath(archivo)}")


if __name__ == "__main__":
    print("Generando tabla de datos dummy...\n")
    datos = generar_tabla(20)
    mostrar_tabla(datos)
    exportar_csv(datos)
