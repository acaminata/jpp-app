# JPP App

Monorepo para el **Optimizador de Programación de Pedidos de Combustibles (JPP)** con dos componentes principales:

- **backend/** → API en **FastAPI** que conecta con Athena, expone datos de plantas y estaciones, e incluye endpoints de **telemetría**.
- **frontend/** → Interfaz en **Streamlit** que consume el backend para que usuarios no técnicos puedan explorar la información y preparar escenarios de optimización.

---

## 🚀 Cómo ejecutar localmente

### 1. Backend
1. Ir a la carpeta `backend`
2. Crear y activar un entorno virtual (Python 3.11+)
3. Instalar dependencias:  
   ```bash
   pip install -r requirements.txt
   ```
4. Copiar `.env.sample` a `.env` y completar credenciales + `API_KEY`
5. Ejecutar con:  
   ```bash
   uvicorn app.main:app --reload
   ```
   o usando el script de desarrollo (Windows PowerShell):  
   ```powershell
   ./dev.ps1
   ```

La API quedará disponible en: [http://localhost:8000](http://localhost:8000)

#### Endpoints principales
- **GET /health** → Verifica que la API esté activa (requiere header `X-API-Key`).
- **GET /plants** → Lista plantas disponibles desde Athena.
- **GET /plant-stations?plant_id=1234** → Lista estaciones asociadas a una planta.
- **GET /telemetry/summary?client_id=10080** → Resumen de capacidades por producto y lectura inicial estimada (últimos 3 domingos).

---

### 2. Frontend
1. Ir a la carpeta `frontend`
2. Crear y activar un entorno virtual (Python 3.11+)
3. Instalar dependencias:  
   ```bash
   pip install -r requirements.txt
   ```
4. Definir la variable de entorno `BACKEND_URL` (ejemplo: `http://localhost:8000`)
5. Ejecutar con:  
   ```bash
   streamlit run ui/app.py
   ```

Abrir en el navegador: [http://localhost:8501](http://localhost:8501)

#### Funcionalidades
- Selector de plantas desde el backend.
- Visualización de clientes/estaciones asociados.
- Modal **“Reajustar estación”** con:
  - Capacidades totales por producto
  - Lecturas iniciales promedio (últimos 3 domingos)
  - Número de tanques
  - Tabla de tanques con capacidad y stock inicial

---

## 📂 Estructura del proyecto
```
jpp-app/
├─ backend/     # API FastAPI
│  ├─ app/
│  │  ├─ main.py            # Inicializa FastAPI + routers
│  │  ├─ config.py          # Configuración y .env
│  │  ├─ deps/              # Dependencias (auth, Athena)
│  │  ├─ routers/           # Endpoints (plants, stations, telemetry)
│  │  └─ schemas/           # Modelos Pydantic
│  ├─ requirements.txt
│  ├─ .env.sample
│  └─ README.md
│
├─ frontend/    # UI Streamlit
│  ├─ ui/
│  │  ├─ app.py             # Aplicación principal
│  │  ├─ services/          # Cliente HTTP y cache
│  │  ├─ dialogs/           # Modales (ej: station_details)
│  │  ├─ components/        # Componentes UI reutilizables
│  │  └─ assets/            # Logo, estilos CSS, plantillas HTML
│  ├─ .streamlit/
│  │  └─ secrets.toml       # Configuración secreta (API_KEY, BACKEND_URL)
│  ├─ requirements.txt
│  └─ README.md
│
└─ README.md   # Este archivo
```

---

## 📌 Próximos incrementos
- Mejorar visualización en modales (sidebar/tab con KPIs).
- Filtros avanzados (zona, jefe de zona).
- Selector múltiple de estaciones.
- Parámetros de escenario y ejecución del optimizador con descarga en Excel.
