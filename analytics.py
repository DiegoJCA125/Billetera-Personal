"""
Funciones encargadas de analizar los datos financieros.

IMPORTANTE:
Este archivo NO se encarga de crear, editar o eliminar movimientos.

Su responsabilidad es obtener información útil
a partir de los movimientos almacenados en PostgreSQL.
"""

from db import obtener_conexion


def obtener_resumen_financiero():
    """
    Obtiene un resumen general de las finanzas.

    Devuelve:

    - total_ingresos
    - total_gastos
    - balance
    """

    # Abrimos una conexión con PostgreSQL
    with obtener_conexion() as conexion:

        # Creamos un cursor para ejecutar SQL
        with conexion.cursor() as cursor:

            # PostgreSQL calculará los totales directamente.
            cursor.execute(
                """
                SELECT

                    -- SUMA DE TODOS LOS INGRESOS
                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'Ingreso'
                                THEN monto
                                ELSE 0
                            END
                        ),
                        0
                    ) AS total_ingresos,

                    -- SUMA DE TODOS LOS GASTOS
                    COALESCE(
                        SUM(
                            CASE
                                WHEN tipo = 'Gasto'
                                THEN monto
                                ELSE 0
                            END
                        ),
                        0
                    ) AS total_gastos

                FROM movimientos
                """
            )

            # fetchone() devuelve una sola fila.
            resultado = cursor.fetchone()

    # Extraemos los dos valores obtenidos.
    total_ingresos, total_gastos = resultado

    # Calculamos el balance.
    balance = total_ingresos - total_gastos

    # Devolvemos los tres resultados.
    return total_ingresos, total_gastos, balance

# ---------------------------------------------------------
# PRUEBA DEL ARCHIVO
# ---------------------------------------------------------

def obtener_gastos_por_categoria():
    """
    Calcula cuánto dinero se ha gastado en cada categoría.

    Esta función pertenece a analytics.py porque su objetivo
    es analizar los datos, no registrar ni modificar movimientos.
    """

    # Abrimos la conexión con PostgreSQL.
    with obtener_conexion() as conexion:

        # Creamos un cursor para ejecutar la consulta SQL.
        with conexion.cursor() as cursor:

            # PostgreSQL agrupa los gastos por categoría y suma
            # los montos de cada grupo.
            cursor.execute("""
                SELECT
                    categoria,
                    SUM(monto) AS total_gastado
                FROM movimientos
                WHERE tipo = 'Gasto'
                GROUP BY categoria
                ORDER BY total_gastado DESC
            """)

            # Obtenemos todas las categorías con sus respectivos totales.
            resultados = cursor.fetchall()

    # Convertimos los resultados en un diccionario.
    # Ejemplo: {"Alimentación": 800000, "Transporte": 450000}
    return {
        categoria: float(total)
        for categoria, total in resultados
    }

def obtener_gastos_por_mes():
    """
    Calcula el total de gastos de cada mes.

    PostgreSQL agrupa los movimientos por año y mes.
    Así podemos comparar periodos sin mezclar, por ejemplo,
    enero de un año con enero de otro.
    """

    # Abrimos la conexión con PostgreSQL.
    with obtener_conexion() as conexion:

        # Creamos el cursor para ejecutar SQL.
        with conexion.cursor() as cursor:

            # Extraemos el año y el mes de la fecha,
            # sumamos los gastos y ordenamos cronológicamente.
            cursor.execute("""
                SELECT
                    EXTRACT(YEAR FROM fecha)::INTEGER AS anio,
                    EXTRACT(MONTH FROM fecha)::INTEGER AS mes,
                    SUM(monto) AS total_gastado
                FROM movimientos
                WHERE tipo = 'Gasto'
                GROUP BY
                    EXTRACT(YEAR FROM fecha),
                    EXTRACT(MONTH FROM fecha)
                ORDER BY anio ASC, mes ASC
            """)

            # Recuperamos los resultados de la consulta.
            resultados = cursor.fetchall()

    # Devolvemos una lista de diccionarios.
    # Cada diccionario representa un mes.
    return [
        {
            "anio": anio,
            "mes": mes,
            "total_gastado": float(total),
        }
        for anio, mes, total in resultados
    ]


def obtener_resumen_mensual():
    """
    Resume los ingresos, gastos y balance de cada mes.

    En vez de ejecutar consultas separadas, calculamos
    ingresos y gastos en una sola consulta SQL.
    """

    # Abrimos la conexión con PostgreSQL.
    with obtener_conexion() as conexion:
        with conexion.cursor() as cursor:

            # Agrupamos los movimientos por año y mes.
            # CASE permite sumar ingresos y gastos por separado.
            cursor.execute("""
                SELECT
                    EXTRACT(YEAR FROM fecha)::INTEGER AS anio,
                    EXTRACT(MONTH FROM fecha)::INTEGER AS mes,

                    COALESCE(
                        SUM(CASE
                            WHEN tipo = 'Ingreso' THEN monto
                            ELSE 0
                        END), 0
                    ) AS total_ingresos,

                    COALESCE(
                        SUM(CASE
                            WHEN tipo = 'Gasto' THEN monto
                            ELSE 0
                        END), 0
                    ) AS total_gastos

                FROM movimientos

                GROUP BY
                    EXTRACT(YEAR FROM fecha),
                    EXTRACT(MONTH FROM fecha)

                ORDER BY anio ASC, mes ASC
            """)

            # Recuperamos todos los meses calculados.
            resultados = cursor.fetchall()

    # Convertimos las filas en diccionarios fáciles de usar.
    resumen = []

    for anio, mes, ingresos, gastos in resultados:

        # Convertimos Decimal a float para trabajar cómodamente
        # con los valores desde Python y los gráficos.
        ingresos = float(ingresos)
        gastos = float(gastos)

        # El balance mensual es la diferencia entre ingresos y gastos.
        balance = ingresos - gastos

        resumen.append({
            "anio": anio,
            "mes": mes,
            "total_ingresos": ingresos,
            "total_gastos": gastos,
            "balance": balance,
        })

    return resumen


if __name__ == "__main__":

    # Ejecutamos nuestra función de análisis.
    ingresos, gastos, balance = obtener_resumen_financiero()

    # Mostramos los resultados en la terminal.
    print("\n===== RESUMEN FINANCIERO =====")

    print(f"Ingresos: ${ingresos:,.2f}")
    print(f"Gastos:   ${gastos:,.2f}")
    print(f"Balance:  ${balance:,.2f}")
    
    # Consultamos los gastos agrupados por mes.
    gastos_mensuales = obtener_gastos_por_mes()

    print("\n===== GASTOS POR MES =====")

    # Recorremos cada mes y mostramos su total.
    for registro in gastos_mensuales:
        print(
            f"{registro['anio']}-{registro['mes']:02d}: "
            f"${registro['total_gastado']:,.2f}"
        )

    # Consultamos el resumen financiero de cada mes.
    resumen_mensual = obtener_resumen_mensual()

    print("\n===== RESUMEN FINANCIERO MENSUAL =====")

    # Mostramos ingresos, gastos y balance de cada periodo.
    for registro in resumen_mensual:
        print(
            f"{registro['anio']}-{registro['mes']:02d} | "
            f"Ingresos: ${registro['total_ingresos']:,.2f} | "
            f"Gastos: ${registro['total_gastos']:,.2f} | "
            f"Balance: ${registro['balance']:,.2f}"
        )
