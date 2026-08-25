
# 📊 Aplicación Web de Finanzas Personales con Dashboard Analítico

> **Proyecto de Aula - Nivel Intermedio–Avanzado**  
> **Duración sugerida:** 4 semanas (16-20 horas de trabajo autónomo + acompañamiento en clase)  
> **Modalidad:** Individual o en parejas  

---

## 📋 Tabla de Contenidos
- [Presentación del Proyecto](#-presentación-del-proyecto)
- [Objetivos de Aprendizaje](#-objetivos-de-aprendizaje)
- [Arquitectura General](#-arquitectura-general)
- [Historias de Usuario](#-historias-de-usuario)
- [Requerimientos Funcionales y No Funcionales](#-requerimientos-funcionales-y-no-funcionales)
- [Modelo de Datos](#-modelo-de-datos)
- [Especificación de la API REST](#-especificación-de-la-api-rest)
- [Módulo Analítico y Machine Learning](#-módulo-analítico-y-machine-learning)
- [Interfaz de Usuario (Frontend)](#-interfaz-de-usuario-frontend)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Cronograma Sugerido](#-cronograma-sugerido)
- [Rúbrica de Evaluación](#-rúbrica-de-evaluación)
- [Retos Opcionales](#-retos-opcionales)

---

## 🎯 Presentación del Proyecto

Este proyecto consiste en el desarrollo de una aplicación web full-stack que permite a los usuarios registrar sus ingresos y gastos, obteniendo **información analítica avanzada y valor predictivo** sobre su comportamiento financiero. 

La plataforma permite visualizar métricas de ahorro, identificar las categorías de mayor consumo, analizar tendencias históricas mes a mes, predecir el gasto del siguiente periodo y detectar anomalías en los movimientos financieros.

### Competencias a Desarrollar:
1. **Desarrollo Frontend:** HTML5, CSS3, JavaScript Asíncrono (`fetch`), Chart.js.
2. **Desarrollo Backend / API REST:** Python (Flask o FastAPI), arquitectura por capas.
3. **Persistencia de Datos y Análisis:** MySQL (Modelo Entidad-Relación normalizado), Pandas y Scikit-learn.

---

## 🎓 Objetivos de Aprendizaje

Al completar este proyecto, el estudiante estará en capacidad de:
- Diseñar y normalizar un modelo de datos relacional (mínimo 3FN) en MySQL para un dominio real.
- Construir una API RESTful escalable en Python con manejo adecuado de verbos y códigos de estado HTTP.
- Consumir endpoints asíncronos desde la interfaz web usando `async/await` y `fetch API`.
- Implementar visualizaciones interactivas de datos dinámicos utilizando Chart.js.
- Procesar, estructurar y limpiar series temporales de datos usando **Pandas**.
- Desplegar modelos de Machine Learning (Regresión Lineal y detección de anomalías) con **Scikit-learn**.
- Documentar y sustentar un proyecto de software listo para integrar a un portafolio profesional.

---

## 🏗️ Arquitectura General

```text
[ Frontend: HTML/CSS/JS + Chart.js ]
              |  fetch() / JSON
              v
[ Backend/API: Python (Flask o FastAPI) ]
              |  mysql-connector-python / SQLAlchemy
              v
[ Base de Datos: MySQL ]
              |
              v
[ Módulo Analítico: Pandas + Scikit-learn ]
              |  (resultados en JSON)
              v
[ Frontend: Dashboard con gráficos ]
```

*El módulo analítico está integrado como parte de la API Backend (endpoints `/api/analitica`), respondiendo en tiempo real a las solicitudes del dashboard.*

---

## 👤 Historias de Usuario

> *"Como usuario de la aplicación, quiero registrar mis ingresos y gastos clasificados por categoría, para poder visualizar en un panel interactivo cuánto he ahorrado, en qué gasto más, recibir alertas sobre gastos inusualmente altos y consultar una proyección estimada de mis gastos para el próximo mes."*

---

## ⚙️ Requerimientos del Sistema

### Requerimientos Funcionales (RF)
| ID | Descripción |
|---|---|
| **RF01** | Permite crear un usuario (registro básico de usuario). |
| **RF02** | Crear, listar, editar y eliminar categorías (ej. Alimentación, Transporte, Salario). |
| **RF03** | Registrar movimientos (ingreso/gasto) con monto, fecha, categoría, descripción y tipo. |
| **RF04** | Listar movimientos de un usuario con filtros por rango de fechas y categoría. |
| **RF05** | Calcular y mostrar el total de ingresos, total de gastos y el balance neto (ahorro). |
| **RF06** | Mostrar gráfico de dona/pastel con la distribución de gastos por categoría. |
| **RF07** | Mostrar gráfico de líneas o barras con la tendencia de ingresos vs. gastos por mes. |
| **RF08** | Generar la **predicción del gasto del próximo mes** usando un modelo de regresión. |
| **RF09** | **Detectar anomalías** en consumos que se desvíen significativamente del patrón histórico. |
| **RF10** | Presentar los resultados del análisis predictivo y cuantitativo en el dashboard visual. |

### Requerimientos No Funcionales (RNF)
- **Estándar REST:** La API debe responder en formato JSON utilizando métodos HTTP adecuados (`GET`, `POST`, `PUT`, `DELETE`).
- **Arquitectura Limpia:** Código backend estructurado en capas (Rutas, Lógica de Negocio, Acceso a Datos).
- **Seguridad Básica:** Almacenamiento de contraseñas mediante hash seguro (ej. `bcrypt`).
- **Responsividad:** Interfaz limpia adaptada para dispositivos de escritorio y tablets.
- **Control de Versiones:** Repositorio Git organizado con mensajes de commit descriptivos.

---

## 🗄️ Modelo de Datos (MySQL)

### Diagrama Entidad-Relación
```text
usuarios (1) ----< (N) ingresos_gastos (N) >---- (1) categorias
```

### Script DDL de Creación
```sql
CREATE DATABASE IF NOT EXISTS finanzas_personales
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE finanzas_personales;

CREATE TABLE usuarios (
    id_usuario      INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    correo          VARCHAR(150) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    fecha_registro  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias (
    id_categoria    INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(50) NOT NULL,
    tipo            ENUM('ingreso', 'gasto') NOT NULL,
    id_usuario      INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE
);

CREATE TABLE ingresos_gastos (
    id_movimiento   INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario      INT NOT NULL,
    id_categoria    INT NOT NULL,
    tipo            ENUM('ingreso', 'gasto') NOT NULL,
    monto           DECIMAL(12,2) NOT NULL,
    fecha           DATE NOT NULL,
    descripcion     VARCHAR(255),
    fecha_creacion  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        ON DELETE RESTRICT
);

-- Índices optimizados para consultas del módulo analítico
CREATE INDEX idx_mov_usuario_fecha ON ingresos_gastos (id_usuario, fecha);
CREATE INDEX idx_mov_categoria ON ingresos_gastos (id_categoria);
```

### Datos de Prueba Iniciales (Seed Script)
```sql
INSERT INTO usuarios (nombre, correo, contrasena_hash)
VALUES ('Ana Torres', 'ana@example.com', '$2b$12$eImiTXuWVxfM37uY4JANjOL.88T9qqQadO03p863/H021.282.');

INSERT INTO categorias (nombre, tipo, id_usuario) VALUES
('Salario', 'ingreso', 1),
('Freelance', 'ingreso', 1),
('Alimentación', 'gasto', 1),
('Transporte', 'gasto', 1),
('Entretenimiento', 'gasto', 1),
('Salud', 'gasto', 1);

INSERT INTO ingresos_gastos (id_usuario, id_categoria, tipo, monto, fecha, descripcion) VALUES
(1, 1, 'ingreso', 2500000, '2026-06-01', 'Pago mensual'),
(1, 3, 'gasto', 320000, '2026-06-05', 'Mercado del mes'),
(1, 4, 'gasto', 90000,  '2026-06-07', 'Transporte semanal'),
(1, 5, 'gasto', 150000, '2026-06-10', 'Cine y salidas'),
(1, 1, 'ingreso', 2500000, '2026-07-01', 'Pago mensual'),
(1, 3, 'gasto', 300000, '2026-07-04', 'Mercado del mes'),
(1, 6, 'gasto', 800000, '2026-07-15', 'Consulta médica de urgencia'); -- Candidato a anomalía
```

---

## 🚀 Especificación de la API REST

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/usuarios` | Registrar un nuevo usuario |
| `POST` | `/api/categorias` | Crear una nueva categoría |
| `GET` | `/api/categorias?id_usuario=` | Obtener categorías asociadas a un usuario |
| `POST` | `/api/movimientos` | Registrar un nuevo ingreso o gasto |
| `GET` | `/api/movimientos?id_usuario=&desde=&hasta=&categoria=` | Consultar movimientos con filtros |
| `PUT` | `/api/movimientos/{id}` | Actualizar un movimiento existente |
| `DELETE` | `/api/movimientos/{id}` | Eliminar un movimiento por ID |
| `GET` | `/api/resumen?id_usuario=&mes=` | Obtener totales (Ingresos, Gastos, Balance) |
| `GET` | `/api/analitica/prediccion?id_usuario=` | Consultar predicción de gasto para el próximo mes |
| `GET` | `/api/analitica/anomalias?id_usuario=` | Obtener listado de movimientos anómalos |

### Ejemplos de Intercambio de Datos (JSON)

**Petición `POST /api/movimientos`**
```json
{
  "id_usuario": 1,
  "id_categoria": 3,
  "tipo": "gasto",
  "monto": 85000,
  "fecha": "2026-08-20",
  "descripcion": "Mercado quincenal"
}
```

**Respuesta `GET /api/analitica/prediccion`**
```json
{
  "id_usuario": 1,
  "prediccion_proximo_mes": 1180000,
  "metodo": "regresion_lineal",
  "confianza": "media",
  "detalle_por_categoria": {
    "Alimentación": 320000,
    "Transporte": 95000,
    "Entretenimiento": 140000
  }
}
```

---

## 🧠 Módulo Analítico & Machine Learning

El módulo analítico procesa los registros financieros utilizando **Pandas** y modelos de **Scikit-learn**:

1. **Predicción con Regresión Lineal:** Estima el gasto acumulado del siguiente mes entrenando un modelo lineal (`LinearRegression`) a partir de la tendencia temporal de los meses anteriores.
2. **Detección de Anomalías (Z-Score):** Evalúa las desviaciones estándar por categoría. Si un movimiento supera el umbral configurado ($|Z| > 2$), es marcado como una anomalía estadística.

```python
import pandas as pd
from sklearn.linear_model import LinearRegression

def predecir_gasto_proximo_mes(df):
    gastos = df[df['tipo'] == 'gasto']
    resumen_mensual = gastos.groupby('mes')['monto'].sum().reset_index()
    resumen_mensual['n_mes'] = range(len(resumen_mensual))

    X = resumen_mensual[['n_mes']]
    y = resumen_mensual['monto']

    modelo = LinearRegression()
    modelo.fit(X, y)

    siguiente = [[len(resumen_mensual)]]
    prediccion = modelo.predict(siguiente)[0]
    return round(prediccion, 2)

def detectar_anomalias(df, umbral_z=2):
    gastos = df[df['tipo'] == 'gasto'].copy()
    stats = gastos.groupby('id_categoria')['monto'].agg(['mean', 'std']).reset_index()
    gastos = gastos.merge(stats, on='id_categoria')
    gastos['z_score'] = (gastos['monto'] - gastos['mean']) / gastos['std']
    return gastos[gastos['z_score'].abs() > umbral_z]
```

---

## 🎨 Interfaz de Usuario (Frontend)

La interfaz incluye:
- **Panel Dashboard:** Tarjetas resumen (KPIs) con Total Ingresos, Total Gastos, Balance y Predicción del próximo mes.
- **Visualización Gráfica:** 
  - Gráfico en dona (`doughnut`) para distribución del gasto por categorías.
  - Gráfico de líneas (`line`) mostrando la comparación mensual de ingresos vs. gastos.
- **Gestión de Movimientos:** Formulario dinámico para nuevos registros y tabla editable interactiva.
- **Sección de Alertas:** Panel informativo destacando movimientos inusuales detectados por el backend.

---

## 📁 Estructura del Repositorio

```text
finanzas-personales/
├── backend/
├── rutas/
│   ├── auth.py
│   ├── movimientos.py
│   └── analitica.py
├── modelos/
│   └── database.py
├── analitica/
│   ├── predictor.py
│   └── anomalias.py
├── app.py
├── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js
│       └── charts.js
├── database/
│   ├── schema.sql
│   └── seed.sql
└── README.md
```

---

## 🛠️ Instalación y Configuración

### Pre-requisitos
- Python 3.9+
- MySQL Server 8.0+
- Git

### Pasos de Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/finanzas-personales.git
   cd finanzas-personales
   ```

2. **Configurar la base de datos:**
   Ejecuta los scripts DDL y DML en tu cliente de MySQL:
   ```bash
   mysql -u root -p < database/schema.sql
   mysql -u root -p < database/seed.sql
   ```

3. **Configurar el entorno Backend:**
   ```bash
   cd backend
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```
   *La API iniciará en `http://localhost:5000` (o `http://localhost:8000` según el framework).*

5. **Abrir el Frontend:**
   Abre el archivo `frontend/index.html` en tu navegador de preferencia o usa Live Server.

---

## 📅 Cronograma Sugerido (4 Semanas)

- **Semana 1:** Diseño de BD MySQL, carga de seeds y desarrollo inicial del API REST (CRUDs básicos).
- **Semana 2:** Construcción de interfaz Web y consumo asíncrono de endpoints mediante `fetch`.
- **Semana 3:** Integración del módulo analítico con Pandas y Scikit-learn (predicción y anomalías).
- **Semana 4:** Integración del Dashboard con Chart.js, refinamiento de UI, documentación y sustentación.

---

## 📊 Rúbrica de Evaluación (100 pts)

| Criterio | Puntos | Descripción |
|---|---|---|
| **Modelo de BD** | 15 pts | Normalización (3FN), llaves, índices y seed ampliado. |
| **API REST Backend** | 20 pts | Rutas implementadas, respuestas JSON y manejo de errores. |
| **Frontend & Integración** | 20 pts | UX/UI fluida, CRUD operativo y manejo de estados asíncronos. |
| **Módulo Analítico** | 25 pts | Correcta implementación de predicciones y anomalías con ML. |
| **Visualización (Chart.js)** | 10 pts | Integración de gráficos interactivos claros y responsivos. |
| **Documentación & Sustentación** | 10 pts | Calidad del README, comentarios y sustentación técnica. |

---

## 🌟 Retos Opcionales
- Autenticación mediante Json Web Tokens (JWT).
- Exportación de informes analíticos en formato PDF.
- Comparación de modelos (Regresión Lineal vs. Random Forest).
- Despliegue en la nube (Backend en Render/Railway, Frontend en Vercel/Netlify).
