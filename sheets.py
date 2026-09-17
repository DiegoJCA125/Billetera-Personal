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
SHEET_ID = 0

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

def actualizar_fila(numero_fila, fecha, tipo, categoria, descripcion, monto):
    """
    Sobrescribe una fila EXISTENTE con nuevos valores (a diferencia
    de agregar_fila, que siempre crea una fila nueva al final).
 
    numero_fila es la posición real en la hoja (ej. 5 = fila 5),
    el mismo número que ya calculamos en obtener_historial().
 
    El rango aquí es específico a ESA fila: "Hoja 1!A5:E5" en vez
    de "Hoja 1!A:E" (que es "todas las filas").
    """
    service = obtener_servicio()
    rango_especifico = f"Hoja 1!A{numero_fila}:E{numero_fila}"
    valores = {
        "values": [
            [fecha, tipo, categoria, descripcion, str(monto)]
        ]
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range= rango_especifico,
        valueInputOption="USER_ENTERED",
        body=valores,
    ).execute()
    
def borrar_fila(numero_fila):
    """
    Elimina POR COMPLETO una fila de la hoja (no solo borra su
    contenido, la fila desaparece y las de abajo suben una posición
    — igual que si borraras una fila a mano en Sheets con clic derecho
    > Eliminar fila).
 
    Esto usa batchUpdate() en vez de values().update(), porque estamos
    cambiando la ESTRUCTURA de la hoja (cuántas filas tiene), no solo
    el contenido de las celdas. batchUpdate() acepta una lista de
    "requests" (peticiones) — aquí solo mandamos una: "deleteDimension"
    (eliminar una dimensión, en este caso una fila).
 
    OJO con los índices: la API interna de Google cuenta las filas
    empezando en 0 (no en 1 como ves en la interfaz de Sheets), por
    eso restamos 1. Y "endIndex" es EXCLUSIVO (no incluye ese número),
    por eso no restamos ahí.
    """
    service = obtener_servicio()
    cuerpo_peticion = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": SHEET_ID,
                        "dimension": "ROWS",
                        "startIndex": numero_fila - 1,
                        "endIndex": numero_fila,
                    }
                }
            }
        ]
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=cuerpo_peticion
    ).execute()


if __name__ == "__main__":
    print("Leyendo filas actuales...")
    filas = leer_todas_las_filas()
    for fila in filas:
        print(fila)