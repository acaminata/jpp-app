# JPP Backend

API en **FastAPI** que conecta con Athena y expone datos para la interfaz JPP.

---

## 🔧 Requisitos
- Python 3.11+
- Credenciales AWS con permisos para Athena y S3.
- Variables de entorno: `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_ATHENA_OUTPUT`, `ATHENA_DATABASE`, `ATHENA_WORKGROUP`, `API_KEY`, `CORS_ALLOWED_ORIGINS`.
- Dependencias: ver `requirements.txt` (incluye `python-dotenv`, `pyathena`, `fastapi`, `uvicorn`).

---

## ▶️ Ejecución local
1. Ir a la carpeta `backend`
2. Crear y activar un entorno virtual
3. Instalar dependencias con:  
   ```bash
   pip install -r requirements.txt
   ```
4. Copiar `.env.sample` a `.env` y completar credenciales + API_KEY + CORS_ALLOWED_ORIGINS
5. Ejecutar con script:  
   ```powershell
   ./dev.ps1
   ```
   ó manualmente:  
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 🌐 Endpoints
- **GET /health** → Verifica que la API esté activa (requiere header `X-API-Key`).
- **GET /plants** → Lista plantas desde Athena.
- **GET /plant-stations?plant_id=1234** → Lista estaciones asociadas a una planta.

---

## 📂 Estructura
backend/
├─ app/
│  ├─ main.py            # Inicializa FastAPI + CORS + routers
│  ├─ config.py          # Configuración y .env
│  ├─ deps/
│  │  ├─ athena.py       # Conexión Athena
│  │  └─ auth.py         # Validación API Key
│  ├─ routers/
│  │  ├─ plants.py       # Endpoint /plants
│  │  └─ stations.py     # Endpoint /plant-stations
│  └─ schemas/
│     ├─ plant.py        # Modelo Pydantic Plant
│     └─ station.py      # Modelo Pydantic Station
├─ requirements.txt
├─ .env.sample
└─ README.md
