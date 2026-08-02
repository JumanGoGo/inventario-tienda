"""agrega tabla categorias y FK en productos.categoria_id

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=500), nullable=True),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("fecha_creacion", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("fecha_actualizacion", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_categorias_nombre", "categorias", ["nombre"], unique=True)

    op.create_index("ix_productos_categoria_id", "productos", ["categoria_id"])
    op.create_foreign_key(
        "fk_productos_categoria_id",
        "productos",
        "categorias",
        ["categoria_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_productos_categoria_id", "productos", type_="foreignkey")
    op.drop_index("ix_productos_categoria_id", table_name="productos")

    op.drop_index("ix_categorias_nombre", table_name="categorias")
    op.drop_table("categorias")
