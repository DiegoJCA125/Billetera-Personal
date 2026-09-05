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
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

# SCOPES DEFINE QUE PUEDE HACER EN LA PP EN UNA LISTA DE PERMISOS
# SE PEDIRA PERMISOS PARA LEER Y ESCRIBIR EN EL SHEETS
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def obtener_credenciales():
    """
    Devuelve un objeto 'Credentials' valido listo para usar en las llamadas a la API de sheets
    Si existe un token guardado en un sesion anterior , lo que hara es que lo cargara y lo reutilizara
    Si existe pero ya se vencio o expiro, lo refrescra automaticamenta
    Si no existe el token, abrira el navehador para que se acepten los permisos por primera vez y lo guardara
    """
    creds = None

    # 1 REVISA SI YA SE CUENTA CON UN TOKEN GUARDADO
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # 2 Y 3 SI NO HAY TOKEN VALIDO, CONSEGUIRA UNO
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Si el token existe per vencio, se renovara sin abrir el navegadoir
            creds.refresh(Request())
        else:
            # si no hay token, realizara el flujo completo, abrira el navegadr y pedira permisos
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as archivo_token:
            archivo_token.write(creds.to_json())
    return creds

if __name__ == "__main__":
    credenciales = obtener_credenciales()
    print("Autenticacion exitosa. Se creo / actualizo token.json")

    