"""
main.py
--------
Lógica de negocio. Las operaciones CRUD vienen de db.py; todo cálculo
o análisis viene de analytics.py — sin excepciones, para no tener dos
caminos distintos calculando lo mismo.
"""

from datetime import date
from math import isfinite

from db import (
    leer_todas_las_filas,
    agregar_fila,
    actualizar_fila,
    borrar_fila,
    obtener_fila_por_id,
)

# Todo lo que sea "calcular" o "analizar" viene de analytics.py.
from analytics import (
    obtener_gastos_por_categoria,
    obtener_resumen_financiero,
    obtener_resumen_mensual,
)

def validar_movimiento(tipo, categoria, descripcion, monto):
    """
    Valida los datos de un movimiento ANTES de enviarlos a PostgreSQL.

    Esta función representa nuestra primera capa de calidad de datos:
    si los datos no cumplen las reglas, ni siquiera intentamos guardarlos.
    """
    # VALIDAMOS QUE EL TIPO SEA UNO DE LOS VALORES PERMITIDOS
    if tipo not in ("Gasto", "Ingreso"):
        raise ValueError("El tipo de movimiento debe ser 'Gasto' o 'Ingreso'")

    # VALIDA QUE LA CATEOGIRA EXISTE Y NO SEA SOLO ESPACIO
    if not categoria or not categoria.strip():
        raise ValueError("La cateogria es obligatoria")

    # POSTGRESQL DEFINE categori COMO VARCHAR(100) POR ESO SE VALIDA A SI MISMO EL LIMITE ANTES DE LLEGAR A LA BASE DE DATOS
    if len(categoria.strip()) > 100:
        raise ValueError("La categoria no puede superar los 100 caracteres")

    #VALIDA QUE LA DESCRIPCION EXISTE
    if not descripcion or not descripcion.strip():
        raise ValueError("La descripcion es obligatoria")

    #SE VALIDA QUE EL MONTO SE UN NUMERO
    try:
        monto = float(monto)
    except (TypeError, ValueError):
        raise ValueError("El monto debe ser un numero valido")

    # EVITAMOS VALORES COMO NaN O INFINITO.
    if not isfinite(monto):
        raise ValueError("El monto debe ser un número finito.")

    # UN MOVIMIENTO FINANCIERO NO DEBE TENER UN MONTO NEGATIVO.
    if monto < 0:
        raise ValueError("El monto no puede ser negativo.")

    # DEVOLVEMOS LOS DATOS LIMPIOS PARA QUE EL RESTO DEL PROGRAMA
    # TRABAJE CON ELLOS.
    return tipo, categoria.strip(), descripcion.strip(), monto


def registrar_movimiento(tipo, categoria, descripcion, monto):
    # PRIMERO VALIDAMOS LOS DATOS.
    # SI ALGO ESTÁ MAL, ValueError DETIENE EL PROCESO
    # Y NO SE ENVÍA NADA A POSTGRESQL.
    tipo, categoria, descripcion, monto = validar_movimiento(
        tipo,
        categoria,
        descripcion,
        monto,
    )

    # SI LLEGAMOS AQUÍ, LOS DATOS PASARON NUESTRAS VALIDACIONES.
    fecha_hoy = date.today().isoformat()

    # AHORA SÍ GUARDAMOS EL MOVIMIENTO EN POSTGRESQL.
    agregar_fila(
        fecha_hoy,
        tipo,
        categoria,
        descripcion,
        monto,
    )

    print(f"✅ Registrado: {tipo} | {categoria} | {descripcion} | ${monto}")


def registrar_gasto(categoria, descripcion, monto):
    registrar_movimiento("Gasto", categoria, descripcion, monto)


def registrar_ingreso(categoria, descripcion, monto):
    registrar_movimiento("Ingreso", categoria, descripcion, monto)


def eliminar_movimiento(id_movimiento):
    borrar_fila(id_movimiento)
    print(f"🗑️ Movimiento {id_movimiento} eliminado.")


def editar_movimiento(id_movimiento, tipo, categoria, descripcion, monto):
    fila_actual = obtener_fila_por_id(id_movimiento)

    if fila_actual is None:
        print(f"⚠️ No se encontró ningún movimiento con id {id_movimiento}.")
        return

    fecha_original = fila_actual[1]
    actualizar_fila(id_movimiento, fecha_original, tipo, categoria, descripcion, monto)
    print(f"✅ Movimiento {id_movimiento} actualizado.")


def obtener_historial(limite=10):
    filas = leer_todas_las_filas()

    historial = []
    for fila in filas:
        id_mov, fecha, tipo, categoria, descripcion, monto = fila
        historial.append({
            "fila_numero": id_mov,
            "fecha": fecha.isoformat(),
            "tipo": tipo,
            "categoria": categoria,
            "descripcion": descripcion,
            "monto": float(monto),
        })

    return historial[::-1][:limite]


def calcular_balance():
    """
    ANTES: llamaba a db.obtener_balance() directamente — un segundo
    camino para el mismo cálculo que ya existía en analytics.py.
    AHORA: delega por completo a analytics.obtener_resumen_financiero(),
    que es la única fuente de verdad para este número.
    """
    total_ingresos, total_gastos, balance = obtener_resumen_financiero()
    return float(total_ingresos), float(total_gastos), float(balance)


def gastos_por_categoria():
    return obtener_gastos_por_categoria()


def resumen_mensual():
    """
    NUEVO: expone obtener_resumen_mensual() de analytics.py al resto
    de la app (consola y Flask). Devuelve una lista de diccionarios,
    uno por mes, cada uno con anio, mes, total_ingresos, total_gastos
    y balance.
    """
    return obtener_resumen_mensual()


def mostrar_resumen():
    ingresos, gastos, balance = calcular_balance()
    print("\n📊 RESUMEN DE TU BILLETERA")
    print(f"   Ingresos totales: ${ingresos:,.0f}")
    print(f"   Gastos totales:   ${gastos:,.0f}")
    print(f"   Balance actual:   ${balance:,.0f}")


MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def mostrar_resumen_mensual():
    datos = resumen_mensual()

    if not datos:
        print("\nTodavía no hay suficientes movimientos para un resumen mensual.")
        return

    print("\n📅 RESUMEN FINANCIERO MENSUAL")
    for registro in datos:
        nombre_mes = MESES[registro["mes"] - 1]
        print(
            f"   {nombre_mes} {registro['anio']} | "
            f"Ingresos: ${registro['total_ingresos']:,.0f} | "
            f"Gastos: ${registro['total_gastos']:,.0f} | "
            f"Balance: ${registro['balance']:,.0f}"
        )


def menu():
    while True:
        print("\n===== BILLETERA PERSONAL =====")
        print("1. Registrar un gasto")
        print("2. Registrar un ingreso")
        print("3. Ver resumen")
        print("4. Ver historial")
        print("5. Editar un movimiento")
        print("6. Eliminar un movimiento")
        print("7. Ver resumen mensual")
        print("8. Salir")
        opcion = input("Elige una opción (1-8): ")

        if opcion == "1":
            categoria = input("Categoría: ")
            descripcion = input("Descripción: ")
            monto = float(input("Monto: "))
            registrar_gasto(categoria, descripcion, monto)

        elif opcion == "2":
            categoria = input("Categoría: ")
            descripcion = input("Descripción: ")
            monto = float(input("Monto: "))
            registrar_ingreso(categoria, descripcion, monto)

        elif opcion == "3":
            mostrar_resumen()

        elif opcion == "4":
            historial = obtener_historial(limite=10)
            print("\n📋 ÚLTIMOS 10 MOVIMIENTOS")
            for movimiento in historial:
                print(
                    f"   [{movimiento['fila_numero']}] "
                    f"{movimiento['fecha']} | {movimiento['tipo']} | "
                    f"{movimiento['categoria']} | {movimiento['descripcion']} | "
                    f"${movimiento['monto']:,.0f}"
                )

        elif opcion == "5":
            id_movimiento = int(input("ID del movimiento a editar: "))
            tipo = input("Nuevo tipo (Gasto/Ingreso): ")
            categoria = input("Nueva categoría: ")
            descripcion = input("Nueva descripción: ")
            monto = float(input("Nuevo monto: "))
            editar_movimiento(id_movimiento, tipo, categoria, descripcion, monto)

        elif opcion == "6":
            id_movimiento = int(input("ID del movimiento a eliminar: "))
            eliminar_movimiento(id_movimiento)

        elif opcion == "7":
            mostrar_resumen_mensual()

        elif opcion == "8":
            print("¡Hasta luego! 👋")
            break

        else:
            print("Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    menu()