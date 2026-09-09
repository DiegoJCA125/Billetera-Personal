"""
sheets.py
----------
Este modulo contiene las funciones que hablan directamente con Google Sheet: leer todas las filas y agregar una fila nueva.
 
Concepto clave: el "servicio" (service)
-----------------------------------------
Para hacer CUALQUIER operacion con la API de Sheets, primero hay que
construir un objeto "service". Piensa en él como un "control remoto"
ya configurado con las credenciales: una vez se tiene,se puede usar
para leer, escribir, borrar, etc. sin tener que autenticar de nuevo
en cada función.
"""

from auth import obtener_servicio

SPREADSHEET_ID = "1PW8ah_QxY-nPRNJFaxYTghfHIuOJsMWLbI0lKD2pzhM"

# El "rango" le dice a la API en que pestaña y que columnas trabajar.
# "Hoja 1" es el nombre de la pestaña (así se llama por defecto en
# "A:E" significa "desde la columna A hasta la E" (nuestras 5 columnas).

RANGO = "Hoja 1!A:E"

def leer_todas_las_filas():
    service = obtener_servicio()
    resultado = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGO)
        .execute()
    )
    filas = resultado.get("values", [])
    return filas

def agregar_fila(fecha, tipo, categoria, descripcion, monto):
    service = obtener_servicio()
    valores = {
        "values": [
            [fecha, tipo, categoria, descripcion, monto]
        ]
    }
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGO,
        valueInputOption="USER_ENTERED",
        body=valores,
    ).execute()

if __name__ == "__main__":
    print("Leyendo filas actuales...")
    filas = leer_todas_las_filas()
    for fila in filas:
        print(fila)