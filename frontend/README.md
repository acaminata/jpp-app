# JPP Frontend

Interfaz en **Streamlit** para el Optimizador de Programación de Pedidos de Combustibles (JPP).
Este frontend consume el backend (FastAPI) para listar plantas y, en siguientes pasos, ejecutar escenarios de optimización.

---

## 🔧 Requisitos
- Python 3.11+
- Backend de JPP en ejecución y accesible (por defecto en http://localhost:8000)

---

## ▶️ Ejecución local
1. Ir a la carpeta `frontend`
2. Crear y activar un entorno virtual (Python 3.11+)
3. Instalar dependencias con: `pip install -r requirements.txt`
4. Definir la URL del backend en la variable de entorno `BACKEND_URL`
5. Ejecutar la aplicación con: `streamlit run ui/app.py`
6. Abrir en el navegador: http://localhost:8501

Notas de ejemplo para la variable de entorno:

- Windows PowerShell:
  - `$env:BACKEND_URL = "http://localhost:8000"`
- Windows CMD:
  - `set BACKEND_URL=http://localhost:8000`
- macOS / Linux (bash/zsh):
  - `export BACKEND_URL=http://localhost:8000`

---

## 📂 Estructura
frontend/
├─ ui/
│  ├─ app.py               # UI principal en Streamlit
│  └─ assets/
│     └─ copec_logo.png    # Logo utilizado en la cabecera
├─ requirements.txt
└─ README.md

---

## 🧪 Verificación rápida
- La portada debe mostrar el logo y el título de JPP.
- El selector de planta debe poblarse desde `GET /plants` del backend (usando `BACKEND_URL`).
- Si hay error de conexión, la página mostrará un mensaje de error.

---

## ❗ Solución de problemas
- Si no se cargan plantas:
  - Verifica que el backend esté corriendo en `http://localhost:8000/health`
  - Revisa `BACKEND_URL` y la conectividad de red
- Si Streamlit no abre el navegador:
  - Revisa el puerto 8501 no esté ocupado o cambia el puerto con `--server.port`

---

## 📌 Próximos incrementos
- Selector múltiple de EDS por planta
- Parámetros de escenario (flags de restricciones)
- Botón “Ejecutar optimización” y descarga del Excel generado