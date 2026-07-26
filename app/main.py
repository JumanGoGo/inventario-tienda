from fastapi import FastAPI

from app.config import settings
from app.routers import movimientos, productos

app = FastAPI(
    title=settings.app_name,
    description="API para el control de inventario de una tienda",
    version="1.0.0",
)

app.include_router(productos.router)
app.include_router(movimientos.router)


@app.get("/", tags=["Healthcheck"])
def raiz():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}
