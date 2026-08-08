# Lista de Casos de Prueba — Parte 3

Este documento enumera los casos probados manualmente sobre la API en ejecución
(`docker compose up --build`, base de datos limpia). Todos los casos están
también automatizados en [`postman_collection.json`](postman_collection.json)
(colección Postman, 39 requests con aserciones) y una parte representativa
está cubierta por la suite de `pytest` (26 tests automatizados en `tests/`).

Para reproducir esta tabla: importar `postman_collection.json` en Postman,
configurar la variable `base_url` (por defecto `http://localhost:8000`) y
correr la colección completa con **Run collection**, en orden de carpetas
(1 → 4). Las carpetas están diseñadas para ejecutarse en secuencia porque
encadenan datos (el producto creado en la carpeta 2 se usa en la 3, etc.).

Leyenda: ✅ = comportamiento esperado y verificado.

## 1. Categoría

| # | Método | Endpoint | Caso | Resultado esperado | Obtenido |
|---|---|---|---|---|---|
| 1.1 | POST | `/api/categorias` | Crear categoría válida | 201 Created | ✅ |
| 1.2 | POST | `/api/categorias` | Crear segunda categoría válida | 201 Created | ✅ |
| 1.3 | GET | `/api/categorias` | Listar todas | 200 OK | ✅ |
| 1.4 | GET | `/api/categorias?nombre=elect` | Búsqueda parcial insensible a mayúsculas | 200 OK, solo coincidencias | ✅ |
| 1.5 | GET | `/api/categorias/{id}` | Obtener por id existente | 200 OK | ✅ |
| 1.6 | PUT | `/api/categorias/{id}` | Actualizar descripción | 200 OK | ✅ |
| 1.7 | POST | `/api/categorias` | **Error:** nombre duplicado | 409 Conflict | ✅ |
| 1.8 | GET | `/api/categorias/999999` | **Error:** id inexistente | 404 Not Found | ✅ |
| 1.9 | PUT | `/api/categorias/{id}` | Desactivar categoría sin productos asociados | 200 OK | ✅ |

## 2. Producto

| # | Método | Endpoint | Caso | Resultado esperado | Obtenido |
|---|---|---|---|---|---|
| 2.1 | POST | `/api/productos` | Crear producto válido, con `categoria_id` real | 201 Created | ✅ |
| 2.2 | POST | `/api/productos` | Crear segundo producto en la misma categoría | 201 Created | ✅ |
| 2.3 | GET | `/api/productos` | Listar todos | 200 OK | ✅ |
| 2.4 | GET | `/api/productos?nombre=laptop` | Búsqueda parcial por nombre | 200 OK, solo coincidencias | ✅ |
| 2.5 | GET | `/api/productos?categoria_id={id}` | Filtro por categoría | 200 OK | ✅ |
| 2.6 | GET | `/api/productos/{id}` | Obtener por id existente | 200 OK | ✅ |
| 2.7 | PUT | `/api/productos/{id}` | Actualizar precio de venta | 200 OK | ✅ |
| 2.8 | GET | `/api/productos/stock-bajo` | Listar productos bajo su stock mínimo | 200 OK | ✅ |
| 2.9 | POST | `/api/productos` | **Error:** SKU duplicado | 409 Conflict | ✅ |
| 2.10 | POST | `/api/productos` | **Error:** `categoria_id` inexistente | 404 Not Found | ✅ |
| 2.11 | POST | `/api/productos` | **Error (regla de negocio):** categoría inactiva | 400 Bad Request | ✅ |
| 2.12 | POST | `/api/productos` | **Error:** `precio_venta` negativo (validación de esquema) | 422 Unprocessable Entity | ✅ |

## 3. Movimiento

| # | Método | Endpoint | Caso | Resultado esperado | Obtenido |
|---|---|---|---|---|---|
| 3.1 | POST | `/api/movimientos` | Entrada válida (incrementa stock) | 201 Created, `stock_nuevo = stock_anterior + cantidad` | ✅ |
| 3.2 | POST | `/api/movimientos` | Salida válida (decrementa stock) | 201 Created | ✅ |
| 3.3 | GET | `/api/movimientos` | Listar todos | 200 OK | ✅ |
| 3.4 | GET | `/api/movimientos?tipo=entrada` | Filtro por tipo | 200 OK | ✅ |
| 3.5 | GET | `/api/movimientos?producto_id={id}` | Filtro por producto | 200 OK | ✅ |
| 3.6 | GET | `/api/movimientos/{id}` | Obtener por id existente | 200 OK | ✅ |
| 3.7 | PUT | `/api/movimientos/{id}` | Actualizar observaciones (no afecta stock) | 200 OK | ✅ |
| 3.8 | POST | `/api/movimientos` | **Error (regla de negocio):** salida mayor al stock disponible | 400 Bad Request | ✅ |
| 3.9 | POST | `/api/movimientos` | **Error:** `producto_id` inexistente | 404 Not Found | ✅ |
| 3.10 | POST | `/api/movimientos` | **Error:** `cantidad = 0` (validación de esquema) | 422 Unprocessable Entity | ✅ |
| 3.11 | DELETE | `/api/movimientos/{id}` | Eliminar el movimiento más reciente (revierte stock) | 204 No Content | ✅ |
| 3.12 | GET | `/api/productos/{id}` | Verificar que el stock refleja la reversión | 200 OK, stock correcto | ✅ |
| 3.13 | POST | `/api/movimientos` | Salida que deja el stock casi en cero (preparación) | 201 Created | ✅ |
| 3.14 | DELETE | `/api/movimientos/{id}` | **Error (regla de negocio, corregida en Parte 3):** eliminar una entrada antigua cuyo efecto ya fue consumido por movimientos posteriores | 400 Bad Request | ✅ |

## 4. Reglas de negocio cruzadas (Categoría ↔ Producto)

| # | Método | Endpoint | Caso | Resultado esperado | Obtenido |
|---|---|---|---|---|---|
| 4.1 | DELETE | `/api/categorias/{id}` | **Error (regla de negocio):** eliminar categoría con productos activos | 409 Conflict | ✅ |
| 4.2 | DELETE | `/api/productos/{id}` | Desactivar producto 1 | 204 No Content | ✅ |
| 4.3 | DELETE | `/api/productos/{id}` | Desactivar producto 2 | 204 No Content | ✅ |
| 4.4 | DELETE | `/api/categorias/{id}` | Eliminar la misma categoría, ya sin productos activos | 204 No Content | ✅ |

## Bug encontrado y corregido durante esta fase

Al diseñar el caso **3.14**, se detectó que `DELETE /api/movimientos/{id}` revertía
el efecto de cualquier movimiento sobre el stock sin validar el resultado. Si el
movimiento eliminado era antiguo y su efecto ya había sido "consumido" por
movimientos posteriores, el stock del producto podía quedar en un valor
negativo, algo que el resto de la API impide explícitamente. Se corrigió en
`app/routers/movimientos.py` (`eliminar_movimiento`) agregando la misma
validación que ya protegía la creación de movimientos, y se añadió el test
automatizado `test_eliminar_entrada_antigua_rechaza_si_deja_stock_negativo`
en `tests/test_movimientos.py`.

## Resumen

- **Tests automatizados (pytest):** 26/26 ✅
- **Casos manuales/Postman documentados aquí:** 39/39 ✅
- **Cobertura:** CRUD completo de las 3 entidades, la relación Producto→Categoría,
  las 4 reglas de negocio, los filtros de búsqueda y el manejo consistente de errores.
