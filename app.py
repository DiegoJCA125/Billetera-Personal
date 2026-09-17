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
from functools import wraps
from flask import Flask, render_template, request, redirect, Response
from main import (
    registrar_gasto,
    registrar_ingreso,
    calcular_balance,
    obtener_historial,
    editar_movimiento,
    eliminar_movimiento,
    gastos_por_categoria,
)

# Esto crea la aplicación Flask. __name__ le dice a Flask en qué
# archivo está corriendo, para que sepa dónde buscar plantillas HTML.
app = Flask(__name__)


# --- Autenticación con usuario y contraseña ---
#
# Leemos el usuario/contraseña desde variables de entorno (nunca
# escritos directamente en el código), igual que hicimos con la
# llave de Google. Si no configuras nada, usa estos valores por
# defecto SOLO para que puedas probar localmente sin dolores de
# cabeza — pero en Render SIEMPRE vas a configurar los tuyos.
USUARIO_APP = os.environ.get("APP_USERNAME", "admin")
CONTRASENA_APP = os.environ.get("APP_PASSWORD", "cambiame123")


def credenciales_validas(usuario, contrasena):
    """Compara lo que escribió la persona contra lo configurado."""
    return usuario == USUARIO_APP and contrasena == CONTRASENA_APP


def pedir_autenticacion():
    """
    Devuelve una respuesta HTTP especial (código 401 "No autorizado")
    que hace que el navegador muestre automáticamente su cuadro
    nativo de "usuario y contraseña" — no tenemos que diseñar
    nosotros esa ventana, el navegador ya la trae integrada para
    este tipo de autenticación (se llama "HTTP Basic Auth").
    """
    return Response(
        "Acceso restringido. Ingresa tu usuario y contraseña.",
        401,
        {"WWW-Authenticate": 'Basic realm="Billetera Personal"'},
    )


def requiere_login(funcion_vista):
    """
    Este es un DECORADOR (por eso empieza con @ cuando lo usamos).
    Un decorador "envuelve" una función para agregarle comportamiento
    extra sin modificar su código interno.

    Aquí, antes de dejar que se ejecute cualquier ruta marcada con
    @requiere_login, primero revisamos si la persona ya mandó
    credenciales válidas (request.authorization). Si no las mandó,
    o están mal, cortamos ahí mismo con pedir_autenticacion() y la
    función original (funcion_vista) nunca llega a ejecutarse.

    @wraps(funcion_vista) es un detalle técnico necesario para que
    Flask no se confunda entre las distintas rutas decoradas — sin
    esto, Flask podría pensar que todas las rutas se llaman igual.
    """
    @wraps(funcion_vista)
    def funcion_envuelta(*args, **kwargs):
        auth = request.authorization
        if not auth or not credenciales_validas(auth.username, auth.password):
            return pedir_autenticacion()
        return funcion_vista(*args, **kwargs)
    return funcion_envuelta


@app.route("/")
@requiere_login
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
@requiere_login
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
@requiere_login
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
@requiere_login
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
@requiere_login
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


@app.route("/graficas")
@requiere_login
def pagina_graficas():
    """
    gastos_por_categoria() nos da un diccionario, ej:
    {"Comida": 150000, "Transporte": 80000}

    Pero Chart.js (la librería de JavaScript que dibuja la gráfica)
    espera los datos en DOS listas separadas: una de nombres (labels)
    y otra de números (data), en el mismo orden. Por eso las separamos
    aquí antes de pasarlas a la plantilla.

    list(diccionario.keys())   -> lista de las categorías
    list(diccionario.values()) -> lista de los montos, en ese mismo orden
    """
    totales = gastos_por_categoria()
    categorias = list(totales.keys())
    montos = list(totales.values())

    return render_template(
        "graficas.html", categorias=categorias, montos=montos
    )


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