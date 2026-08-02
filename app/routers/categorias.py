from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter(prefix="/api/categorias", tags=["Categorias"])


@router.post("", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(payload: CategoriaCreate, db: Session = Depends(get_db)):
    existente = db.execute(select(Categoria).where(Categoria.nombre == payload.nombre)).scalar_one_or_none()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una categoria con el nombre '{payload.nombre}'",
        )

    categoria = Categoria(**payload.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.get("", response_model=list[CategoriaOut])
def listar_categorias(
    activa: bool | None = None,
    nombre: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = select(Categoria)
    if activa is not None:
        query = query.where(Categoria.activa == activa)
    if nombre:
        query = query.where(func.lower(Categoria.nombre).contains(nombre.lower()))
    query = query.offset(skip).limit(limit)
    return db.execute(query).scalars().all()


@router.get("/{categoria_id}", response_model=CategoriaOut)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(categoria_id: int, payload: CategoriaUpdate, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")

    datos = payload.model_dump(exclude_unset=True)

    # Regla de negocio: no se puede desactivar una categoria si tiene productos activos asociados.
    if datos.get("activa") is False and categoria.activa:
        _validar_sin_productos_activos(categoria_id, db)

    if "nombre" in datos and datos["nombre"] != categoria.nombre:
        duplicado = db.execute(
            select(Categoria).where(Categoria.nombre == datos["nombre"], Categoria.id != categoria_id)
        ).scalar_one_or_none()
        if duplicado:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una categoria con el nombre '{datos['nombre']}'",
            )

    for campo, valor in datos.items():
        setattr(categoria, campo, valor)

    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria no encontrada")

    # Regla de negocio: no se puede eliminar (desactivar) una categoria
    # mientras tenga productos activos asociados, para no dejar productos
    # huerfanos de clasificacion en el inventario.
    _validar_sin_productos_activos(categoria_id, db)

    categoria.activa = False
    db.commit()


def _validar_sin_productos_activos(categoria_id: int, db: Session) -> None:
    tiene_productos_activos = db.execute(
        select(Producto.id).where(Producto.categoria_id == categoria_id, Producto.activo == True)  # noqa: E712
    ).first()
    if tiene_productos_activos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede desactivar la categoria: tiene productos activos asociados",
        )
