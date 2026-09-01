# 💰 Finanza$.py Personales—Dashboard Analítico

> Aplicación web full-stack para registrar ingresos y gastos, visualizar tu comportamiento financiero y anticiparte a tus próximos gastos con Machine Learning.

**Descripción corta (para el campo "About" de GitHub):**
> App web full-stack de finanzas personales con dashboard analítico: registro de ingresos/gastos, predicción de gasto con regresión lineal y detección de anomalías con Scikit-learn.



---

## 📖 Sobre el proyecto

**Finanzas Personales** es una aplicación web que permite a cualquier usuario registrar sus ingresos y gastos clasificados por categoría, y a cambio recibir información útil y accionable sobre su comportamiento financiero: cuánto está ahorrando, en qué categoría gasta más, cómo ha evolucionado su balance mes a mes, y una **proyección estadística de cuánto gastará el próximo mes**.

Lo que diferencia este proyecto de un CRUD tradicional es su **módulo analítico**, construido con Pandas y Scikit-learn, que procesa el histórico de movimientos del usuario para:

- 📈 **Predecir el gasto del próximo mes** mediante regresión lineal sobre la tendencia mensual.
- 🚨 **Detectar anomalías**: identifica movimientos que se desvían significativamente del patrón histórico por categoría (z-score, umbral `|z| > 2`), y los muestra como alertas en el dashboard.



---

## ✨ Funcionalidades

- 👤 Registro de usuarios e inicio de sesión (selectory)
- 🏷️ CRUD completo de categorías (ingreso/gasto)
- 💸 CRUD completo de movimientos con filtros por rango de fechas y categoría
- 📊 Totales: ingresos, gastos, balance/ahorro y % de ahorro
- 🍩 Gráfico dona de distribución del gasto por categoría
- 📉 Gráfico de líneas: ingresos vs. gastos por mes (tendencia dinámica desde el backend)
- 🔮 Predicción del gasto del próximo mes con Machine Learning
- ⚠️ Alertas de movimientos anómalos (z-score)
- 🧠 Insights: categoría más costosa del mes y del histórico, % ahorro mensual
- 📱 Interfaz responsiva (escritorio y tablet), con estados de carga y manejo de errores



---

## 🛠️ Tech Stack

| Capa | Tecnologías |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (fetch/async-await), Chart.js |
| **Backend / API** | Python + FastAPI (arquitectura por capas: rutas / servicios / datos). |
| **Base de datos** | MySQL (modelo relacional normalizado, 3FN) |
| **Análisis y ML** | Pandas, Scikit-learn (Regresión Lineal, detección de anomalías por z-score) |

---

## 🚀 Instalación y ejecución

### 1) Requisitos previos

- Python 3.10+ instalado
- MySQL 8+ instalado y corriendo

###2) Base de datos

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

> El `seed.sql` crea 3 usuarios con 6 meses de histórico (marzo–agosto 2025** e incluye un gasto atípico de $1.400.000 (categoría Servicios, usuario 1** como candidato a anomalía.



###3) Backend (API REST)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows
# .venv/bin/activate               # Linux/macOS
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y ajusta tus credenciales:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=finanzas_personales
```

Ejecuta el servidor:

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

La API queda disponible en `http://127.0.0.1:8000` (docs interactivas en `/docs`).
### 4) Frontend

Abre `frontend/index.html` en tu navegador (o sirve la carpeta con cualquier servidor estática):

```bash
python -m http.server 8080 --directory frontend
```

y abre `http://localhost:8080/index.html`. Selecciona un usuario desde la pantalla de inicio (o regístrate). El frontend llama a la API en `http://127.0.0.1:8000`.

---

## 🏗️ Estructura del repositorio

```
finanzas-personales/
├── backend/
│   ├── rutas/            auth.py, movimientos.py, categorias.py, analitica.py
│   ├── servicios/        usuarios, categorias, movimientos, analitica_service.py+ backend/)   # placeholder
│   ├── analitica/       predictor.py (regresión lineal), anomalias.py (z-score)
│   ├── modelos/         database.py (SQLAlchemy + conexión MySQL)
│   ├── app.py            (FastAPI, CORS, routers)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js        (fetch/async-await, Chart.js, validación JS)
├── database/
│   ├── schema.sql        (3FN, FKs, índices)
│   └── seed.sql          (3 usuarios, 6 meses, anomalía incluida)
├── docs/
│   └── INFORME_DISENO.md   (decisiones de BD y modelo analítico）
├── .env.example
├── .gitignore
└── README.md
```

---

## 🧠 Cómo funciona el módulo analítico

1. **Extracción**: el histórico del usuario se consulta con SQL vía SQLAlchemy.
2. **Limpieza**: pandas convierte `fecha` a `datetime` y valida montos numericos.
3. **Métricas**: % ahorro mensual,, categoría más costosa (mes/histórico), tendencia mensual (`groupby` por mes).
4. **Predicción**: `LinearRegression` de scikit-learn entrenada con (índice de mes → gasto total mensual**; predice el índice siguiente. Con < 2 meses usa promedio simple (sin fallar**.
5. **Anomalías**: z-score por categoría; umbral configurable |z| > 2 (por defecto**; como alternativa el plan sugiere `IsolationForest`.

---

## ✅ Cobertura de requerimientos (RF/RNF)

| ID | Estado | Cómo se cubre |
|---|---|---|
| RF01 | ✅ | `POST /api/usuarios` + pantalla de registro/login en el frontend |
| RF02 | ✅ | CRUD completo `/api/categorias` + vista "Categorías" |
| RF03 | ✅ | `POST /api/movimientos` + modal con validación JS |
| RF04 | ✅ | `GET /api/movimientos` con filtros `desde`, `hasta`, `categoria` + tabla y formulario de filtros |
| RF05 | ✅ | `GET /api/resumen` (totales, balance, % ahorro** + tarjetas KPI |
| RF06 | ✅ | Chart.js `doughnut` con gasto por categoría |
| RF07 | ✅ | Chart.js `line` ingresos vs gastos por mes (datos dinámicos desde `/api/analitica/insights`) |
| RF08 | ✅ | `GET /api/analitica/prediccion` (LinearRegression,** mostrado en KPI e insights |
| RF09 | ✅ | `GET /api/analitica/anomalias` (z-score,** alertas en el dashboard |
| RF10 | ✅ | Resultados de predicción y anomalías presentados visualmente (tarjeta, insights, alertas) |

RNF: API JSON con códigos de estado REST ✔· backend por capas ✔· contraseñas con bcrypt ✔· frontend responsivo ✔· repo Git con commits descriptivos ✔· README ✔· informe en `docs/` ✔.

---

## 🏷️ Topics sugeridos para GitHub

`python` `fastapi` `mysql` `pandas` `scikit-learn` `machine-learning` `chartjs` `rest-api` `personal-finance` `dashboard` `full-stack`