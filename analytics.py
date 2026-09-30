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

if __name__ == "__main__":

    # Ejecutamos nuestra función de análisis.
    ingresos, gastos, balance = obtener_resumen_financiero()

    # Mostramos los resultados en la terminal.
    print("\n===== RESUMEN FINANCIERO =====")

    print(f"Ingresos: ${ingresos:,.2f}")
    print(f"Gastos:   ${gastos:,.2f}")
    print(f"Balance:  ${balance:,.2f}")