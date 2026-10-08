"""
app.py
-------
Servidor Flask. Sin cambios en la autenticación ni en las rutas
existentes — solo se agrega /mensual al final.
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
    resumen_mensual,
    MESES,
    validar_movimiento,
)

app = Flask(__name__)
#LA APLICACION NO DEBE DE INICIAR CON CREDENCIALES PREDETERMINADOS
USUARIO_APP = os.environ.get("APP_USERNAME")
CONTRASENA_APP = os.environ.get("APP_PASSWORD")

#FALLA EXPLICITAMENTE SI FALTA ALGUN CREDENCIAL
if not USUARIO_APP or not CONTRASENA_APP:
    raise RuntimeError(
        "Debes configurar APP_USERNAME y APP_PASSWORD."
    )

def credenciales_validas(usuario, contrasena):
    return usuario == USUARIO_APP and contrasena == CONTRASENA_APP


def pedir_autenticacion():
    return Response(
        "Acceso restringido. Ingresa tu usuario y contraseña.",
        401,
        {"WWW-Authenticate": 'Basic realm="Billetera Personal"'},
    )


def requiere_login(funcion_vista):
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
    # OBTENEMOS LOS DATOS QUE VIENEN DEL FORMULARIO.
    tipo = request.form["tipo"]
    categoria = request.form["categoria"]
    descripcion = request.form["descripcion"]
    monto = request.form["monto"]

    try:
        # CONVERTIMOS EL MONTO A NÚMERO.
        # Si alguien escribe algo que no sea un número válido,
        # Python generará un ValueError.
        monto = float(monto)

        # VALIDAMOS TODOS LOS DATOS ANTES DE GUARDARLOS.
        validar_movimiento(
            tipo,
            categoria,
            descripcion,
            monto,
        )

        # SI TODO ES CORRECTO, GUARDAMOS EL MOVIMIENTO.
        if tipo == "Gasto":
            registrar_gasto(categoria, descripcion, monto)
        else:
            registrar_ingreso(categoria, descripcion, monto)

    except ValueError as error:
        # EN LUGAR DE MOSTRAR UN ERROR DE FLASK,
        # VOLVEMOS A LA PÁGINA PRINCIPAL Y LE ENVIAMOS
        # EL MENSAJE PARA MOSTRARLO EN LA INTERFAZ.
        ingresos, gastos, balance = calcular_balance()
        historial = obtener_historial(limite=10)

        return render_template(
            "index.html",
            ingresos=ingresos,
            gastos=gastos,
            balance=balance,
            historial=historial,
            error_validacion=str(error),
        )

    return redirect("/")


@app.route("/eliminar/<int:numero_fila>", methods=["POST"])
@requiere_login
def eliminar(numero_fila):
    eliminar_movimiento(numero_fila)
    return redirect("/")


@app.route("/editar/<int:numero_fila>", methods=["GET"])
@requiere_login
def mostrar_formulario_editar(numero_fila):
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
    tipo = request.form["tipo"]
    categoria = request.form["categoria"]
    descripcion = request.form["descripcion"]
    monto = float(request.form["monto"])

    editar_movimiento(numero_fila, tipo, categoria, descripcion, monto)
    return redirect("/")


@app.route("/graficas")
@requiere_login
def pagina_graficas():
    totales = gastos_por_categoria()
    categorias = list(totales.keys())
    montos = list(totales.values())

    return render_template(
        "graficas.html", categorias=categorias, montos=montos
    )


@app.route("/mensual")
@requiere_login
def pagina_mensual():
    """
    NUEVA ruta: trae resumen_mensual() de main.py (que a su vez viene
    de analytics.py) y arma 3 listas paralelas — etiquetas, ingresos,
    gastos y balances — en el mismo orden, que es justo lo que
    Chart.js necesita para dibujar un gráfico de líneas con 3 series.
    """
    datos = resumen_mensual()

    etiquetas = [f"{MESES[d['mes'] - 1][:3]} {d['anio']}" for d in datos]
    ingresos = [d["total_ingresos"] for d in datos]
    gastos = [d["total_gastos"] for d in datos]
    balances = [d["balance"] for d in datos]

    return render_template(
        "mensual.html",
        etiquetas=etiquetas,
        ingresos=ingresos,
        gastos=gastos,
        balances=balances,
    )


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=True)