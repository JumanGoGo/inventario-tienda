def crear_producto_ejemplo(client, sku="SKU-001"):
    payload = {
        "nombre": "Laptop Dell",
        "sku": sku,
        "descripcion": "Laptop 15 pulgadas",
        "precio_venta": "799.99",
        "costo_unitario": "600.00",
        "stock_minimo": 5,
    }
    return client.post("/api/productos", json=payload)


def test_crear_producto(client):
    response = crear_producto_ejemplo(client)
    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "SKU-001"
    assert data["stock_actual"] == 0
    assert data["activo"] is True


def test_no_permite_sku_duplicado(client):
    crear_producto_ejemplo(client)
    response = crear_producto_ejemplo(client)
    assert response.status_code == 409


def test_listar_productos(client):
    crear_producto_ejemplo(client, sku="SKU-001")
    crear_producto_ejemplo(client, sku="SKU-002")
    response = client.get("/api/productos")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_obtener_producto_no_encontrado(client):
    response = client.get("/api/productos/999")
    assert response.status_code == 404


def test_actualizar_producto(client):
    creado = crear_producto_ejemplo(client).json()
    response = client.put(f"/api/productos/{creado['id']}", json={"precio_venta": "899.99"})
    assert response.status_code == 200
    assert response.json()["precio_venta"] == "899.99"


def test_eliminar_producto_es_soft_delete(client):
    creado = crear_producto_ejemplo(client).json()
    response = client.delete(f"/api/productos/{creado['id']}")
    assert response.status_code == 204

    consulta = client.get(f"/api/productos/{creado['id']}")
    assert consulta.json()["activo"] is False
