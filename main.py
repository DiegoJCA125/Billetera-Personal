"""
main.py
--------
Misma lógica de negocio de siempre, pero ahora hablando con db.py
(PostgreSQL) en vez de sheets.py (Google Sheets API).

Fíjate en algo importante: las funciones que usa app.py (Flask) se
llaman EXACTAMENTE igual que antes (registrar_gasto, calcular_balance,
obtener_historial, etc.) — por eso app.py y los templates HTML no
necesitan casi ningún cambio. Esto es la ventaja real de haber
separado responsabilidades desde el principio: pudimos cambiar POR
COMPLETO la forma en que se guardan los datos sin tocar la interfaz
web para nada.
"""

from datetime import date
from db import (
    leer_todas_las_filas,
    agregar_fila,
    actualizar_fila,
    borrar_fila,
    obtener_fila_por_id,
    obtener_balance,
    obtener_totales_por_categoria,
)


def registrar_movimiento(tipo, categoria, descripcion, monto):
    fecha_hoy = date.today().isoformat()
    agregar_fila(fecha_hoy, tipo, categoria, descripcion, monto)
    print(f"✅ Registrado: {tipo} | {categoria} | {descripcion} | ${monto}")


def registrar_gasto(categoria, descripcion, monto):
    registrar_movimiento("Gasto", categoria, descripcion, monto)


def registrar_ingreso(categoria, descripcion, monto):
    registrar_movimiento("Ingreso", categoria, descripcion, monto)


def eliminar_movimiento(id_movimiento):
    borrar_fila(id_movimiento)
    print(f"🗑️ Movimiento {id_movimiento} eliminado.")


def editar_movimiento(id_movimiento, tipo, categoria, descripcion, monto):
    """
    Igual que antes: conservamos la fecha ORIGINAL del movimiento en
    vez de reemplazarla por la de hoy. Ahora, en vez de recorrer todo
    el historial buscando el id (como hacíamos con la lista de
    Sheets), pedimos DIRECTAMENTE esa fila por su id con una consulta
    SQL — mucho más eficiente.
    """
    fila_actual = obtener_fila_por_id(id_movimiento)

    if fila_actual is None:
        print(f"⚠️ No se encontró ningún movimiento con id {id_movimiento}.")
        return

    # fila_actual es una tupla: (id, fecha, tipo, categoria, descripcion, monto)
    # Nos interesa solo la fecha, que es el segundo elemento (índice 1).
    fecha_original = fila_actual[1]

    actualizar_fila(id_movimiento, fecha_original, tipo, categoria, descripcion, monto)
    print(f"✅ Movimiento {id_movimiento} actualizado.")


def obtener_historial(limite=10):
    """
    Ahora esto es mucho más simple que la versión de Sheets: ya no
    tenemos que calcular "en qué fila de la hoja está esto" a mano
    (indice + 2, etc.) — PostgreSQL nos da el id REAL de cada fila
    directamente, así que solo hay que darle formato a cada tupla
    como diccionario.

    Mantenemos la llave "fila_numero" en el diccionario (aunque
    ahora es el id real de la base de datos) para no tener que
    modificar app.py ni los templates HTML — siguen funcionando
    exactamente igual sin cambios.
    """
    filas = leer_todas_las_filas()  # ya vienen ordenadas por fecha ASC

    historial = []
    for fila in filas:
        id_mov, fecha, tipo, categoria, descripcion, monto = fila
        historial.append({
            "fila_numero": id_mov,
            "fecha": fecha.isoformat(),  # PostgreSQL devuelve un objeto date, lo convertimos a texto
            "tipo": tipo,
            "categoria": categoria,
            "descripcion": descripcion,
            "monto": float(monto),  # NUMERIC llega como Decimal, lo pasamos a float
        })

    # Igual que antes: invertimos para mostrar lo más reciente primero,
    # y nos quedamos solo con los primeros "limite".
    return historial[::-1][:limite]


def calcular_balance():
    """
    Ya no sumamos en un bucle de Python — obtener_balance() le pide
    a PostgreSQL que haga la suma directamente con SQL, y aquí solo
    calculamos la resta final.
    """
    total_ingresos, total_gastos = obtener_balance()
    total_ingresos = float(total_ingresos)
    total_gastos = float(total_gastos)
    balance = total_ingresos - total_gastos
    return total_ingresos, total_gastos, balance


def gastos_por_categoria():
    """
    Igual: ya no agrupamos a mano con un diccionario en Python,
    PostgreSQL nos entrega los totales ya agrupados con GROUP BY.
    Solo convertimos el resultado a un diccionario de Python.
    """
    resultados = obtener_totales_por_categoria()
    return {categoria: float(total) for categoria, total in resultados}


def mostrar_resumen():
    ingresos, gastos, balance = calcular_balance()
    print("\n📊 RESUMEN DE TU BILLETERA")
    print(f"   Ingresos totales: ${ingresos:,.0f}")
    print(f"   Gastos totales:   ${gastos:,.0f}")
    print(f"   Balance actual:   ${balance:,.0f}")


def menu():
    while True:
        print("\n===== BILLETERA PERSONAL =====")
        print("1. Registrar un gasto")
        print("2. Registrar un ingreso")
        print("3. Ver resumen")
        print("4. Ver historial")
        print("5. Editar un movimiento")
        print("6. Eliminar un movimiento")
        print("7. Salir")
        opcion = input("Elige una opción (1-7): ")

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
            print("¡Hasta luego! 👋")
            break

        else:
            print("Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    menu()