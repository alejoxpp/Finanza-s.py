from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.modelos.database import get_db
from backend.servicios.categorias_service import crear_categoria, listar_categorias

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
