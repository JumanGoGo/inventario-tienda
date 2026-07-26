from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TipoMovimiento(str, Enum):
    entrada = "entrada"
    salida = "salida"
    ajuste = "ajuste"


class MovimientoBase(BaseModel):
    producto_id: int
    tipo: TipoMovimiento
    # Para entrada/salida debe ser positiva. Para ajuste puede ser negativa
    # (ej. merma) o positiva (ej. corrección de conteo).
    cantidad: int = Field(..., description="Distinto de cero")
    documento_id: Optional[str] = Field(None, max_length=50)
    referencia: Optional[str] = Field(None, max_length=200)
    observaciones: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def validar_cantidad(self):
        if self.cantidad == 0:
            raise ValueError("cantidad no puede ser cero")
        if self.tipo in (TipoMovimiento.entrada, TipoMovimiento.salida) and self.cantidad < 0:
            raise ValueError(f"cantidad debe ser positiva para movimientos de tipo '{self.tipo.value}'")
        return self


class MovimientoCreate(MovimientoBase):
    pass


class MovimientoUpdate(BaseModel):
    documento_id: Optional[str] = Field(None, max_length=50)
    referencia: Optional[str] = Field(None, max_length=200)
    observaciones: Optional[str] = Field(None, max_length=500)


class MovimientoOut(MovimientoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_anterior: int
    stock_nuevo: int
    fecha_creacion: datetime
