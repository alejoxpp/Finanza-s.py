from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import mysql.connector
from datetime import date
import pandas as pd

from analitica import cargar_datos, predecir_gasto_proximo_mes, detectar_anomalias

app = FastAPI(title="Finanzas Personales API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión DB
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="finanzas_personales"
    )

# --- Schemas ---
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    correo: str
    contrasena: str = Field(..., min_length=8)

class CategoriaCreate(BaseModel):
    nombre: str
    tipo: str
    id_usuario: int

class MovimientoCreate(BaseModel):
    id_usuario: int
    id_categoria: int
    tipo: str
    monto: float = Field(..., gt=0)
    fecha: date
    descripcion: Optional[str] = None

# --- Rutas CRUD ---
@app.post("/api/usuarios", status_code=201)
def crear_usuario(u: UsuarioCreate):
    db = get_db()
    cursor = db.cursor()
    try:
        # Hash simulado para el ejercicio
        hash_pw = f"hash_{u.contrasena}"
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contrasena_hash) VALUES (%s, %s, %s)",
            (u.nombre, u.correo, hash_pw)
        )
        db.commit()
        return {"id_usuario": cursor.lastrowid, "mensaje": "Usuario creado con éxito"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
    finally:
        db.close()

@app.get("/api/categorias")
def listar_categorias(id_usuario: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias WHERE id_usuario = %s", (id_usuario,))
    res = cursor.fetchall()
    db.close()
    return res

@app.post("/api/movimientos", status_code=201)
def registrar_movimiento(m: MovimientoCreate):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """INSERT INTO ingresos_gastos 
               (id_usuario, id_categoria, tipo, monto, fecha, descripcion) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (m.id_usuario, m.id_categoria, m.tipo, m.monto, m.fecha, m.descripcion)
        )
        db.commit()
        return {"id_movimiento": cursor.lastrowid, "mensaje": "Movimiento registrado"}
    finally:
        db.close()

@app.get("/api/movimientos")
def listar_movimientos(id_usuario: int, desde: Optional[date] = None, hasta: Optional[date] = None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = "SELECT m.*, c.nombre as categoria FROM ingresos_gastos m JOIN categorias c ON m.id_categoria = c.id_categoria WHERE m.id_usuario = %s"
    params = [id_usuario]

    if desde:
        query += " AND m.fecha >= %s"
        params.append(desde)
    if hasta:
        query += " AND m.fecha <= %s"
        params.append(hasta)
        
    query += " ORDER BY m.fecha DESC"
    cursor.execute(query, tuple(params))
    res = cursor.fetchall()
    db.close()
    return res

@app.get("/api/resumen")
def obtener_resumen(id_usuario: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END) as total_ingresos,
            SUM(CASE WHEN tipo = 'gasto' THEN monto ELSE 0 END) as total_gastos
        FROM ingresos_gastos WHERE id_usuario = %s
    """, (id_usuario,))
    data = cursor.fetchone()
    db.close()
    
    ingresos = float(data['total_ingresos'] or 0)
    gastos = float(data['total_gastos'] or 0)
    balance = ingresos - gastos
    
    return {
        "total_ingresos": ingresos,
        "total_gastos": gastos,
        "balance": balance,
        "porcentaje_ahorro": round((balance / ingresos * 100), 2) if ingresos > 0 else 0
    }

# --- Rutas Módulo Analítico ---
@app.get("/api/analitica/prediccion")
def api_prediccion(id_usuario: int):
    db = get_db()
    try:
        df = cargar_datos(db, id_usuario)
        resultado = predecir_gasto_proximo_mes(df)
        return {"id_usuario": id_usuario, **resultado}
    finally:
        db.close()

@app.get("/api/analitica/anomalias")
def api_anomalias(id_usuario: int):
    db = get_db()
    try:
        df = cargar_datos(db, id_usuario)
        anomalias = detectar_anomalias(df)
        return {"id_usuario": id_usuario, "anomalias": anomalias}
    finally:
        db.close()