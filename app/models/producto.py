from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    descripcion = Column(String(500), nullable=True)
    precio_venta = Column(Numeric(10, 2), nullable=False)
    costo_unitario = Column(Numeric(10, 2), nullable=True)
    stock_actual = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=0)

    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True, index=True)

    # proveedor_id se agrega como FK real cuando se implemente la tabla Proveedor.
    proveedor_id = Column(Integer, nullable=True)

    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    categoria = relationship("Categoria", backref="productos")
