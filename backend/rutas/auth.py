from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.modelos.database import get_db
from backend.servicios.usuarios_service import crear_usuario, listar_usuarios

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


class UsuarioCrear(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str


@router.post("")
def registrar_usuario(payload: UsuarioCrear, db: Session = Depends(get_db)):
    try:
        usuario = crear_usuario(db, payload.nombre, str(payload.correo), payload.contrasena)
        return {"message": "Usuario registrado correctamente", "data": usuario}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("")
def listar_usuarios_endpoint(db: Session = Depends(get_db)):
    return {"data": listar_usuarios(db)}
