"""
app.py
-------
Este archivo levanta un servidor web local usando Flask. La idea es
simple: en vez de escribir en la consola (input()), vas a llenar un
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

import os
from flask import Flask, render_template, request, redirect
from main import registrar_gasto, registrar_ingreso, calcular_balance, obtener_historial

# Esto crea la aplicación Flask. __name__ le dice a Flask en qué
# archivo está corriendo, para que sepa dónde buscar plantillas HTML.
app = Flask(__name__)


@app.route("/")
def pagina_principal():
    """
    Se ejecuta cuando visitas la página principal (ej. localhost:5000).
    Calculamos el balance actual Y traemos el historial reciente,
    y le pasamos ambas cosas a la plantilla HTML.
    """
    ingresos, gastos, balance = calcular_balance()
    historial = obtener_historial(limite=10)
    return render_template(
        "index.html",
        ingresos=ingresos,
        gastos=gastos,
        balance=balance,
        historial=historial,
    )


@app.route("/registrar", methods=["POST"])
def procesar_formulario():
    """
    Se ejecuta SOLO cuando el formulario HTML envía sus datos (por
    eso methods=["POST"] — POST es el método que usan los formularios
    para "enviar" información, a diferencia de GET que es para "pedir"
    una página).

    request.form es un diccionario con lo que el usuario escribió en
    el formulario. Las llaves ("tipo", "categoria", etc.) deben
    coincidir EXACTAMENTE con el atributo "name" de cada campo en
    el HTML (eso lo vemos en el siguiente paso).
    """
    tipo = request.form["tipo"]
    categoria = request.form["categoria"]
    descripcion = request.form["descripcion"]
    monto = float(request.form["monto"])

    if tipo == "Gasto":
        registrar_gasto(categoria, descripcion, monto)
    else:
        registrar_ingreso(categoria, descripcion, monto)

    # redirect("/") manda al usuario de vuelta a la página principal
    # después de guardar. Esto evita un problema clásico: si alguien
    # refresca la página después de enviar un formulario, el navegador
    # podría reenviar el mismo dato sin querer y duplicarlo.
    return redirect("/")


# host="0.0.0.0" es LA CLAVE para que puedas entrar desde tu celular:
# significa "acepta conexiones desde cualquier dispositivo en la red",
# no solo desde esta misma PC. Sin esto, solo tú desde el navegador
# de tu propio computador podrías verlo.
#
# Render asigna su PROPIO número de puerto automáticamente y te lo
# entrega en una variable de entorno llamada "PORT". Con
# os.environ.get("PORT", 5000) le decimos: "si existe esa variable,
# úsala; si no existe (como en tu PC), usa 5000 como antes".
if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=True)