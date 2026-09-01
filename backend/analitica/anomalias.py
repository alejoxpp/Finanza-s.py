from __future__ import annotations

import numpy as np
import pandas as pd


def detectar_anomalias(df: pd.DataFrame, umbral_z: float = 2.0) -> list:
    if df is None or df.empty:
        return []

    gastos = df[df["tipo"] == "gasto"].copy()
    if gastos.empty:
        return []

    gastos["fecha"] = pd.to_datetime(gastos["fecha"])
    gastos["monto"] = pd.to_numeric(gastos["monto"], errors="coerce").fillna(0)

    resumen_categoria = (
        gastos.groupby("id_categoria", as_index=False)["monto"]
        .agg(["mean", "std"])
        .rename(columns={"mean": "promedio", "std": "desviacion"})
        .reset_index(drop=True)
    )

    if resumen_categoria.empty:
        return []

    gastos = gastos.merge(resumen_categoria, on="id_categoria", how="left")
    gastos["desviacion"] = gastos["desviacion"].fillna(0)

    gastos["z_score"] = np.where(
        gastos["desviacion"] > 0,
        (gastos["monto"] - gastos["promedio"]) / gastos["desviacion"],
        0.0,
    )

    anomalias = gastos[np.abs(gastos["z_score"]) > umbral_z].copy()
    if anomalias.empty:
        return []

    resultado = []
    for _, row in anomalias.iterrows():
        resultado.append(
            {
                "id_movimiento": int(row["id_movimiento"]),
                "id_categoria": int(row["id_categoria"]),
                "categoria": row.get("categoria", "Sin nombre"),
                "fecha": row["fecha"].strftime("%Y-%m-%d"),
                "monto": round(float(row["monto"]), 2),
                "promedio_categoria": round(float(row["promedio"]), 2),
                "z_score": round(float(row["z_score"]), 2),
                "descripcion": row.get("descripcion", ""),
            }
        )

    return resultado
