# JPP Backend

API en **FastAPI** que conecta con Athena y expone datos para la interfaz JPP.

---

## 🔧 Requisitos
- Python 3.11+
- Credenciales AWS con permisos para Athena y S3.

---

## ▶️ Ejecución local
1. Ir a la carpeta `backend`
2. Crear y activar un entorno virtual
3. Instalar dependencias con: pip install -r requirements.txt
4. Copiar `.env.sample` a `.env` y completar credenciales
5. Ejecutar: uvicorn app.main:app --reload

---

## 🌐 Endpoints
- GET /health → Verifica que la API esté activa
- GET /plants → Lista plantas desde Athena

---

## 📂 Estructura
backend/
├─ app/
│  ├─ main.py          # Inicializa FastAPI
│  ├─ config.py        # Configuración y .env
│  ├─ deps/athena.py   # Conexión Athena
│  ├─ routers/plants.py# Endpoint /plants
│  └─ schemas/plant.py # Modelo Pydantic para plantas
├─ requirements.txt
├─ .env.sample
└─ README.md


===== frontend/README.md =====
# JPP Frontend

Interfaz en **Streamlit** para el modelo JPP.

---

## 🔧 Requisitos
- Python 3.11+
- Backend de JPP corriendo localmente o en un servidor accesible.

---

## ▶️ Ejecución local
1. Ir a la carpeta `frontend`
2. Crear y activar un entorno virtual
3. Instalar dependencias con: pip install -r requirements.txt
4. Configurar la variable de entorno BACKEND_URL (ej: http://localhost:8000)
5. Ejecutar: streamlit run ui/app.py

Abrir en el navegador: http://localhost:8501

---

## 📂 Estructura
frontend/
├─ ui/
│  ├─ app.py               # UI principal
│  └─ assets/copec_logo.png
├─ requirements.txt
└─ README.md