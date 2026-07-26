from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoOut, ProductoUpdate

router = APIRouter(prefix="/api/productos", tags=["Productos"])


@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(payload: ProductoCreate, db: Session = Depends(get_db)):
    existente = db.execute(select(Producto).where(Producto.sku == payload.sku)).scalar_one_or_none()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El SKU '{payload.sku}' ya existe")

    producto = Producto(**payload.model_dump(), stock_actual=0)
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.get("", response_model=list[ProductoOut])
def listar_productos(
    activo: bool | None = None,
    categoria_id: int | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = select(Producto)
    if activo is not None:
        query = query.where(Producto.activo == activo)
    if categoria_id is not None:
        query = query.where(Producto.categoria_id == categoria_id)
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()


@router.get("/stock-bajo", response_model=list[ProductoOut])
def productos_con_stock_bajo(db: Session = Depends(get_db)):
    productos = db.execute(select(Producto).where(Producto.activo == True)).scalars().all()  # noqa: E712
    return [p for p in productos if p.stock_actual < p.stock_minimo]


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, payload: ProductoUpdate, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    datos = payload.model_dump(exclude_unset=True)
    for campo, valor in datos.items():
        setattr(producto, campo, valor)

    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    producto.activo = False
    db.commit()
