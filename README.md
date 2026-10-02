# 💰 Billetera Personal

Aplicación web para el control de finanzas personales, construida como proyecto de aprendizaje de Data Engineering. Permite registrar ingresos y gastos desde el celular o el computador, con los datos almacenados en PostgreSQL.

🔗 **Demo en vivo:** https://portafolio-dataengineering.onrender.com/
*(protegido con usuario y contraseña — contáctame si quieres una demo)*

## ✨ Funcionalidades

- Registro de gastos e ingresos por categoría
- Cálculo automático de balance (ingresos - gastos)
- Historial de los últimos movimientos
- Edición y eliminación de registros
- Gráfica de gastos por categoría (Chart.js)
- **Resumen financiero mensual**, con evolución de ingresos/gastos/balance mes a mes
- Autenticación con usuario y contraseña
- Diseño responsive, usable desde el celular

## 🛠️ Stack técnico

| Capa | Tecnología |
|---|---|
| Backend | Python, Flask |
| Almacenamiento | PostgreSQL |
| Frontend | HTML, CSS, Jinja2, Chart.js |
| Autenticación | HTTP Basic Auth |
| Despliegue | Render (gunicorn) |
| Control de versiones | Git / GitHub |

## 🏗️ Arquitectura

```
Navegador (celular o PC)
        │
        ▼
   Flask (app.py)  ──── HTTP Basic Auth
        │
        ▼
  main.py (lógica de negocio: registrar, editar, eliminar)
        │
        ├──▶ db.py (operaciones CRUD sobre PostgreSQL)
        │
        └──▶ analytics.py (TODO cálculo/análisis: balance,
                            gastos por categoría, resumen mensual)
        │
        ▼
   PostgreSQL (base de datos)
```

El proyecto separa responsabilidades en 3 capas con una regla estricta:

- `db.py` → únicamente operaciones CRUD (crear, leer, actualizar, borrar filas)
- `analytics.py` → únicamente cálculos y análisis sobre los datos (balance, totales por categoría, resumen mensual). Ningún cálculo vive fuera de este archivo.
- `main.py` → reglas de negocio, conecta ambas capas y expone una sola interfaz limpia a `app.py`
- `app.py` → servidor web e interfaz de usuario

> **Nota de evolución:** el proyecto empezó usando Google Sheets como almacenamiento (ver historial de commits). Se migró a PostgreSQL para ganar robustez, validaciones de datos reales (tipos, restricciones) y capacidad real de análisis con SQL (`GROUP BY`, `EXTRACT`, agregaciones).

## 🔒 Seguridad

- Las credenciales de la base de datos y las contraseñas de la app se manejan mediante **variables de entorno**, nunca quedan escritas en el código ni se suben al repositorio.
- Todas las rutas que exponen o modifican datos requieren autenticación (`@requiere_login`).

## 🚀 Cómo correrlo localmente

1. Clona el repositorio e instala las dependencias:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Crea una base de datos PostgreSQL local y corre `schema.sql` para crear la tabla `movimientos`.
3. Define las variables de entorno:
   ```powershell
   $env:DATABASE_URL="postgresql://usuario:contraseña@localhost:5432/tu_base_de_datos"
   $env:APP_USERNAME="tu_usuario"
   $env:APP_PASSWORD="tu_contraseña"
   ```
4. Corre la aplicación:
   ```bash
   python app.py
   ```
5. Abre `http://localhost:5000` en tu navegador.

## 📚 Qué aprendí construyendo esto

- Diseño de schemas SQL con restricciones reales (`CHECK`, `NOT NULL`, tipos de datos)
- Consultas de agregación (`SUM`, `GROUP BY`, `EXTRACT`) para análisis financiero
- Separación estricta de responsabilidades: CRUD vs. análisis vs. lógica de negocio
- Migración de datos entre sistemas de almacenamiento distintos sin perder historial
- Desarrollo web con Flask: rutas, plantillas Jinja2, formularios GET/POST
- Manejo seguro de credenciales con variables de entorno
- Despliegue de aplicaciones Python en la nube (Render, gunicorn)
- Visualización de datos con Chart.js (gráficas de categoría y de evolución temporal)

## 🔮 Posibles mejoras futuras

- Filtros de historial por fecha o categoría
- Exportar reportes mensuales en PDF
- Notificaciones cuando el gasto mensual supere cierto límite
- Multi-usuario (cada persona con sus propios datos)

---

Proyecto desarrollado como parte de mi ruta de aprendizaje en Data Engineering.