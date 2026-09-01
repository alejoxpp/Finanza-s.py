from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.modelos.database import get_db
from backend.servicios.movimientos_service import (
    crear_movimiento,
    listar_movimientos,
    editar_movimiento,
    eliminar_movimiento,
)

router = APIRouter(prefix="/movimientos", tags=["movimientos"])


class MovimientoCrear(BaseModel):
    id_usuario: int
    id_categoria: int
    tipo: str
    monto: float
    fecha: str
    descripcion: str | None = None


@router.post("")
def crear_movimiento_endpoint(payload: MovimientoCrear, db: Session = Depends(get_db)):
    try:
        movimiento = crear_movimiento(
            db,
            payload.id_usuario,
            payload.id_categoria,
            payload.tipo,
            payload.monto,
            payload.fecha,
            payload.descripcion or "",
        )
        return {"message": "Movimiento registrado correctamente", "data": movimiento}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("")
def listar_movimientos_endpoint(
    id_usuario: int = Query(..., description="ID del usuario"),
    desde: str | None = Query(None),
    hasta: str | None = Query(None),
    categoria: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return {
        "data": listar_movimientos(db, id_usuario, desde=desde, hasta=hasta, categoria=categoria)
    }


@router.put("/{id_movimiento}")
def actualizar_movimiento_endpoint(
    id_movimiento: int,
    payload: MovimientoCrear,
    db: Session = Depends(get_db),
):
    try:
        movimiento = editar_movimiento(
            db,
            id_movimiento,
            payload.id_usuario,
            payload.id_categoria,
            payload.tipo,
            payload.monto,
            payload.fecha,
            payload.descripcion or "",
        )
        return {"message": "Movimiento actualizado correctamente", "data": movimiento}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{id_movimiento}")
def eliminar_movimiento_endpoint(
    id_movimiento: int,
    id_usuario: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
):
    ok = eliminar_movimiento(db, id_movimiento, id_usuario)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
    return {"message": "Movimiento eliminado correctamente"}
