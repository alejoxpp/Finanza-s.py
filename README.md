# 💰 Finanza$.py Personales — Dashboard Analítico

> Aplicación web full-stack para registrar ingresos y gastos, visualizar tu comportamiento financiero y anticiparte a tus próximos gastos con Machine Learning.

**Descripción corta (para el campo "About" de GitHub):**
> App web full-stack de finanzas personales con dashboard analítico: registro de ingresos/gastos, predicción de gasto con regresión lineal y detección de anomalías con Scikit-learn.

---

## 📖 Sobre el proyecto

**Finanzas Personales** es una aplicación web que le permite a cualquier usuario registrar sus ingresos y gastos clasificados por categoría, y a cambio recibir información útil y accionable sobre su comportamiento financiero: cuánto está ahorrando, en qué categoría gasta más, cómo ha evolucionado su balance mes a mes, y una **proyección estadística de cuánto gastará el próximo mes**.

Lo que diferencia este proyecto de un CRUD tradicional es su **módulo analítico**, construido con Pandas y Scikit-learn, que procesa el histórico de movimientos del usuario para:

- 📈 **Predecir el gasto del próximo mes** mediante un modelo de regresión lineal entrenado sobre la tendencia mensual.
- 🚨 **Detectar anomalías**: identifica automáticamente movimientos que se desvían significativamente del comportamiento habitual del usuario en una categoría (por z-score), y los señala como alertas en el dashboard.

Todo el análisis se expone en tiempo real a través de una API REST y se visualiza en un dashboard interactivo con Chart.js.

## ✨ Funcionalidades principales

- 👤 Registro de usuario y gestión de categorías (ingreso/gasto)
- 💸 CRUD completo de movimientos financieros con filtros por fecha y categoría
- 📊 Cálculo automático de totales: ingresos, gastos y balance/ahorro
- 🍩 Gráfico de distribución de gastos por categoría
- 📉 Gráfico de tendencia de ingresos vs. gastos por mes
- 🔮 Predicción del gasto del próximo mes con Machine Learning
- ⚠️ Detección y alertas de movimientos anómalos
- 📱 Interfaz responsiva (escritorio y tablet)

## 🛠️ Tech Stack

| Capa | Tecnologías |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (fetch / async-await), Chart.js |
| **Backend / API** | Python (Flask o FastAPI), arquitectura por capas |
| **Base de datos** | MySQL (modelo relacional normalizado, 3FN) |
| **Análisis y ML** | Pandas, Scikit-learn (Regresión Lineal, detección de anomalías por z-score) |

## 🏗️ Arquitectura

```
Frontend (HTML/CSS/JS + Chart.js)
        │  fetch() / JSON
        ▼
Backend / API REST (Flask o FastAPI)
        │  mysql-connector-python / SQLAlchemy
        ▼
Base de datos (MySQL)
        │
        ▼
Módulo Analítico (Pandas + Scikit-learn)
        │  resultados en JSON
        ▼
Dashboard con gráficos interactivos
```

## 📂 Estructura del repositorio

```
finanzas-personales/
├── backend/
│   ├── rutas/          # auth.py, movimientos.py, analitica.py
│   ├── modelos/         # database.py
│   ├── analitica/       # predictor.py, anomalias.py
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/ (api.js, charts.js)
├── database/
│   ├── schema.sql
│   └── seed.sql
└── README.md
```

## 🚀 Estado del proyecto

Proyecto de aula en desarrollo — nivel intermedio-avanzado. Construido como pieza de portafolio para demostrar diseño de bases de datos relacionales, desarrollo de APIs REST, consumo asíncrono de datos y aplicación de Machine Learning a un dominio financiero real.

## 🏷️ Topics sugeridos para GitHub

`python` `flask` `fastapi` `mysql` `pandas` `scikit-learn` `machine-learning` `chartjs` `rest-api` `personal-finance` `dashboard` `full-stack`
