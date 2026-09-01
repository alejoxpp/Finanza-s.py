from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.modelos.database import get_db
from backend.servicios.analitica_service import anomalias_usuario, prediccion_usuario, resumen_usuario

router = APIRouter(tags=["analitica"])


@router.get("/api/resumen")
def resumen_endpoint(
    id_usuario: int = Query(..., description="ID del usuario"),
    mes: str | None = Query(None, description="Mes en formato YYYY-MM"),
    db: Session = Depends(get_db),
):
    try:
        return {"data": resumen_usuario(db, id_usuario, mes=mes)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al generar el resumen: {str(exc)}") from exc


@router.get("/api/analitica/prediccion")
def prediccion_endpoint(
    id_usuario: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
):
    try:
        return {"data": prediccion_usuario(db, id_usuario)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al calcular la predicción: {str(exc)}") from exc


@router.get("/api/analitica/anomalias")
def anomalias_endpoint(
    id_usuario: int = Query(..., description="ID del usuario"),
    umbral_z: float = Query(2.0, description="Umbral de z-score para anomalías"),
    db: Session = Depends(get_db),
):
    try:
        return {"data": anomalias_usuario(db, id_usuario, umbral_z=umbral_z)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al detectar anomalías: {str(exc)}") from exc
