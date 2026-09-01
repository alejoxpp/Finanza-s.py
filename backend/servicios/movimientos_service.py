from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text


def crear_movimiento(db: Session, id_usuario: int, id_categoria: int, tipo: str, monto: float, fecha: str, descripcion: str):
    tipo_limpio = tipo.lower()
    if tipo_limpio not in {"ingreso", "gasto"}:
        raise ValueError("El tipo debe ser 'ingreso' o 'gasto'")

    categoria = db.execute(
        text("SELECT id_categoria, tipo FROM categorias WHERE id_categoria = :id_categoria AND id_usuario = :id_usuario"),
        {"id_categoria": id_categoria, "id_usuario": id_usuario}
    ).fetchone()

    if not categoria:
        raise ValueError("La categoría no existe o no pertenece al usuario")
    if categoria[1] != tipo_limpio:
        raise ValueError("El tipo del movimiento no coincide con el tipo de la categoría")

    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        raise ValueError("La fecha debe tener formato YYYY-MM-DD")

    if monto <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    descripcion_limpia = descripcion.strip() if descripcion else ""

    db.execute(
        text("""
            INSERT INTO ingresos_gastos (id_usuario, id_categoria, tipo, monto, fecha, descripcion)
            VALUES (:id_usuario, :id_categoria, :tipo, :monto, :fecha, :descripcion)
        """),
        {
            "id_usuario": id_usuario,
            "id_categoria": id_categoria,
            "tipo": tipo_limpio,
            "monto": float(monto),
            "fecha": fecha_dt.date(),
            "descripcion": descripcion_limpia,
        }
    )
    db.commit()

    movimiento = db.execute(
        text("SELECT id_movimiento, id_usuario, id_categoria, tipo, monto, fecha, descripcion, fecha_creacion FROM ingresos_gastos WHERE id_usuario = :id_usuario ORDER BY id_movimiento DESC LIMIT 1"),
        {"id_usuario": id_usuario}
    ).fetchone()

    return {
        "id_movimiento": movimiento[0],
        "id_usuario": movimiento[1],
        "id_categoria": movimiento[2],
        "tipo": movimiento[3],
        "monto": float(movimiento[4]),
        "fecha": movimiento[5].strftime("%Y-%m-%d") if movimiento[5] else None,
        "descripcion": movimiento[6],
        "fecha_creacion": movimiento[7].strftime("%Y-%m-%d %H:%M:%S") if movimiento[7] else None,
    }


def listar_movimientos(db: Session, id_usuario: int, desde: str = None, hasta: str = None, categoria: int = None):
    query = """
        SELECT m.id_movimiento, m.id_categoria, c.nombre AS categoria, m.tipo, m.monto, m.fecha, m.descripcion
        FROM ingresos_gastos m
        INNER JOIN categorias c ON c.id_categoria = m.id_categoria
        WHERE m.id_usuario = :id_usuario
    """
    params = {"id_usuario": id_usuario}

    if desde:
        query += " AND m.fecha >= :desde"
        params["desde"] = desde
    if hasta:
        query += " AND m.fecha <= :hasta"
        params["hasta"] = hasta
    if categoria:
        query += " AND m.id_categoria = :categoria"
        params["categoria"] = categoria

    query += " ORDER BY m.fecha DESC, m.id_movimiento DESC"

    rows = db.execute(text(query), params).fetchall()

    return [
        {
            "id_movimiento": row[0],
            "id_categoria": row[1],
            "categoria": row[2],
            "tipo": row[3],
            "monto": float(row[4]),
            "fecha": row[5].strftime("%Y-%m-%d") if row[5] else None,
            "descripcion": row[6],
        }
        for row in rows
    ]


def editar_movimiento(db: Session, id_movimiento: int, id_usuario: int, id_categoria: int, tipo: str, monto: float, fecha: str, descripcion: str):
    movimiento_actual = db.execute(
        text("SELECT id_movimiento, id_categoria, tipo, monto, fecha FROM ingresos_gastos WHERE id_movimiento = :id_movimiento AND id_usuario = :id_usuario"),
        {"id_movimiento": id_movimiento, "id_usuario": id_usuario}
    ).fetchone()
    if not movimiento_actual:
        raise ValueError("El movimiento no existe o no pertenece al usuario")

    tipo_limpio = tipo.lower()
    if tipo_limpio not in {"ingreso", "gasto"}:
        raise ValueError("El tipo debe ser 'ingreso' o 'gasto'")

    categoria = db.execute(
        text("SELECT tipo FROM categorias WHERE id_categoria = :id_categoria AND id_usuario = :id_usuario"),
        {"id_categoria": id_categoria, "id_usuario": id_usuario}
    ).fetchone()
    if not categoria:
        raise ValueError("La categoría no existe o no pertenece al usuario")
    if categoria[0] != tipo_limpio:
        raise ValueError("El tipo del movimiento no coincide con el tipo de la categoría")

    try:
        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        raise ValueError("La fecha debe tener formato YYYY-MM-DD")

    if monto <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    db.execute(
        text("""
            UPDATE ingresos_gastos
            SET id_categoria = :id_categoria,
                tipo = :tipo,
                monto = :monto,
                fecha = :fecha,
                descripcion = :descripcion
            WHERE id_movimiento = :id_movimiento AND id_usuario = :id_usuario
        """),
        {
            "id_movimiento": id_movimiento,
            "id_usuario": id_usuario,
            "id_categoria": id_categoria,
            "tipo": tipo_limpio,
            "monto": float(monto),
            "fecha": fecha_dt.date(),
            "descripcion": (descripcion or "").strip(),
        }
    )
    db.commit()

    movimiento = db.execute(
        text("SELECT id_movimiento, id_usuario, id_categoria, tipo, monto, fecha, descripcion, fecha_creacion FROM ingresos_gastos WHERE id_movimiento = :id_movimiento AND id_usuario = :id_usuario"),
        {"id_movimiento": id_movimiento, "id_usuario": id_usuario}
    ).fetchone()

    return {
        "id_movimiento": movimiento[0],
        "id_usuario": movimiento[1],
        "id_categoria": movimiento[2],
        "tipo": movimiento[3],
        "monto": float(movimiento[4]),
        "fecha": movimiento[5].strftime("%Y-%m-%d") if movimiento[5] else None,
        "descripcion": movimiento[6],
        "fecha_creacion": movimiento[7].strftime("%Y-%m-%d %H:%M:%S") if movimiento[7] else None,
    }


def eliminar_movimiento(db: Session, id_movimiento: int, id_usuario: int):
    row = db.execute(
        text("DELETE FROM ingresos_gastos WHERE id_movimiento = :id_movimiento AND id_usuario = :id_usuario"),
        {"id_movimiento": id_movimiento, "id_usuario": id_usuario}
    )
    db.commit()
    return row.rowcount > 0
