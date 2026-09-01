from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.modelos.database import get_db
from backend.servicios.categorias_service import (
    crear_categoria,
    listar_categorias,
    editar_categoria,
    eliminar_categoria,
)

router = APIRouter(prefix="/categorias", tags=["categorias"])


class CategoriaCrear(BaseModel):
    id_usuario: int
    nombre: str
    tipo: str


@router.post("")
def crear_categoria_endpoint(payload: CategoriaCrear, db: Session = Depends(get_db)):
    try:
        categoria = crear_categoria(db, payload.id_usuario, payload.nombre, payload.tipo)
        return {"message": "Categoría creada correctamente", "data": categoria}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("")
def listar_categorias_endpoint(
    id_usuario: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
):
    return {"data": listar_categorias(db, id_usuario)}


@router.put("/{id_categoria}")
def actualizar_categoria_endpoint(
    id_categoria: int,
    payload: CategoriaCrear,
    db: Session = Depends(get_db),
):
    try:
        categoria = editar_categoria(
            db, id_categoria, payload.id_usuario, payload.nombre, payload.tipo
        )
        return {"message": "Categoría actualizada correctamente", "data": categoria}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{id_categoria}")
def eliminar_categoria_endpoint(
    id_categoria: int,
    id_usuario: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
):
    try:
        ok = eliminar_categoria(db, id_categoria, id_usuario)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    return {"message": "Categoría eliminada correctamente"}
