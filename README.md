# Sistema de Gestión de Inventario - Parte 1

API REST construida con FastAPI para el control de inventario de una tienda.

## Tecnologías

- FastAPI + Uvicorn
- SQLAlchemy 2.0
- Alembic (migraciones)
- PostgreSQL
- Docker / Docker Compose
- Pytest

## Cómo ejecutar

```bash
docker compose up --build
```

La API queda disponible en `http://localhost:8000` y la documentación interactiva en:

```
http://localhost:8000/docs
```

Al iniciar, el contenedor `api` ejecuta automáticamente `alembic upgrade head` antes de levantar el servidor, por lo que las tablas se crean solas.

## Entidades implementadas (Parte 1)

- **Producto**: CRUD completo (crear, listar, obtener, actualizar, eliminar-lógico).
- **Movimiento**: CRUD completo. Registrar un movimiento (`entrada`, `salida`, `ajuste`) actualiza automáticamente el `stock_actual` del producto asociado, validando que no queden stocks negativos.

Categoría, Proveedor, Usuario (autenticación) y Alerta se agregan en la Parte 2.

## Variables de entorno

Copiar `.env.example` a `.env` y ajustar si es necesario. Ya viene incluido un `.env` funcional para desarrollo local.

## Tests

```bash
pip install -r requirements.txt
pytest
```

Los tests usan una base de datos SQLite en memoria, por lo que no requieren Docker ni PostgreSQL.

## Estructura del proyecto

```
app/
  main.py            # Instancia FastAPI y registro de routers
  config.py          # Carga de variables de entorno (.env)
  database/db.py     # Engine, sesión y Base declarativa de SQLAlchemy
  models/            # Modelos SQLAlchemy (tablas)
  schemas/           # Esquemas Pydantic (validación de entrada/salida)
  routers/           # Endpoints agrupados por entidad
alembic/             # Migraciones de base de datos
tests/               # Tests con pytest
```
