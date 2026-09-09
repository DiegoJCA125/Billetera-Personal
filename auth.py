"""
OAuth2 ES EL PROTOCO QUE USA GOOGLE PARA DAR ACCESO A UNA APP SIN NECESIDAD DE DARLE UN CONTRASEÑA

1. El script abre una ventana del navegador.
2. inicia sesión y acepta los permisos ("esta app quiere leer/
   escribir en el Sheets").
3. Google entrega al script un "token" (una llave temporal).
4. Ese token se guarda en un archivo (token.json) para que la
   PRÓXIMA vez no tenga que volver a aceptar en el navegador.
"""
# LIBRERIAS QUE SE INSTALAN
from google.oauth2 import service_account
from googleapiclient.discovery import build

# SCOPES DEFINE QUE PUEDE HACER EN LA PP EN UNA LISTA DE PERMISOS
# SE PEDIRA PERMISOS PARA LEER Y ESCRIBIR EN EL SHEETS
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# NOMBRE DEL ARCHIVO DE LA LLAVE DE LA CUENTA DEL SERVICIO
ARCHIVO_LLAVE = "service_account.json"

def obtener_credenciales():
    """
    Carga las credenciales directamente desde el archivo JSON de
    la cuenta de servicio. No hay navegador, no hay token que
    guardar ni refrescar: cada vez que se llama a esta función,
    genera credenciales válidas al instante a partir de la llave.
    """
    creds = service_account.Credentials.from_service_account_file(
        ARCHIVO_LLAVE, scopes=SCOPES
    )
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
    


    