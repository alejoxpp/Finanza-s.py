from __future__ import annotations

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.analitica.anomalias import detectar_anomalias
from backend.analitica.predictor import predecir_gasto_proximo_mes


def obtener_historico_usuario(db: Session, id_usuario: int):
    rows = db.execute(
        text("""
            SELECT m.id_movimiento, m.id_categoria, c.nombre AS categoria, m.tipo, m.monto, m.fecha, m.descripcion
            FROM ingresos_gastos m
            INNER JOIN categorias c ON c.id_categoria = m.id_categoria
            WHERE m.id_usuario = :id_usuario
            ORDER BY m.fecha ASC
        """),
        {"id_usuario": id_usuario},
    ).fetchall()

    data = []
    for row in rows:
        data.append(
            {
                "id_movimiento": row[0],
                "id_categoria": row[1],
                "categoria": row[2],
                "tipo": row[3],
                "monto": float(row[4]),
                "fecha": row[5].strftime("%Y-%m-%d") if row[5] else None,
                "descripcion": row[6],
            }
        )

    return pd.DataFrame(data)


def resumen_usuario(db: Session, id_usuario: int, mes: str | None = None):
    if mes:
        query = """
            SELECT
                SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) AS total_ingresos,
                SUM(CASE WHEN tipo = 'gasto' THEN monto ELSE 0 END) AS total_gastos,
                SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE -monto END) AS balance
            FROM ingresos_gastos
            WHERE id_usuario = :id_usuario AND DATE_FORMAT(fecha, '%Y-%m') = :mes
        """
        params = {"id_usuario": id_usuario, "mes": mes}
    else:
        query = """
            SELECT
                SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) AS total_ingresos,
                SUM(CASE WHEN tipo = 'gasto' THEN monto ELSE 0 END) AS total_gastos,
                SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE -monto END) AS balance
            FROM ingresos_gastos
            WHERE id_usuario = :id_usuario
        """
        params = {"id_usuario": id_usuario}

    row = db.execute(text(query), params).fetchone()
    total_ingresos = float(row[0] or 0)
    total_gastos = float(row[1] or 0)
    balance = float(row[2] or 0)

    return {
        "total_ingresos": round(total_ingresos, 2),
        "total_gastos": round(total_gastos, 2),
        "balance": round(balance, 2),
        "ahorro_porcentaje": round((balance / total_ingresos * 100) if total_ingresos else 0.0, 2),
    }


def prediccion_usuario(db: Session, id_usuario: int):
    df = obtener_historico_usuario(db, id_usuario)
    return predecir_gasto_proximo_mes(df)


def anomalias_usuario(db: Session, id_usuario: int, umbral_z: float = 2.0):
    df = obtener_historico_usuario(db, id_usuario)
    return detectar_anomalias(df, umbral_z=umbral_z)


def insights_usuario(db: Session, id_usuario: int) -> dict:
    """Devuelve insight analíticos: categoría más costosa (mes e histórico) y
    tendencia mensual de ingresos/gastos/ahorro calculada con Pandas."""
    df = obtener_historico_usuario(db, id_usuario)

    if df is None or df.empty:
        return {
            "categoria_mas_costosa_mes": None,
            "categoria_mas_costosa_historico": None,
            "tendencia_mensual": [],
        }

    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    df["monto"] = pd.to_numeric(df["monto"], errors="coerce").fillna(0)

    gastos = df[df["tipo"] == "gasto"]

    # --- Histórico ---
    categoria_mas_costosa_historico = None
    if not gastos.empty:
        top_hist = (
            gastos.groupby("categoria", as_index=False)["monto"]
            .sum()
            .sort_values("monto", ascending=False)
            .iloc[0]
        )
        categoria_mas_costosa_historico = {
            "categoria": str(top_hist["categoria"]),
            "total": round(float(top_hist["monto"]), 2),
        }

    # --- Mes más reciente (o el que tenga el último movimiento de gasto) ---
    categoria_mas_costosa_mes = None
    if not gastos.empty:
        ultimo_mes = str(gastos["mes"].max())
        gastos_mes = gastos[gastos["mes"] == ultimo_mes]
        top_mes = (
            gastos_mes.groupby("categoria", as_index=False)["monto"]
            .sum()
            .sort_values("monto", ascending=False)
            .iloc[0]
        )
        categoria_mas_costosa_mes = {
            "mes": ultimo_mes,
            "categoria": str(top_mes["categoria"]),
            "total": round(float(top_mes["monto"]), 2),
        }

    # --- Tendencia mensual ---
    tabla_mes = (
        df.groupby(["mes", "tipo"], as_index=False)["monto"]
        .sum()
        .pivot(index="mes", columns="tipo", values="monto")
        .fillna(0)
        .reset_index()
    )

    tendencia_mensual = []
    for _, row in tabla_mes.iterrows():
        ingresos = float(row.get("ingreso", 0))
        gastos_m = float(row.get("gasto", 0))
        ahorro = ingresos - gastos_m
        tendencia_mensual.append(
            {
                "mes": row["mes"],
                "ingresos": round(ingresos, 2),
                "gastos": round(gastos_m, 2),
                "ahorro": round(ahorro, 2),
                "ahorro_porcentaje": round((ahorro / ingresos * 100) if ingresos else 0.0, 2),
            }
        )

    tendencia_mensual.sort(key=lambda item: item["mes"])

    return {
        "categoria_mas_costosa_mes": categoria_mas_costosa_mes,
        "categoria_mas_costosa_historico": categoria_mas_costosa_historico,
        "tendencia_mensual": tendencia_mensual,
    }
