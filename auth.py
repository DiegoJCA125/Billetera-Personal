"""
auth.py (versión lista para producción)
------------------------------------------
Ahora esta función revisa DOS posibles fuentes para las credenciales,
en este orden:
 
1. Variable de entorno GOOGLE_SERVICE_ACCOUNT_JSON
   -> Se usa cuando la app corre en Render (o cualquier hosting).
      Ahí no existe el archivo físico, así que guardamos el JSON
      completo como texto dentro de esa variable.
 
2. Archivo local service_account.json
   -> Se usa cuando trabajas en tu propia PC, como hasta ahora.
 
Así, el MISMO código funciona en los dos ambientes sin tener que
mantener dos versiones distintas.
"""
# LIBRERIAS QUE SE INSTALAN
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# SCOPES DEFINE QUE PUEDE HACER EN LA PP EN UNA LISTA DE PERMISOS
# SE PEDIRA PERMISOS PARA LEER Y ESCRIBIR EN EL SHEETS
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# NOMBRE DEL ARCHIVO DE LA LLAVE DE LA CUENTA DEL SERVICIO
ARCHIVO_LLAVE = "service_account.json"
NOMBRE_VARIABLE_ENTORNO = "GOOGLE_SERVICE_ACCOUNT_JSON"

def obtener_credenciales():
    """
    os.environ.get(nombre) busca una variable de entorno por su
    nombre. Si no existe, devuelve None (en vez de dar error),
    por eso podemos usarlo para "preguntar" si existe sin romper
    el programa.
    """
    contenido_variable = os.environ.get(NOMBRE_VARIABLE_ENTORNO)

    if contenido_variable:
        info = json.loads(contenido_variable)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = service_account.Credentials.from_service_account_file(ARCHIVO_LLAVE, scopes=SCOPES)
    return creds

def obtener_servicio():
    """
    Igual que antes: construye el objeto 'service' para hablar
    con la API de Sheets, pero ahora usando las credenciales de
    la cuenta de servicio.
    """
    creds = obtener_credenciales()
    service = build("sheets", "v4", credentials=creds)
    return service

if __name__ == "__main__":
    servicio = obtener_servicio()
    print("Autenticacion con cuenta de servicio exitosa.")
    


    