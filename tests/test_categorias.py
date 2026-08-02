def crear_categoria(client, nombre="Electronica"):
    return client.post("/api/categorias", json={"nombre": nombre, "descripcion": "Productos electronicos"})


def crear_producto_en_categoria(client, categoria_id, sku="SKU-CAT-001"):
    return client.post(
        "/api/productos",
        json={
            "nombre": "Laptop Dell",
            "sku": sku,
            "precio_venta": "799.99",
            "stock_minimo": 5,
            "categoria_id": categoria_id,
        },
    )


def test_crear_categoria(client):
    response = crear_categoria(client)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Electronica"
    assert data["activa"] is True


def test_no_permite_nombre_duplicado(client):
    crear_categoria(client)
    response = crear_categoria(client)
    assert response.status_code == 409


def test_listar_categorias_con_busqueda_por_nombre(client):
    crear_categoria(client, nombre="Electronica")
    crear_categoria(client, nombre="Ropa")
    response = client.get("/api/categorias", params={"nombre": "elect"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Electronica"


def test_obtener_categoria_no_encontrada(client):
    response = client.get("/api/categorias/999")
    assert response.status_code == 404


def test_actualizar_categoria(client):
    creada = crear_categoria(client).json()
    response = client.put(f"/api/categorias/{creada['id']}", json={"descripcion": "Nueva descripcion"})
    assert response.status_code == 200
    assert response.json()["descripcion"] == "Nueva descripcion"


# --- Relacion entre entidades (Producto -> Categoria) ---


def test_crear_producto_con_categoria_valida(client):
    categoria = crear_categoria(client).json()
    response = crear_producto_en_categoria(client, categoria["id"])
    assert response.status_code == 201
    assert response.json()["categoria_id"] == categoria["id"]


def test_crear_producto_con_categoria_inexistente_falla(client):
    response = crear_producto_en_categoria(client, categoria_id=999)
    assert response.status_code == 404


def test_crear_producto_con_categoria_inactiva_falla(client):
    categoria = crear_categoria(client).json()
    client.put(f"/api/categorias/{categoria['id']}", json={"activa": False})

    response = crear_producto_en_categoria(client, categoria["id"])
    assert response.status_code == 400


def test_filtrar_productos_por_categoria(client):
    cat1 = crear_categoria(client, nombre="Electronica").json()
    cat2 = crear_categoria(client, nombre="Ropa").json()
    crear_producto_en_categoria(client, cat1["id"], sku="SKU-001")
    crear_producto_en_categoria(client, cat2["id"], sku="SKU-002")

    response = client.get("/api/productos", params={"categoria_id": cat1["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["sku"] == "SKU-001"


def test_buscar_productos_por_nombre(client):
    categoria = crear_categoria(client).json()
    crear_producto_en_categoria(client, categoria["id"], sku="SKU-001")

    response = client.get("/api/productos", params={"nombre": "laptop"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    response_sin_match = client.get("/api/productos", params={"nombre": "monitor"})
    assert response_sin_match.status_code == 200
    assert len(response_sin_match.json()) == 0


# --- Regla de negocio: no desactivar categoria con productos activos ---


def test_no_permite_desactivar_categoria_con_productos_activos(client):
    categoria = crear_categoria(client).json()
    crear_producto_en_categoria(client, categoria["id"])

    response = client.delete(f"/api/categorias/{categoria['id']}")
    assert response.status_code == 409


def test_permite_desactivar_categoria_sin_productos_activos(client):
    categoria = crear_categoria(client).json()
    response = client.delete(f"/api/categorias/{categoria['id']}")
    assert response.status_code == 204

    consulta = client.get(f"/api/categorias/{categoria['id']}")
    assert consulta.json()["activa"] is False


def test_permite_desactivar_categoria_si_sus_productos_ya_estan_inactivos(client):
    categoria = crear_categoria(client).json()
    producto = crear_producto_en_categoria(client, categoria["id"]).json()
    client.delete(f"/api/productos/{producto['id']}")

    response = client.delete(f"/api/categorias/{categoria['id']}")
    assert response.status_code == 204
