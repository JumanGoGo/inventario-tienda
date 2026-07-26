from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductoBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    sku: str = Field(..., max_length=50)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_venta: Decimal = Field(..., gt=0)
    costo_unitario: Optional[Decimal] = Field(None, ge=0)
    stock_minimo: int = Field(0, ge=0)
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_venta: Optional[Decimal] = Field(None, gt=0)
    costo_unitario: Optional[Decimal] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    activo: Optional[bool] = None


class ProductoOut(ProductoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_actual: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
