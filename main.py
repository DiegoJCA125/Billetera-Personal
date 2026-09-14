"""
main.py
--------
Aquí vive la LÓGICA DE NEGOCIO de la billetera: las reglas de qué
significa "registrar un gasto" o "calcular mi balance". Este archivo
NO sabe nada de cómo se conecta a Google — para eso usa las funciones
que ya construimos en sheets.py. Esto es una buena práctica que se
llama "separación de responsabilidades": cada archivo hace una sola
cosa y la hace bien.
"""

from datetime import date
from sheets import leer_todas_las_filas, agregar_fila


def registrar_movimiento(tipo, categoria, descripcion, monto):
    """
    Función genérica para registrar CUALQUIER movimiento (gasto o ingreso).
    Las funciones de arriba (registrar_gasto, registrar_ingreso) son solo
    atajos más claros de usar, pero ambas terminan llamando a esta.

    date.today() devuelve la fecha de HOY automáticamente, así no
    tienes que escribirla a mano cada vez.
    .isoformat() la convierte al formato "AAAA-MM-DD" (ej. 2026-09-04),
    que es el estándar que ya usamos en la hoja.
    """
    fecha_hoy = date.today().isoformat()
    agregar_fila(fecha_hoy, tipo, categoria, descripcion, monto)
    print(f"✅ Registrado: {tipo} | {categoria} | {descripcion} | ${monto}")


def registrar_gasto(categoria, descripcion, monto):
    """Atajo para registrar un gasto. Simplemente fija tipo='Gasto'."""
    registrar_movimiento("Gasto", categoria, descripcion, monto)


def registrar_ingreso(categoria, descripcion, monto):
    """Atajo para registrar un ingreso (ej. tu salario)."""
    registrar_movimiento("Ingreso", categoria, descripcion, monto)


def calcular_balance():
    """
    Recorre TODAS las filas de la hoja y calcula:
    - total de ingresos
    - total de gastos
    - balance = ingresos - gastos

    Devuelve los tres valores como una tupla (varios valores juntos).
    """
    filas = leer_todas_las_filas()

    # filas[0] es el encabezado ("Fecha", "Tipo", ...), no un dato real.
    # filas[1:] significa "todas las filas EXCEPTO la primera" — así
    # nos saltamos el encabezado al hacer los cálculos.
    datos = filas[1:]

    total_ingresos = 0
    total_gastos = 0

    for fila in datos:
        # Desempaquetamos cada fila en variables con nombre, más
        # legible que usar fila[0], fila[1], etc.
        fecha, tipo, categoria, descripcion, monto = fila

        # El monto llega como texto (string) desde Sheets, por eso
        # hay que convertirlo a número con float() antes de sumarlo.
        monto = float(monto)

        if tipo == "Ingreso":
            total_ingresos += monto
        elif tipo == "Gasto":
            total_gastos += monto

    balance = total_ingresos - total_gastos
    return total_ingresos, total_gastos, balance


def obtener_historial(limite=10):
    """
    Devuelve los últimos 'limite' movimientos, del más reciente al
    más antiguo, listos para mostrar en pantalla o en la web.

    Cada movimiento se devuelve como un diccionario (no una lista
    simple) para que sea más legible acceder a sus datos: en vez de
    fila[0], fila[1]..., podrás usar movimiento["fecha"],
    movimiento["monto"], etc.

    OJO: también guardamos "fila_numero" — la posición REAL de esa
    fila dentro de la Google Sheet (contando el encabezado como
    fila 1). Todavía no lo usamos para nada, pero lo vamos a
    necesitar en el próximo paso, cuando agreguemos "editar" y
    "borrar" — para eso hay que saber EXACTAMENTE qué fila tocar.
    """
    filas = leer_todas_las_filas()
    datos = filas[1:]  # nos saltamos el encabezado

    historial = []
    for indice, fila in enumerate(datos):
        # enumerate() nos da, en cada vuelta del bucle, tanto la
        # POSICIÓN (indice: 0, 1, 2...) como el VALOR (fila).
        # La fila real en Sheets es indice + 2, porque:
        #   - Sheets empieza a contar en 1, no en 0 (+1)
        #   - la fila 1 es el encabezado, así que los datos
        #     empiezan en la fila 2 (+1 otra vez)
        fecha, tipo, categoria, descripcion, monto = fila
        historial.append({
            "fila_numero": indice + 2,
            "fecha": fecha,
            "tipo": tipo,
            "categoria": categoria,
            "descripcion": descripcion,
            "monto": float(monto),
        })

    # [::-1] invierte el orden de la lista (Sheets nos da lo más
    # viejo primero; para un historial, queremos lo más reciente
    # arriba, que es como esperamos ver un extracto bancario).
    historial_reciente_primero = historial[::-1]

    # Slicing de nuevo: nos quedamos solo con los primeros "limite"
    # elementos de esa lista ya invertida.
    return historial_reciente_primero[:limite]


def mostrar_resumen():
    """
    Imprime en pantalla un resumen legible del estado de la billetera.
    Separamos esto de calcular_balance() porque una función calcula
    (devuelve números) y la otra solo se encarga de mostrarlos bonito.
    Así, más adelante, si quieres mostrar el resumen en una página web
    en vez de la consola, reutilizas calcular_balance() sin tocarlo.
    """
    ingresos, gastos, balance = calcular_balance()
    print("\n📊 RESUMEN DE TU BILLETERA")
    print(f"   Ingresos totales: ${ingresos:,.0f}")
    print(f"   Gastos totales:   ${gastos:,.0f}")
    print(f"   Balance actual:   ${balance:,.0f}")


def menu():
    """
    Menú interactivo por consola. Le muestra opciones al usuario,
    lee lo que escribe con input(), y según la opción llama a la
    función correspondiente.

    input() SIEMPRE devuelve texto (string), aunque el usuario
    escriba un número — por eso más abajo convertimos con float()
    cuando pedimos el monto.

    El bucle "while True" hace que el menú se repita indefinidamente
    hasta que el usuario elija la opción de salir (rompemos el bucle
    con la palabra clave "break").
    """
    while True:
        print("\n===== BILLETERA PERSONAL =====")
        print("1. Registrar un gasto")
        print("2. Registrar un ingreso")
        print("3. Ver resumen")
        print("4. Ver historial")
        print("5. Salir")
        opcion = input("Elige una opción (1-5): ")

        if opcion == "1":
            categoria = input("Categoría (ej. Comida, Transporte): ")
            descripcion = input("Descripción: ")
            monto = float(input("Monto: "))
            registrar_gasto(categoria, descripcion, monto)

        elif opcion == "2":
            categoria = input("Categoría (ej. Salario, Bono): ")
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
            print("¡Hasta luego! 👋")
            break

        else:
            # Manejo simple de errores: si el usuario escribe algo
            # que no es 1, 2, 3 o 4, se lo avisamos y el bucle
            # vuelve a mostrar el menú (no se rompe el programa).
            print("Opción no válida, intenta de nuevo.")


# Este bloque ahora solo arranca el menú interactivo — ya no
# registra nada automáticamente al correr el script.
if __name__ == "__main__":
    menu()