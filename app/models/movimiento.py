from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)

    # usuario_id se convertira en FK real cuando se implemente autenticacion (Parte 2).
    usuario_id = Column(Integer, nullable=True)

    tipo = Column(String(20), nullable=False)  # entrada, salida, ajuste
    cantidad = Column(Integer, nullable=False)
    documento_id = Column(String(50), nullable=True)
    referencia = Column(String(200), nullable=True)
    observaciones = Column(String(500), nullable=True)
    stock_anterior = Column(Integer, nullable=False)
    stock_nuevo = Column(Integer, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    producto = relationship("Producto", backref="movimientos")
