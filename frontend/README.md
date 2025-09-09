# JPP Frontend

Interfaz en **Streamlit** para el **Optimizador de Programación de Pedidos de Combustibles (JPP)**.  
Este frontend consume el backend (FastAPI) para listar plantas, visualizar clientes/estaciones asociadas y explorar información de telemetría por estación.

---

## 🔧 Requisitos
- **Python 3.11+**
- Backend de JPP en ejecución y accesible (por defecto en `http://localhost:8000`)

---

## ▶️ Ejecución local

1. Ir a la carpeta `frontend`
2. Crear y activar un entorno virtual (Python 3.11+)
3. Instalar dependencias con:

   ```bash
   pip install -r requirements.txt
   ```

4. Definir la URL del backend en la variable de entorno `BACKEND_URL`
5. Ejecutar la aplicación con:

   ```bash
   streamlit run ui/app.py
   ```

6. Abrir en el navegador: [http://localhost:8501](http://localhost:8501)

Ejemplos de configuración de `BACKEND_URL`:

- **Windows PowerShell**  
  ```powershell
  $env:BACKEND_URL = "http://localhost:8000"
  ```
- **Windows CMD**  
  ```cmd
  set BACKEND_URL=http://localhost:8000
  ```
- **macOS / Linux (bash/zsh)**  
  ```bash
  export BACKEND_URL=http://localhost:8000
  ```

---

## 📂 Estructura

```bash
frontend/
├─ ui/
│  ├─ app.py                 # UI principal de Streamlit
│  ├─ services/              # Cliente HTTP y funciones cacheadas
│  │  ├─ api.py
│  │  └─ data.py
│  ├─ dialogs/               # Diálogos modales
│  │  └─ station_details.py
│  ├─ components/            # Componentes reutilizables de UI
│  │  └─ station_card.py
│  ├─ utils/                 # Funciones auxiliares (formato, carga de assets)
│  │  ├─ formatting.py
│  │  └─ assets.py
│  └─ assets/
│     ├─ styles/             # Hojas de estilo CSS
│     │  └─ dialog.css
│     ├─ templates/          # Fragmentos HTML
│     │  └─ kpi_grid.html
│     └─ copec_logo.png      # Logo utilizado en la cabecera
├─ .streamlit/
│  └─ secrets.toml           # Variables sensibles (ej: API_KEY, BACKEND_URL opcional)
├─ requirements.txt
└─ README.md
```

---

## 🧪 Verificación rápida

- La portada debe mostrar el **logo** y el **título** de JPP.  
- El **selector de planta** debe poblarse desde `GET /plants` del backend (usando `BACKEND_URL`).  
- Al seleccionar una planta, deben cargarse las **estaciones asociadas** desde `GET /plant-stations`.  
- El botón **“Ver detalles”** de cada estación debe abrir un **diálogo modal** mostrando:
  - KPIs (Capacidad total, Stock inicial, #TKs)  
  - Tabla de tanques con capacidad y stock inicial (2 decimales)

---

## ❗ Solución de problemas

- **No se cargan plantas:**  
  - Verifica que el backend esté corriendo (`http://localhost:8000/health`)  
  - Confirma que `BACKEND_URL` esté definido correctamente  

- **Streamlit no abre en navegador:**  
  - Asegúrate de que el puerto `8501` esté libre  
  - Cambia el puerto con:  
    ```bash
    streamlit run ui/app.py --server.port 8502
    ```

---

## 📌 Próximos incrementos

- Filtros avanzados por zona o jefe de zona  
- Selector múltiple de estaciones  
- Parámetros de escenario (restricciones de optimización)  
- Botón **“Ejecutar optimización”** con descarga automática de Excel  
- Mejoras visuales y de navegación (sidebar, tabs)
