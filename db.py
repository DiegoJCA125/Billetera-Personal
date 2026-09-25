"""
db.py
------
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

# DATABASE_URL sigue el mismo patrón que ya conoces de APP_USERNAME/
# APP_PASSWORD: se lee de una variable de entorno, nunca escrita en
# el código. El formato de esta URL es:
# postgresql://usuario:contraseña@host:puerto/nombre_basededatos
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


def obtener_balance():
    """
    En vez de traer TODAS las filas y sumarlas en Python (como
    hacíamos con calcular_balance() en la versión de Sheets), le
    pedimos a PostgreSQL que haga la suma DIRECTAMENTE con SQL.

    CASE WHEN ... THEN ... ELSE ... END es el "if" de SQL: por cada
    fila, si el tipo es 'Ingreso' suma el monto, si no, suma 0 —
    así el SUM() solo termina contando lo que nos interesa en cada
    columna calculada.

    COALESCE(algo, 0) devuelve 0 en vez de NULL cuando la tabla está
    vacía (SUM() de cero filas da NULL, no 0, y eso rompería cálculos
    después si no lo manejamos).
    """
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COALESCE(SUM(CASE WHEN tipo = 'Ingreso' THEN monto ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN tipo = 'Gasto' THEN monto ELSE 0 END), 0)
                FROM movimientos
            """)
            total_ingresos, total_gastos = cursor.fetchone()

    return total_ingresos, total_gastos


def obtener_totales_por_categoria():
    """
    El equivalente en SQL de lo que antes hacías con un diccionario
    y un bucle for en Python (gastos_por_categoria en main.py).

    GROUP BY categoria le dice a PostgreSQL: "junta todas las filas
    que tengan la misma categoría, y aplícales SUM() a cada grupo por
    separado". Es exactamente el mismo concepto de un GROUP BY que ya
    viste en tu curso de SQL — pero aquí es la base de datos la que
    hace el trabajo, no tu código.
    """
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT categoria, SUM(monto)
                FROM movimientos
                WHERE tipo = 'Gasto'
                GROUP BY categoria
                ORDER BY SUM(monto) DESC
            """)
            resultados = cursor.fetchall()

    return resultados


if __name__ == "__main__":
    # Prueba rápida: intenta conectarse y contar cuántas filas hay.
    filas = leer_todas_las_filas()
    print(f" CONEXION EXITOSA. La tabla tiene {len(filas)} filas.")
