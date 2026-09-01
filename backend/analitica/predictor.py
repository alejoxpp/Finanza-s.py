from __future__ import annotations

import numpy as np
import pandas as pd

try:
    from sklearn.linear_model import LinearRegression
except ImportError:
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


def predecir_gasto_proximo_mes(df: pd.DataFrame) -> dict:
    if df is None or df.empty:
        return {
            "prediccion": 0.0,
            "confianza": "baja",
            "meses_analizados": 0,
            "razon": "Sin datos de gastos para predecir.",
        }

    gastos = df[df["tipo"] == "gasto"].copy()
    if gastos.empty:
        return {
            "prediccion": 0.0,
            "confianza": "baja",
            "meses_analizados": 0,
            "razon": "No existen registros de gasto para este usuario.",
        }

    gastos["fecha"] = pd.to_datetime(gastos["fecha"])
    gastos["mes"] = gastos["fecha"].dt.to_period("M")
    resumen_mensual = gastos.groupby("mes", as_index=False)["monto"].sum()

    if len(resumen_mensual) < 2:
        promedio = float(resumen_mensual["monto"].mean()) if not resumen_mensual.empty else 0.0
        return {
            "prediccion": round(max(promedio, 0.0), 2),
            "confianza": "baja",
            "meses_analizados": int(len(resumen_mensual)),
            "razon": "Hay menos de 2 meses de historial, por lo que se usa el promedio simple.",
        }

    resumen_mensual["indice_mes"] = np.arange(len(resumen_mensual))
    X = resumen_mensual[["indice_mes"]].values
    y = resumen_mensual["monto"].values

    modelo = LinearRegression()
    modelo.fit(X, y)

    siguiente_mes = np.array([[len(resumen_mensual)]])
    prediccion = float(modelo.predict(siguiente_mes)[0])
    prediccion = max(prediccion, 0.0)

    if len(resumen_mensual) >= 6:
        confianza = "alta"
    elif len(resumen_mensual) >= 3:
        confianza = "media"
    else:
        confianza = "baja"

    ultimo_mes = resumen_mensual["mes"].iloc[-1]
    mes_estimado = str((ultimo_mes.to_timestamp() + pd.DateOffset(months=1)).to_period("M"))

    return {
        "prediccion": round(prediccion, 2),
        "confianza": confianza,
        "meses_analizados": int(len(resumen_mensual)),
        "mes_estimado": mes_estimado,
        "razon": "Predicción calculada con regresión lineal sobre la tendencia mensual de gastos.",
    }
