"""
Reemplaza a sheets.py y auth.py por completo. Ya no necesitamos
autenticarnos con Google ni hablar HTTP con una API externa — nos
conectamos DIRECTAMENTE a la base de datos con una librería.

Concepto clave: cursor
-------------------------
Una "conexión" es el canal abierto hacia la base de datos. Un
"cursor" es la herramienta que usas DENTRO de esa conexión para
mandar comandos SQL y leer los resultados — piensa en la conexión
como la llamada telefónica, y el cursor como tu voz hablando durante
esa llamada.
"""

import os
import psycopg2
from psycopg2 import errors #PERMITE IDENTIFICAR ERRORES ESPECIFICOS EN EL POSTGRESQL

DATABASE_URL = os.environ.get("DATABASE_URL")


def obtener_conexion():
    """
    Abre y devuelve una conexión nueva a PostgreSQL.

    psycopg2.connect() acepta la URL completa directamente, así no
    tenemos que separar manualmente usuario/contraseña/host como
    parámetros sueltos.
    """
    conexion = psycopg2.connect(DATABASE_URL)
    return conexion


def leer_todas_las_filas():
    """
    Equivalente a sheets.py: leer_todas_las_filas().
    Aquí, en vez de pedir un rango de celdas, mandamos una consulta
    SQL real.

    "with conexion:" y "with conexion.cursor() as cursor:" son
    "context managers" — se aseguran de cerrar la conexión/cursor
    automáticamente al terminar, incluso si algo falla en el medio.
    Esto evita dejar conexiones "colgadas" abiertas por accidente.
    """
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id, fecha, tipo, categoria, descripcion, monto "
                "FROM movimientos ORDER BY fecha ASC, id ASC"
            )
            # fetchall() trae TODAS las filas que coincidieron,
            # como una lista de tuplas: [(1, fecha, 'Gasto', ...), ...]
            filas = cursor.fetchall()

    return filas


def agregar_fila(fecha, tipo, categoria, descripcion, monto):
    """
    Equivalente a sheets.py: agregar_fila().

    %s son "placeholders" — psycopg2 los reemplaza de forma SEGURA
    por los valores reales que le pasamos en la tupla de después.

    IMPORTANTE POR SEGURIDAD: nunca construyas la consulta SQL
    pegando texto directamente (ej. f"...VALUES ('{fecha}', ...)")
    — eso abre la puerta a "SQL injection", donde alguien podría
    escribir datos maliciosos que se ejecuten como comandos SQL
    reales. Los placeholders %s evitan ese riesgo por completo.
    """
    try:
        # ABRIMOS UNA CONEXION CON POSTGRESQL
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO movimientos (fecha, tipo, categoria, descripcion, monto) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (fecha, tipo, categoria, descripcion, monto),
                )
            # conexion.commit() "confirma" los cambios de forma permanente.
            # Sin esto, el INSERT quedaría pendiente y se perdería al
            # cerrar la conexión. Vive fuera del cursor, sobre la conexión.
            conexion.commit()
        # SI EL MOVIMIENTO SE GUARDO CORRECTAMENTE
        return True
    
    except Exception as error:
        # SI POSTGRESQL ENCUENTRA UN PROBLEM, SE CAPTURARA EL ERROR PARA EVITAR QUE LA APLICACION COLAPSE
        print(f"ERROR AL AGREGAR MOVIMIENTO: {error}")
        # COLOCAREMOS QWUE LA OPERACION NO FUE EXITOSA
        return False

def actualizar_fila(id_movimiento, fecha, tipo, categoria, descripcion, monto):
    """Equivalente a sheets.py: actualizar_fila(), pero usando el id real."""
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "UPDATE movimientos "
                "SET fecha = %s, tipo = %s, categoria = %s, "
                "    descripcion = %s, monto = %s "
                "WHERE id = %s",
                (fecha, tipo, categoria, descripcion, monto, id_movimiento),
            )
        conexion.commit()


def borrar_fila(id_movimiento):
    """
    Equivalente a sheets.py: borrar_fila().

    Mucho más simple que el batchUpdate() de la API de Sheets con
    índices desde 0 — aquí un DELETE con un WHERE basta.
    """
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "DELETE FROM movimientos WHERE id = %s",
                (id_movimiento,),
            )
        conexion.commit()


def obtener_fila_por_id(id_movimiento):
    """
    Trae UNA sola fila por su id. La necesitamos para "editar": antes
    de sobrescribir un movimiento, queremos conservar su fecha
    original (igual que hacíamos antes buscando en el historial
    completo — aquí es más directo, un SELECT con WHERE).
    """
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(
                "SELECT id, fecha, tipo, categoria, descripcion, monto "
                "FROM movimientos WHERE id = %s",
                (id_movimiento,),
            )
            # fetchone() trae solo UNA fila (o None si no existe),
            # a diferencia de fetchall() que trae todas.
            fila = cursor.fetchone()

    return fila

if __name__ == "__main__":
    # Prueba rápida: intenta conectarse y contar cuántas filas hay.
    filas = leer_todas_las_filas()
    print(f" CONEXION EXITOSA. La tabla tiene {len(filas)} filas.")
