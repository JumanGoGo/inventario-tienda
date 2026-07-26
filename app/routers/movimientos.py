from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.movimiento import Movimiento
from app.models.producto import Producto
from app.schemas.movimiento import MovimientoCreate, MovimientoOut, MovimientoUpdate, TipoMovimiento

router = APIRouter(prefix="/api/movimientos", tags=["Movimientos"])


@router.post("", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED)
def crear_movimiento(payload: MovimientoCreate, db: Session = Depends(get_db)):
    producto = db.get(Producto, payload.producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    stock_anterior = producto.stock_actual

    if payload.tipo == TipoMovimiento.entrada:
        stock_nuevo = stock_anterior + payload.cantidad
    elif payload.tipo == TipoMovimiento.salida:
        if payload.cantidad > stock_anterior:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente: disponible {stock_anterior}, solicitado {payload.cantidad}",
            )
        stock_nuevo = stock_anterior - payload.cantidad
    else:  # ajuste (cantidad puede ser negativa o positiva)
        stock_nuevo = stock_anterior + payload.cantidad
        if stock_nuevo < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ajuste dejaría el stock en un valor negativo",
            )

    movimiento = Movimiento(
        **payload.model_dump(),
        stock_anterior=stock_anterior,
        stock_nuevo=stock_nuevo,
    )
    producto.stock_actual = stock_nuevo

    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


@router.get("", response_model=list[MovimientoOut])
def listar_movimientos(
    producto_id: int | None = None,
    tipo: TipoMovimiento | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = select(Movimiento)
    if producto_id is not None:
        query = query.where(Movimiento.producto_id == producto_id)
    if tipo is not None:
        query = query.where(Movimiento.tipo == tipo.value)
    query = query.order_by(Movimiento.fecha_creacion.desc()).offset(skip).limit(limit)
    return db.execute(query).scalars().all()


@router.get("/{movimiento_id}", response_model=MovimientoOut)
def obtener_movimiento(movimiento_id: int, db: Session = Depends(get_db)):
    movimiento = db.get(Movimiento, movimiento_id)
    if not movimiento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
    return movimiento


@router.put("/{movimiento_id}", response_model=MovimientoOut)
def actualizar_movimiento(movimiento_id: int, payload: MovimientoUpdate, db: Session = Depends(get_db)):
    """Permite corregir metadatos (documento, referencia, observaciones).
    No modifica cantidad/tipo: eso requeriría un nuevo movimiento de ajuste
    para no perder la trazabilidad del stock.
    """
    movimiento = db.get(Movimiento, movimiento_id)
    if not movimiento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")

    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(movimiento, campo, valor)

    db.commit()
    db.refresh(movimiento)
    return movimiento


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_movimiento(movimiento_id: int, db: Session = Depends(get_db)):
    """Elimina el registro y revierte su efecto sobre el stock del producto,
    manteniendo la consistencia del inventario.
    """
    movimiento = db.get(Movimiento, movimiento_id)
    if not movimiento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")

    producto = db.get(Producto, movimiento.producto_id)
    if producto:
        if movimiento.tipo == TipoMovimiento.entrada.value:
            producto.stock_actual -= movimiento.cantidad
        elif movimiento.tipo == TipoMovimiento.salida.value:
            producto.stock_actual += movimiento.cantidad
        else:  # ajuste
            producto.stock_actual -= movimiento.cantidad

    db.delete(movimiento)
    db.commit()
