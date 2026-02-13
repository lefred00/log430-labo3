"""
Tests for orders manager
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

import json
import pytest
from store_manager import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    result = client.get('/health-check')
    assert result.status_code == 200
    assert result.get_json() == {'status':'ok'}

import json

def test_stock_flow(client):
    # 1) Créez un article (POST /products)
    product_data = {"name": "Some Item", "sku": "SMOKE-12345", "price": 99.90}
    response = client.post(
        "/products",
        data=json.dumps(product_data),
        content_type="application/json",
    )
    assert response.status_code == 201, response.get_data(as_text=True)

    data = response.get_json()
    assert data["product_id"] > 0
    product_id = data["product_id"]

    # 2) Ajoutez 5 unités au stock de cet article (POST /stocks)
    stock_data = {"product_id": product_id, "quantity": 5}
    response = client.post(
        "/stocks",
        data=json.dumps(stock_data),
        content_type="application/json",
    )
    assert response.status_code in (200, 201), response.get_data(as_text=True)

    # 3) Vérifiez le stock (GET /stocks/:id)  -> attendu: 5
    response = client.get(f"/stocks/{product_id}")
    assert response.status_code == 200, response.get_data(as_text=True)
    stock = response.get_json()
    assert stock["quantity"] == 5, stock

    # 4) Faites une commande de 2 unités (POST /orders)
    order_data = {
        "user_id": 1,
        "items": [{"product_id": product_id, "quantity": 2}],
    }
    response = client.post(
        "/orders",
        data=json.dumps(order_data),
        content_type="application/json",
    )
    assert response.status_code in (200, 201), response.get_data(as_text=True)

    data = response.get_json()
    assert data["order_id"] > 0
    order_id = data["order_id"]

    # 5) Vérifiez le stock encore une fois -> attendu: 3
    response = client.get(f"/stocks/{product_id}")
    assert response.status_code == 200, response.get_data(as_text=True)
    stock = response.get_json()
    assert stock["quantity"] == 3, stock

    # 6) Extra: supprimez la commande (DELETE /orders/:id) -> stock revient à 5
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code in (200, 204), response.get_data(as_text=True)

    response = client.get(f"/stocks/{product_id}")
    assert response.status_code == 200, response.get_data(as_text=True)
    stock = response.get_json()
    assert stock["quantity"] == 5, stock
