"""tablas iniciales: productos y movimientos

Revision ID: 0001
Revises:
Create Date: 2026-07-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nombre", sa.String(length=150), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=False),
        sa.Column("descripcion", sa.String(length=500), nullable=True),
        sa.Column("precio_venta", sa.Numeric(10, 2), nullable=False),
        sa.Column("costo_unitario", sa.Numeric(10, 2), nullable=True),
        sa.Column("stock_actual", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stock_minimo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column("proveedor_id", sa.Integer(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_productos_sku", "productos", ["sku"], unique=True)

    op.create_table(
        "movimientos",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("productos.id"), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("documento_id", sa.String(length=50), nullable=True),
        sa.Column("referencia", sa.String(length=200), nullable=True),
        sa.Column("observaciones", sa.String(length=500), nullable=True),
        sa.Column("stock_anterior", sa.Integer(), nullable=False),
        sa.Column("stock_nuevo", sa.Integer(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_movimientos_producto_id", "movimientos", ["producto_id"])


def downgrade() -> None:
    op.drop_index("ix_movimientos_producto_id", table_name="movimientos")
    op.drop_table("movimientos")
    op.drop_index("ix_productos_sku", table_name="productos")
    op.drop_table("productos")
