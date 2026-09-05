"""
app.py
-------
Este archivo levanta un servidor web local usando Flask. La idea es
simple: en vez de escribir en la consola (input()), va a llenar un
formulario en tu navegador (o en el navegador de tu celular).
 
Concepto clave: rutas ("routes")
----------------------------------
Una "ruta" es una URL específica de tu sitio y qué función de Python
se ejecuta cuando alguien la visita. Por ejemplo:
- "/" (la página principal) -> ejecuta la función pagina_principal()
- "/registrar" -> ejecuta la función procesar_formulario()
 
Flask conecta URLs con funciones usando el decorador @app.route(...).
Un "decorador" es esa línea que empieza con @ justo encima de una
función: le agrega comportamiento extra sin que tengas que
modificar el código de la función misma.
"""

