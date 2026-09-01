from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.modelos.database import test_connection
from backend.rutas import auth, categorias, movimientos, analitica

app = FastAPI(
    title="Finanzas Personales API",
    version="1.0.0",
    description="Backend para gestión de finanzas personales con análisis financiero básico",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database_connected": test_connection(),
    }


app.include_router(auth.router, prefix="/api")
app.include_router(categorias.router, prefix="/api")
app.include_router(movimientos.router, prefix="/api")
app.include_router(analitica.router, prefix="")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
