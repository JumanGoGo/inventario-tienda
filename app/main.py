import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.routers import categorias, movimientos, productos

logger = logging.getLogger("app")

app = FastAPI(
    title=settings.app_name,
    description="API para el control de inventario de una tienda",
    version="1.0.0",
)

app.include_router(categorias.router)
app.include_router(productos.router)
app.include_router(movimientos.router)


@app.exception_handler(IntegrityError)
def manejar_integridad(request: Request, exc: IntegrityError):
    """Cubre violaciones de restricciones de la base de datos que escapan a
    las validaciones de negocio (ej. condiciones de carrera en SKU/nombre
    unicos, o FKs invalidas), devolviendo un error consistente en vez de un 500.
    """
    logger.warning("IntegrityError en %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "La operacion viola una restriccion de integridad de datos (duplicado o referencia invalida)"},
    )


@app.exception_handler(Exception)
def manejar_error_no_controlado(request: Request, exc: Exception):
    """Sin este handler, un error no controlado devuelve texto plano (no JSON),
    lo que rompe la consistencia del contrato de la API. Aqui se homogeneiza
    a JSON y se evita filtrar detalles internos al cliente.
    """
    logger.exception("Error no controlado en %s", request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )


@app.get("/", tags=["Healthcheck"])
def raiz():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
