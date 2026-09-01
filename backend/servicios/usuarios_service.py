import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy import text


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verificar_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def crear_usuario(db: Session, nombre: str, correo: str, contrasena: str):
    existe = db.execute(
        text("SELECT id_usuario FROM usuarios WHERE correo = :correo"),
        {"correo": correo}
    ).fetchone()
    if existe:
        raise ValueError("El correo ya está registrado")

    password_hash = hash_password(contrasena)
    db.execute(
        text("""
            INSERT INTO usuarios (nombre, correo, contrasena_hash)
            VALUES (:nombre, :correo, :contrasena_hash)
        """),
        {"nombre": nombre, "correo": correo, "contrasena_hash": password_hash}
    )
    db.commit()

    usuario = db.execute(
        text("SELECT id_usuario, nombre, correo, fecha_registro FROM usuarios WHERE correo = :correo"),
        {"correo": correo}
    ).fetchone()

    return {
        "id_usuario": usuario[0],
        "nombre": usuario[1],
        "correo": usuario[2],
        "fecha_registro": usuario[3].strftime("%Y-%m-%d %H:%M:%S") if usuario[3] else None,
    }


def listar_usuarios(db: Session):
    rows = db.execute(
        text("SELECT id_usuario, nombre, correo, fecha_registro FROM usuarios ORDER BY id_usuario")
    ).fetchall()
    return [
        {
            "id_usuario": row[0],
            "nombre": row[1],
            "correo": row[2],
            "fecha_registro": row[3].strftime("%Y-%m-%d %H:%M:%S") if row[3] else None,
        }
        for row in rows
    ]
