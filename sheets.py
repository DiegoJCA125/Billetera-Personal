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

from googleapiclient.discovery import build
from auth import obtener_credenciales

SPREADSHEET_ID = "1PW8ah_QxY-nPRNJFaxYTghfHIuOJsMWLbI0lKD2pzhM"

# El "rango" le dice a la API en que pestaña y que columnas trabajar.
# "Hoja 1" es el nombre de la pestaña (así se llama por defecto en
# "A:E" significa "desde la columna A hasta la E" (nuestras 5 columnas).

RANGO = "Hoja 1!A:E"

def obtener_servicio():
    """
    Construye y devuelve un objeto "service" para interactuar con la API de Sheets.
    """
    creds = obtener_credenciales()
    service = build("sheets", "v4", credentials=creds)
    return service

def leer_todas_las_filas():
    """
    Lee todas las filas de la hoja de cálculo y devuelve una lista de listas.
    Cada sublista representa una fila.
    """
    service = obtener_servicio()
    """ .spreadsheets().values().get() es el método específico para
    LEER un rango de celdas. execute() es lo que realmente
    dispara la petición HTTP hacia Google (antes de eso, solo estabamos "armando" la petición).
    """
    resultado = (
        service.spreadsheets().values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGO).execute()
    )
    filas = resultado.get("values",[])
    return filas 

def agregar_fila(fecha, tipo, categoria, descripcion, monto):
    """
    Agrega una nueva fila a la hoja de cálculo con los datos proporcionados.
    """
    service = obtener_servicio()

    """" La API espera los valores en este formato anidado: una lista de filas, y cada fila es una lista de columnas.
    Aquí solo mandamos UNA fila, por eso es una lista con un solo elemento adentro."""
    valores = {
        "values": [[fecha, tipo, categoria, descripcion, str(monto)]
        ]
    }
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGO,
        valueInputOption="USER_ENTERED",
        body=valores
    ).execute()

if __name__ == "__main__":
    print("LEYENDO FILAS ACTUALES...")
    filas = leer_todas_las_filas()
    for fila in filas:
        print(fila) 
    print("\nAGREGANDO UNA FILA NUEVA...")
    agregar_fila("2026-09-04", "Gasto", "Celular", "Recarga de Prueba", 15000)
    print("FILA AGREGADA. REVISA GOOGLE SHEETS")