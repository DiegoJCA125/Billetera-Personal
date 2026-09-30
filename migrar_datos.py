from sheets import leer_todas_las_filas as leer_de_sheets
from db import agregar_fila

def migrar():
    filas = leer_de_sheets()
    datos = filas[1:]
    # SALTARA LA PRIMERA FILA, QUE ES EL ENCABEZADO, YA QUE NO SE NECESITA
    print(f"Se encontraron {len(datos)} movimientos en Google Sheets")
    confirmacion = input("Migrar todos a PostgreSQL? (s/n): ")

    if confirmacion.lower() != "s":
        print("Migracion cancelada")
        return

    migrados = 0
    for fila in datos:
        fecha, tipo, categoria, descripcion, monto = fila
        agregar_fila(fecha, tipo, categoria, descripcion, float(monto))
        migrados += 1
        print(f" ✅ [{migrados}/{len(datos)}] {tipo} | {categoria} | ${monto}")

    print(f"💥 Migracion completa: {migrados} movimientos copiados a PostgreSQL")

if __name__ == "__main__":
    migrar()