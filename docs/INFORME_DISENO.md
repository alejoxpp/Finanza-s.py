# Informe de diseño — Finanzas Personales

> Documento corto que justifica las decisiones de diseño de la base de datos y del módulo analítico, preparado para la sustentación oral (10-15 min).

---

## 1. Diseño de la base de datos (MySQL, 3FN**

### Modelo relacional

```
usuarios (1) —< (N) ingresos_gastos (N) >— (1) categorias
```

### Tablas

| Tabla | Columnas clave | Llaves/índices |
|---|---|---|
| `usuarios` | id_usuario (PK), nombre, correo (UNIQUE), contrasena_hash, fecha_registro | PK + índice único en `correo` |
| `categorias` | id_categoria (PK), id_usuario (FK), nombre, tipo (ENUM ingreso/gasto) | FK a usuarios; UNIQUE (id_usuario, nombre, tipo); índice (id_usuario, tipo) |
| `ingresos_gastos` | id_movimiento (PK), id_usuario (FK), id_categoria (FK), tipo, monto (DECIMAL(10,2), CHECK > 0), fecha, descripcion, fecha_creacion | FKs a usuarios y categorias; índices (id_usuario, fecha) y (id_categoria) para consultas analíticas |

### Decisiones y justificación

1. **3FN**: no hay dependencias transitivas ni parciales: cada tabla almacena datos de una sola entidad; el tipo (ingreso/gasto) se duplica en `ingresos_gastos` como desnormalización controlada — NO: en realidad se **valida con el tipo de la categoría** en la capa de servicios para garantizar consistencia (un gasto solo puede usar categorías de tipo `gasto`), manteniendo la integridad referencial sin violas 3FN.
2. **`DECIMAL(10,2)`** para montos: evita errores de redondeo de punto flotante en dinero; y `CHECK (monto > 0)` garantiza montos positivos a nivel de BD.
 .
3. **Índices analíticos**: `(id_usuario, fecha)` optimiza las consultas de tendencia/resumen por rango de fechas; `(id_categoria)` acelera el `groupby`/`join` del módulo de anomalías y del dona del dashboard.
4. **On delete**: `usuarios→categorias→ingresos_gastos` con `CASCADE` en usuario (bombear cuenta completa**, `RESTRICT` en categoría con movimientos (no se puede borrar una categoría usada** — protegemos el histórico financiero.
5. **Seed**: 3 usuarios × 6 meses (marzo–agosto 2025** con gastos mensuales crecientes y un **gasto atípico** (Servicios $1.400.000 el 2025-08-21** que será detectado como anomalía por z-score, para demostrar RF09 en la sustentación).
## 2. Módulo analítico (Pandas + Scikit-learn**

### Pipeline (endpoint `GET /api/analitica/insights`, `prediccion`, `anomalias`)

1. **Extracción**: `pandas.read_sql` style — en este proyecto se consulta con SQLAlchemy y se construye un `DataFrame` con el histórico del usuario (columnas: id_movimiento, id_categoria, categoria, tipo, monto, fecha, descripcion).
2. **Limpieza**: conversión de `fecha` a `datetime` con `pd.to_datetime`; montos a numérico con `pd.to_numeric(..., errors='coerce').fillna(0)` (nulos → 0 para no romper el modelo).
3. **Métricas**: `groupby` por mes y tipo para obtener la tendencia mensual (ingresos, gastos, ahorro, % ahorro**; `groupby` por categoría para la categoría más costosa del mes y del histórico.

4. **Predicción (RF08** — `mapper/predictor.py`: se agrupan los gastos por mes, se entrena `LinearRegression` con (índice de mes → gasto total mensual** y se predice el índice siguiente. 
   - **¿Por qué regresión lineal?** es el modelo más simple e interpretable para tendencias mono-varibles; suficiente para el dominio y explicable en la sustentación (pendiente = incremento mensual promedio**.
   - **Caso pocos datos**: si hay < 2 meses se usa el promedio simple; nunca falla (manejo explícito del caso límite que pide el plan).
5. **Anomalías (RF09** — `mapper/anomalias.py`: z-score por categoría. Para cada gasto: `z = (monto − promedio_categoría) / desviación_categoría`; si `|z| > umbral` (por defecto 2.0** se marca como anómalo.
   - **¿Por qué z-score y no IsolationForest?** z-score es determinista, interpretable (un gasto 3 veces la desviación típica de su categoría** y fácil de justificar; IsolationForest es más potente pero menos transparente en una sustentación de aula. El plan pedía z-score como primera opción y dejaba IsolationForest como alternativa.
 ello se documenta en el README.
6. **Respuesta JSON**: el resultado se serializa y se entrega al frontend para las tarjetas KPI, insights, gráficos y alertas.

---

##3. Preparación para la sustentación oral (10-15 min**

### Demo en vivo

1. Abrir la app (frontend + backend**, entrar con un usuario del seed (p. ej. Ana — `ana@email.com`**.
2. Registrar un **gasto** (p. ej. $150.000 en Alimentación hoy** y mostrar cómo el dashboard se actualiza: KPIs, dona, tendencia e insights.
3. Mostrar las **anomalías** detectadas (el gasto médico atípico del seed** explicando el cálculo del z-score con números concretos..
4. Explicar la **predicción**: mostrar la recta de regresión (meses → gasto**) y el valor proyectado para septiembre 2025; mencionar el nivel de confianza según el número de meses usados.


### Preguntas típicas esperadas

- **¿Por qué FastAPI?** — rendimiento async, validación automática con Pydantic, docs interactivas `/docs` gratuitas — ideal para una API REST y para sustentar.
 
- **¿Cómo validas que un movimiento pertenece al usuario?** — los servicios verifican que la categoría exista y pertenezca al `id_usuario` antes de insertar; y las consultas siempre filtran por `id_usuario`.
 
- **¿Qué pasa si el usuario no tiene datos?** — la app no falla: el predictor usa promedio simple o devuelve 0 con "confianza baja"; las anomalías devuelven lista vacía; los insights muestran "Registra movimientos para ver análisis"。