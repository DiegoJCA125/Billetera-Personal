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
    print(f"REGISTRADO: {tipo} | {categoria} | {descripcion} | ${monto}")

def registrar_gasto(categoria, descripcion, monto):
    """
    Función para registrar un gasto.
    """
    registrar_movimiento("Gasto", categoria, descripcion, monto)

def registrar_ingreso(categoria, descripcion, monto):
    """
    Función para registrar un ingreso.
    """
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
    # se salta  el encabezado al hacer los cálculos.
    datos = filas[1:]
    total_ingresos = 0
    total_gastos = 0

    for fila in datos:
        # Se desempaca cada fila en variables con nombre, más
        # facil de leer  fila[0], fila[1], etc.
        fecha, tipo, categoria, descripcion, monto = fila
        monto = float(monto)  # Convierte el monto de texto a número ya que desde Sheets, lelga como String

        if tipo == "Ingreso":
            total_ingresos += monto
        elif tipo == "Gasto":
            total_gastos += monto
    balance = total_ingresos - total_gastos
    return total_ingresos, total_gastos, balance

def mostrar_resumen():
    ingresos, gastos, balance = calcular_balance()
    print("\n RESUMEN DE TU BILLETERA")
    print(f" Ingresos totales:   ${ingresos:,.0f}")
    print(f" Gastos totales:     ${gastos:,.0f}")
    print(f" Balance actual:     ${balance:,.0f}")

def menu():
    """
    Menú interactivo por consola. Le muestramos opciones al usuario,
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
        print("\n--- MENÚ DE BILLETERA PERSONAL ---")
        print("1. Registrar un gasto")
        print("2. Registrar un ingreso")
        print("3. Mostrar resumen")
        print("4. Salir")
        opcion = input("Elige una opción (1-4): ")

        if opcion == "1":
            categoria = input("Categoria (Eje. Comida, Transporte, Entretenimiento):")
            descripcion = input("Descripcion: ")
            monto = float(input("Monto: "))
            registrar_gasto(categoria, descripcion, monto)

        elif opcion == "2":
            categoria = input("Categoria (Eje. Sueldo, Bono, Ingresos Extra):")
            descripcion = input("Descripcion: ")
            monto = float(input("Monto: "))
            registrar_ingreso(categoria, descripcion, monto)

        elif opcion == "3":
            mostrar_resumen()

        elif opcion == "4":
            print("¡Hasta luego!")
            break

        else:
            print("Opcion no validar, intenta de nuevo 1-4")

if __name__ == "__main__":
    menu()