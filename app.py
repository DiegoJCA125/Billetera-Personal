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
from main import (
    registrar_gasto,
    registrar_ingreso,
    calcular_balance,
    obtener_historial,
    editar_movimiento,
    eliminar_movimiento,
)

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


@app.route("/eliminar/<int:numero_fila>", methods=["POST"])
def eliminar(numero_fila):
    """
    <int:numero_fila> en la ruta es una "variable de URL": Flask
    toma lo que venga en esa parte de la dirección (ej. /eliminar/5)
    y lo convierte automáticamente a número entero, pasándolo como
    el parámetro numero_fila de esta función. Si alguien pusiera
    /eliminar/abc (texto en vez de número), Flask respondería con
    un error 404 automáticamente, sin que tengamos que validarlo
    nosotros a mano.
    """
    eliminar_movimiento(numero_fila)
    return redirect("/")


@app.route("/editar/<int:numero_fila>", methods=["GET"])
def mostrar_formulario_editar(numero_fila):
    """
    Muestra un formulario PRELLENADO con los datos actuales de ese
    movimiento, para que solo corrijas lo que necesites.

    methods=["GET"] (a diferencia de ["POST"]) porque aquí solo
    estamos "pidiendo ver" una página, no enviando datos todavía.

    Buscamos el movimiento específico dentro del historial completo
    comparando su fila_numero con el que viene en la URL.
    """
    historial = obtener_historial(limite=9999)
    movimiento = None
    for m in historial:
        if m["fila_numero"] == numero_fila:
            movimiento = m
            break

    if movimiento is None:
        return redirect("/")

    return render_template("editar.html", movimiento=movimiento)


@app.route("/editar/<int:numero_fila>", methods=["POST"])
def procesar_edicion(numero_fila):
    """
    Esta es la ruta que SÍ guarda los cambios, cuando envías el
    formulario de editar.html. Fíjate que la URL es la MISMA que la
    de arriba (/editar/<int:numero_fila>) pero el método es distinto
    (POST en vez de GET) — Flask usa ambas cosas juntas (URL + método)
    para decidir qué función ejecutar.
    """
    tipo = request.form["tipo"]
    categoria = request.form["categoria"]
    descripcion = request.form["descripcion"]
    monto = float(request.form["monto"])

    editar_movimiento(numero_fila, tipo, categoria, descripcion, monto)
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