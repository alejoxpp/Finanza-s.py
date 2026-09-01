from sqlalchemy.orm import Session
from sqlalchemy import text


def crear_categoria(db: Session, id_usuario: int, nombre: str, tipo: str):
    nombre_limpio = nombre.strip()
    tipo_limpio = tipo.lower()

    if not nombre_limpio:
        raise ValueError("El nombre de la categoría es obligatorio")
    if tipo_limpio not in {"ingreso", "gasto"}:
        raise ValueError("El tipo debe ser 'ingreso' o 'gasto'")

    existe = db.execute(
        text("SELECT id_categoria FROM categorias WHERE id_usuario = :id_usuario AND nombre = :nombre AND tipo = :tipo"),
        {"id_usuario": id_usuario, "nombre": nombre_limpio, "tipo": tipo_limpio}
    ).fetchone()
    if existe:
        raise ValueError("La categoría ya existe para este usuario")

    db.execute(
        text("""
            INSERT INTO categorias (id_usuario, nombre, tipo)
            VALUES (:id_usuario, :nombre, :tipo)
        """),
        {"id_usuario": id_usuario, "nombre": nombre_limpio, "tipo": tipo_limpio}
    )
    db.commit()

    categoria = db.execute(
        text("SELECT id_categoria, id_usuario, nombre, tipo FROM categorias WHERE id_usuario = :id_usuario AND nombre = :nombre AND tipo = :tipo ORDER BY id_categoria DESC LIMIT 1"),
        {"id_usuario": id_usuario, "nombre": nombre_limpio, "tipo": tipo_limpio}
    ).fetchone()

    return {
        "id_categoria": categoria[0],
        "id_usuario": categoria[1],
        "nombre": categoria[2],
        "tipo": categoria[3],
    }


def listar_categorias(db: Session, id_usuario: int):
    rows = db.execute(
        text("SELECT id_categoria, nombre, tipo FROM categorias WHERE id_usuario = :id_usuario ORDER BY tipo, nombre"),
        {"id_usuario": id_usuario}
    ).fetchall()
    return [
        {
            "id_categoria": row[0],
            "nombre": row[1],
            "tipo": row[2],
        }
        for row in rows
    ]
