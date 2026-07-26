from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, func

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

    # categoria_id / proveedor_id se agregan como FK reales en la Parte 2,
    # cuando se implementen las tablas Categoria y Proveedor.
    categoria_id = Column(Integer, nullable=True)
    proveedor_id = Column(Integer, nullable=True)

    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
