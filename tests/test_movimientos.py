def crear_producto(client, stock_minimo=5):
    payload = {
        "nombre": "Mouse Logitech",
        "sku": "MOU-001",
        "precio_venta": "25.00",
        "stock_minimo": stock_minimo,
    }
    return client.post("/api/productos", json=payload).json()


def test_entrada_incrementa_stock(client):
    producto = crear_producto(client)
    response = client.post(
        "/api/movimientos",
        json={"producto_id": producto["id"], "tipo": "entrada", "cantidad": 50, "referencia": "Compra inicial"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["stock_anterior"] == 0
    assert data["stock_nuevo"] == 50

    producto_actualizado = client.get(f"/api/productos/{producto['id']}").json()
    assert producto_actualizado["stock_actual"] == 50


def test_salida_decrementa_stock(client):
    producto = crear_producto(client)
    client.post("/api/movimientos", json={"producto_id": producto["id"], "tipo": "entrada", "cantidad": 20})

    response = client.post(
        "/api/movimientos",
        json={"producto_id": producto["id"], "tipo": "salida", "cantidad": 5, "documento_id": "BOL-001"},
    )
    assert response.status_code == 201
    assert response.json()["stock_nuevo"] == 15


def test_salida_rechaza_stock_insuficiente(client):
    producto = crear_producto(client)
    response = client.post(
        "/api/movimientos",
        json={"producto_id": producto["id"], "tipo": "salida", "cantidad": 5},
    )
    assert response.status_code == 400


def test_ajuste_permite_cantidad_negativa(client):
    producto = crear_producto(client)
    client.post("/api/movimientos", json={"producto_id": producto["id"], "tipo": "entrada", "cantidad": 10})

    response = client.post(
        "/api/movimientos",
        json={"producto_id": producto["id"], "tipo": "ajuste", "cantidad": -2, "observaciones": "Merma"},
    )
    assert response.status_code == 201
    assert response.json()["stock_nuevo"] == 8


def test_movimiento_con_producto_inexistente(client):
    response = client.post(
        "/api/movimientos",
        json={"producto_id": 999, "tipo": "entrada", "cantidad": 10},
    )
    assert response.status_code == 404


def test_eliminar_movimiento_revierte_stock(client):
    producto = crear_producto(client)
    movimiento = client.post(
        "/api/movimientos", json={"producto_id": producto["id"], "tipo": "entrada", "cantidad": 30}
    ).json()

    response = client.delete(f"/api/movimientos/{movimiento['id']}")
    assert response.status_code == 204

    producto_actualizado = client.get(f"/api/productos/{producto['id']}").json()
    assert producto_actualizado["stock_actual"] == 0
