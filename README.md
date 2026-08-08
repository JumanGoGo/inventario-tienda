# Sistema de Gestión de Inventario

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
git clone <URL_DE_ESTE_REPOSITORIO>
cd inventario-tienda
cp .env.example .env
docker compose up --build
```

La API queda disponible en `http://localhost:8000` y la documentación interactiva (Swagger) en:

```
http://localhost:8000/docs
```

Al iniciar, el contenedor `api` ejecuta automáticamente `alembic upgrade head` antes de levantar el servidor, por lo que las tablas se crean solas (no requiere pasos manuales de migración).

## Estructura del proyecto

```
app/
  main.py            # Instancia FastAPI, registro de routers y manejo global de errores
  config.py          # Carga de variables de entorno (.env)
  database/db.py     # Engine, sesión y Base declarativa de SQLAlchemy
  models/            # Modelos SQLAlchemy (tablas): categoria, producto, movimiento
  schemas/           # Esquemas Pydantic (validación de entrada/salida)
  routers/           # Endpoints agrupados por entidad
alembic/             # Migraciones de base de datos
tests/               # Tests con pytest
scripts/             # Utilidades de desarrollo (ej. generador de la colección Postman)
```

## Variables de entorno

Copiar `.env.example` a `.env` y ajustar si es necesario:

| Variable | Descripción |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Credenciales del contenedor de PostgreSQL |
| `DATABASE_URL` | Cadena de conexión usada por la API (debe apuntar al host `db`, el nombre del servicio en `docker-compose.yml`) |
| `APP_NAME` / `APP_ENV` | Metadatos de la aplicación |

## Entidades implementadas

- **Categoría**: CRUD completo (crear, listar con filtros, obtener, actualizar, eliminar-lógica).
- **Producto**: CRUD completo. Pertenece a una `Categoría` mediante `categoria_id` (clave foránea real).
- **Movimiento**: CRUD completo. Registrar un movimiento (`entrada`, `salida`, `ajuste`) actualiza automáticamente el `stock_actual` del producto asociado, validando que no queden stocks negativos.

Proveedor, Usuario (autenticación) y Alerta quedan fuera de alcance de esta entrega.

## Relación entre entidades

`Producto.categoria_id` es una clave foránea real hacia `Categoria.id` (migración `0002_categorias.py`). Al crear o actualizar un producto se valida que la categoría exista y esté activa.

## Reglas de negocio

- **No se puede desactivar/eliminar una categoría si tiene productos activos asociados** (`DELETE /api/categorias/{id}` responde `409 Conflict`). Evita dejar productos huérfanos de clasificación.
- **No se puede asignar un producto a una categoría inactiva** (`400 Bad Request` al crear/actualizar el producto).
- **No se permite un movimiento de `salida` mayor al stock disponible**, ni un `ajuste` que deje el stock en negativo (`400 Bad Request`).
- **No se puede eliminar un movimiento si revertir su efecto deja el stock en negativo** (`400 Bad Request`). Cubre el caso de eliminar un movimiento antiguo cuyo efecto ya fue consumido por movimientos posteriores.
- **El SKU de un producto y el nombre de una categoría son únicos** (`409 Conflict` ante duplicados).

## Filtros y búsqueda

- `GET /api/productos?nombre=laptop` — búsqueda parcial e insensible a mayúsculas por nombre.
- `GET /api/productos?categoria_id=1&activo=true` — filtros combinables.
- `GET /api/categorias?nombre=elect&activa=true` — mismos filtros para categorías.
- `GET /api/movimientos?producto_id=1&tipo=entrada` — filtros por producto y tipo de movimiento.

## Manejo de errores

Todas las respuestas de error usan el mismo formato JSON `{"detail": "..."}`:

- `400` — violación de una regla de negocio (ej. stock insuficiente, categoría inactiva).
- `404` — recurso no encontrado.
- `409` — conflicto de integridad (duplicados, o intento de romper una regla de negocio referencial).
- `422` — error de validación de esquema (Pydantic), generado automáticamente por FastAPI.
- `500` — error no controlado; se captura con un handler global que responde JSON en vez de texto plano, sin filtrar detalles internos.

## Endpoints principales

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/categorias` | Crear categoría |
| GET | `/api/categorias` | Listar categorías (filtros: `activa`, `nombre`) |
| GET | `/api/categorias/{id}` | Obtener categoría |
| PUT | `/api/categorias/{id}` | Actualizar categoría |
| DELETE | `/api/categorias/{id}` | Desactivar categoría (bloqueado si tiene productos activos) |
| POST | `/api/productos` | Crear producto |
| GET | `/api/productos` | Listar productos (filtros: `activo`, `categoria_id`, `nombre`) |
| GET | `/api/productos/stock-bajo` | Productos con stock por debajo del mínimo |
| GET | `/api/productos/{id}` | Obtener producto |
| PUT | `/api/productos/{id}` | Actualizar producto |
| DELETE | `/api/productos/{id}` | Desactivar producto |
| POST | `/api/movimientos` | Registrar movimiento (entrada/salida/ajuste) |
| GET | `/api/movimientos` | Listar movimientos (filtros: `producto_id`, `tipo`) |
| GET | `/api/movimientos/{id}` | Obtener movimiento |
| PUT | `/api/movimientos/{id}` | Actualizar metadatos del movimiento |
| DELETE | `/api/movimientos/{id}` | Eliminar movimiento (revierte su efecto sobre el stock) |

Lista completa y probada en vivo en `/docs`.

## Tests automatizados

```bash
pip install -r requirements.txt
pytest
```

Los tests usan una base de datos SQLite en memoria, por lo que no requieren Docker ni PostgreSQL.
Estado actual: **26/26 tests pasando**.

## Pruebas manuales (Parte 3)

Además de los tests automatizados, el proyecto incluye una colección Postman
lista para importar:

- [`postman_collection.json`](postman_collection.json) — 39 requests (casos
  válidos y de error) sobre las 3 entidades, organizados en 4 carpetas que se
  ejecutan en secuencia (**Run collection**). Cada request incluye aserciones
  automáticas de código de estado y, en varios casos, del cuerpo de la respuesta.
- [`CASOS_DE_PRUEBA.md`](CASOS_DE_PRUEBA.md) — tabla con la descripción de
  cada caso, el resultado esperado y el resultado obtenido, más el detalle de
  un bug encontrado y corregido durante esta fase (reversión de stock al
  eliminar movimientos antiguos).

Para reproducir: `docker compose up --build` con base de datos limpia, luego
importar la colección en Postman y ejecutarla con `base_url = http://localhost:8000`.

