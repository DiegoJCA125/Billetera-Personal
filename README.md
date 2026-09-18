# 💰 Billetera Personal

Aplicación web para el control de finanzas personales, construida como proyecto de aprendizaje de Data Engineering. Permite registrar ingresos y gastos desde el celular o el computador, con los datos almacenados en tiempo real en Google Sheets.

🔗 **Demo en vivo:** https://portafolio-dataengineering.onrender.com/
*(protegido con usuario y contraseña — contáctame si quieres una demo)*

## ✨ Funcionalidades

- Registro de gastos e ingresos por categoría
- Cálculo automático de balance (ingresos - gastos)
- Historial de los últimos movimientos
- Edición y eliminación de registros
- Gráfica de gastos por categoría (Chart.js)
- Autenticación con usuario y contraseña
- Diseño responsive, usable desde el celular
- Datos almacenados en Google Sheets (accesibles y editables también desde ahí)

## 🛠️ Stack técnico

| Capa | Tecnología |
|---|---|
| Backend | Python, Flask |
| Almacenamiento | Google Sheets API (vía Service Account) |
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
  main.py (lógica de negocio)
        │
        ▼
  sheets.py (API de Google Sheets)
        │
        ▼
  auth.py (autenticación con Google:
           Service Account en producción,
           credenciales locales en desarrollo)
        │
        ▼
   Google Sheets (base de datos)
```

El proyecto sigue el principio de **separación de responsabilidades**: cada archivo tiene una sola tarea.

- `auth.py` → autenticación con la API de Google
- `sheets.py` → operaciones directas sobre la hoja de cálculo (leer, agregar, editar, borrar filas)
- `main.py` → reglas de negocio (qué es un gasto, cómo se calcula el balance, cómo se agrupan las categorías)
- `app.py` → servidor web e interfaz de usuario

## 🔒 Seguridad

- Las credenciales de Google (Service Account) y las contraseñas de la app se manejan mediante **variables de entorno**, nunca quedan escritas en el código ni se suben al repositorio (ver `.gitignore`).
- Todas las rutas que exponen o modifican datos requieren autenticación (`@requiere_login`).

## 🚀 Cómo correrlo localmente

1. Clona el repositorio y entra a la carpeta `BilleteraPersonal`.
2. Crea un entorno virtual e instala las dependencias:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Crea una cuenta de servicio de Google Cloud con acceso a la Google Sheets API, comparte tu hoja de cálculo con su correo, y guarda la llave como `service_account.json` en la raíz del proyecto.
4. Define las variables de entorno de autenticación:
   ```powershell
   $env:APP_USERNAME="tu_usuario"
   $env:APP_PASSWORD="tu_contraseña"
   ```
5. Corre la aplicación:
   ```bash
   python app.py
   ```
6. Abre `http://localhost:5000` en tu navegador.

## 📚 Qué aprendí construyendo esto

- Autenticación OAuth2 y migración a Service Accounts para entornos de producción
- Consumo de APIs REST de Google (Sheets) desde Python
- Desarrollo web con Flask: rutas, plantillas Jinja2, formularios GET/POST
- Manejo seguro de credenciales con variables de entorno
- Despliegue de aplicaciones Python en la nube (Render, gunicorn, Procfile)
- Visualización de datos con Chart.js
- Buenas prácticas de control de versiones con Git (commits pequeños y frecuentes)

## 🔮 Posibles mejoras futuras

- Filtros de historial por fecha o categoría
- Exportar reportes mensuales en PDF
- Notificaciones cuando el gasto mensual supere cierto límite
- Multi-usuario (cada persona con su propia hoja)

---

Proyecto desarrollado como parte de mi ruta de aprendizaje en Data Engineering.
