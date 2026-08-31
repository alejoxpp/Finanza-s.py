import pandas as pd
import numpy as np

try:
    from sklearn.linear_model import LinearRegression  # type: ignore[import-not-found]
except ImportError:  # Fallback para entornos sin scikit-learn instalado
    class LinearRegression:
        def fit(self, X, y):
            X = np.asarray(X, dtype=float)
            y = np.asarray(y, dtype=float)

            if X.ndim == 1:
                X = X.reshape(-1, 1)

            X_design = np.column_stack([np.ones(len(X)), X])
            coef, _, _, _ = np.linalg.lstsq(X_design, y, rcond=None)

            self.intercept_ = coef[0]
            self.coef_ = coef[1:]
            return self

        def predict(self, X):
            X = np.asarray(X, dtype=float)
            if X.ndim == 1:
                X = X.reshape(-1, 1)
            return self.intercept_ + X @ self.coef_


def cargar_datos(conexion, id_usuario: int) -> pd.DataFrame:
    query = """
        SELECT fecha, tipo, monto, id_categoria
        FROM ingresos_gastos
        WHERE id_usuario = %s
    """
    df = pd.read_sql(query, conexion, params=(id_usuario,))
    if not df.empty:
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['mes'] = df['fecha'].dt.to_period('M')
        df['monto'] = df['monto'].astype(float)
    return df

def predecir_gasto_proximo_mes(df: pd.DataFrame) -> dict:
    gastos = df[df['tipo'] == 'gasto']
    if gastos.empty:
        return {"prediccion": 0.0, "confianza": "baja", "razon": "Sin registros de gastos"}

    resumen_mensual = gastos.groupby('mes')['monto'].sum().reset_index()
    cant_meses = len(resumen_mensual)

    # Manejo de bordes: Pocos datos históricos
    if cant_meses < 2:
        promedio = resumen_mensual['monto'].mean()
        return {
            "prediccion": round(float(promedio), 2),
            "confianza": "baja",
            "razon": "Datos insuficientes (<2 meses). Se usó promedio simple."
        }

    resumen_mensual['n_mes'] = range(cant_meses)
    X = resumen_mensual[['n_mes']]
    y = resumen_mensual['monto']

    modelo = LinearRegression()
    modelo.fit(X, y)

    siguiente_mes_idx = np.array([[cant_meses]])
    prediccion = modelo.predict(siguiente_mes_idx)[0]
    prediccion_final = max(0.0, float(prediccion))  # Evitar predicciones negativas

    confianza = "alta" if cant_meses >= 6 else "media"

    return {
        "prediccion": round(prediccion_final, 2),
        "confianza": confianza,
        "razon": f"Calculado con Regresión Lineal ({cant_meses} meses procesados)"
    }

def detectar_anomalias(df: pd.DataFrame, umbral_z: float = 1.5) -> list:
    gastos = df[df['tipo'] == 'gasto'].copy()
    if gastos.empty:
        return []

    # Agrupar por categoría
    stats = gastos.groupby('id_categoria')['monto'].agg(['mean', 'std']).reset_index()
    # Categorías con un solo gasto tendrán std=NaN. Reemplazamos NaN por 0
    stats['std'] = stats['std'].fillna(0)

    gastos = gastos.merge(stats, on='id_categoria')
    
    # Calcular Z-score sin dividir por cero
    gastos['z_score'] = np.where(
        gastos['std'] > 0,
        (gastos['monto'] - gastos['mean']) / gastos['std'],
        0
    )

    anomalias = gastos[gastos['z_score'].abs() > umbral_z]
    
    resultado = []
    for _, row in anomalias.iterrows():
        resultado.append({
            "fecha": row['fecha'].strftime('%Y-%m-%d'),
            "id_categoria": int(row['id_categoria']),
            "monto": float(row['monto']),
            "promedio_categoria": float(row['mean']),
            "z_score": round(float(row['z_score']), 2)
        })
    return resultado