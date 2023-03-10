from app.models.seller import Seller
from app.models.product import Product
import pytest

SELLER_ID = 1
SELLER_STORE_NAME = "Green Acres"
SELLER_STORE_DESCRIPTION = "An apple orchard that specializes in homemade pies, jams, and cider."
SELLER_FIRST_NAME = "Lila"
SELLER_LAST_NAME = "Parker"
SELLER_EMAIL = "lilaparker@fakemail.com"
SELLER_PASSWORD = "password"
SELLER_ADDRESS_1 = "278 Armstrong Rd"
SELLER_CITY = "Hudson"
SELLER_REGION = "New York"
SELLER_POSTAL_CODE = "12534"

##################
# SELLER ROUTES #
##################

# READ
def test_get_sellers_none_saved(client):
    # Act
    response = client.get("/sellers")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body == []

def test_get_sellers(client, one_seller):
    # Act
    response = client.get("/sellers")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body[0]["store_name"] == SELLER_STORE_NAME

def test_get_one_seller_by_store_name(client, one_seller):
    # Act
    response = client.get("/sellers/Green%20Acres")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body == {
        "id": SELLER_ID,
        "store_name": SELLER_STORE_NAME,
        "store_description": SELLER_STORE_DESCRIPTION,
        "first_name": SELLER_FIRST_NAME,
        "last_name": SELLER_LAST_NAME,
        "email": SELLER_EMAIL,
        "address_1": SELLER_ADDRESS_1,
        "city": SELLER_CITY,
        "region": SELLER_REGION,
        "postal_code": SELLER_POSTAL_CODE
    }

def test_get_one_seller_nonexistent_store_name(client, one_seller):
    # Act
    response = client.get("/sellers/Fake%20Store")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert "message" in response_body
    assert "Seller Fake Store not found" in response_body["message"]

# UPDATE
def test_update_one_seller(client, seller_access_token):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.put("/sellers/Green%20Acres", headers=headers, json={
        "store_name": "A New Store Name",
        "store_description": SELLER_STORE_DESCRIPTION,
        "first_name": SELLER_FIRST_NAME,
        "last_name": SELLER_LAST_NAME,
        "email": SELLER_EMAIL,
        "address_1": SELLER_ADDRESS_1,
        "city": SELLER_CITY,
        "region": SELLER_REGION,
        "postal_code": SELLER_POSTAL_CODE
    })
    response_body = response.get_json()
    # Assert
    assert response.status_code == 200
    assert response_body == f"Seller {SELLER_FIRST_NAME} {SELLER_LAST_NAME}, owner of A New Store Name successfully updated."

    updated_seller = Seller.query.get(1)

    assert updated_seller
    assert updated_seller.store_name == "A New Store Name"

def test_update_one_seller_fails_if_unauthorized(client, seller_access_token):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.put("/sellers/5", headers=headers, json={
        "store_name": "A New Store Name",
        "store_description": SELLER_STORE_DESCRIPTION,
        "first_name": SELLER_FIRST_NAME,
        "last_name": SELLER_LAST_NAME,
        "email": SELLER_EMAIL,
        "address_1": SELLER_ADDRESS_1,
        "city": SELLER_CITY,
        "region": SELLER_REGION,
        "postal_code": SELLER_POSTAL_CODE
    })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 403
    assert "message" in response_body
    assert "Action forbidden" in response_body["message"]

def test_update_one_seller_needs_all_fields(client, seller_access_token):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.put("/sellers/Green%20Acres", headers=headers, json={
        "store_name": SELLER_STORE_NAME,
        "store_description": SELLER_STORE_DESCRIPTION,
        "first_name": SELLER_FIRST_NAME,
        "last_name": SELLER_LAST_NAME,
        "email": SELLER_EMAIL,
        "address_1": SELLER_ADDRESS_1,
        "city": SELLER_CITY,
        "postal_code": SELLER_POSTAL_CODE
    })
    response_body = response.get_json()
    # Assert
    assert response.status_code == 400
    assert response_body["message"] == f"Request body must include region."

# DELETE
def test_delete_one_seller(client, seller_access_token):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.delete("/sellers/Green%20Acres", headers=headers)
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body == f"Seller {SELLER_FIRST_NAME} {SELLER_LAST_NAME}, owner of {SELLER_STORE_NAME} successfully deleted."
    assert Seller.query.get(1) == None

def test_delete_fails_if_unauthorized(client, seller_access_token):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.delete("/sellers/5", headers=headers)
    response_body = response.get_json()

    # Assert
    assert response.status_code == 403
    assert "message" in response_body
    assert "Action forbidden" in response_body["message"]

##################
# NESTED PRODUCT ROUTES #
##################

# CREATE
def test_create_one_product(client, seller_access_token):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.post("/sellers/Green%20Acres/products", headers=headers, json={
        "name": "Sweet Corn",
        "price": 3,
        "quantity": 20,
        "image_file": None,
        "description": "Delicious sweet corn!"
    })
    response_body = response.get_json()
    # Assert
    assert response.status_code == 201
    assert response_body == f"Product Sweet Corn from {SELLER_STORE_NAME} successfully created."

    new_product = Product.query.get(1)

    assert new_product
    assert new_product.price == 3
    assert new_product.quantity == 20
    assert new_product.image_file == "default.jpg"
    assert new_product.description == "Delicious sweet corn!"
    assert new_product.seller.store_name == "Green Acres"

def test_create_one_product_must_contain_name(client, seller_access_token):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.post("/sellers/Green-Acres/products", headers=headers, json={
        "price": 3,
        "quantity": 20,
        "image_file": None,
        "description": "Delicious sweet corn!"
    })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 400
    assert "message" in response_body
    assert "Request body must include name" in response_body["message"]
    assert Product.query.all() == []

# READ
def test_get_all_products_from_one_seller(client, one_saved_product):
    # Act
    response = client.get("/sellers/Green%20Acres/products")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body[0]["name"] == "Sweet Corn"


# UPDATE
def test_update_one_product(client, seller_access_token, one_saved_product):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.put("/sellers/Green%20Acres/products/1", headers=headers, json={
        "name": "Sweet Corn",
        "price": 5,
        "quantity": 20,
        "image_file": None,
        "description": "Delicious sweet corn!"
    })
    response_body = response.get_json()
    # Assert
    assert response.status_code == 200
    assert response_body == f"Product Sweet Corn from {SELLER_STORE_NAME} successfully updated."

    product = Product.query.get(1)

    assert product
    assert product.price == 5

def test_update_one_product_need_jwt(client, one_saved_product):
    # Act
    response = client.put("/sellers/Green%20Acres/products/1",  json={
        "name": "Sweet Corn",
        "price": 5,
        "quantity": 20,
        "image_file": None,
        "description": "Delicious sweet corn!"
    })
    response_body = response.get_json()
    # Assert
    assert response.status_code == 401
    assert "Missing JWT" in response_body["msg"]

def test_update_one_product_need_correct_jwt(client, seller_access_token, one_saved_product):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.put("/sellers/Happy%20Cows/products/1", headers=headers, json={
        "name": "Sweet Corn",
        "price": 5,
        "quantity": 20,
        "image_file": None,
        "description": "Delicious sweet corn!"
    })
    response_body = response.get_json()
    # Assert
    assert response.status_code == 403

def test_update_one_nonexistent_product_fails(client, seller_access_token):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.put("/sellers/Green%20Acres/products/2", headers=headers, json={
        "name": "Sweet Corn",
        "price": 5,
        "quantity": 20,
        "image_file": None,
        "description": "Delicious sweet corn!"
    })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert response_body["message"] == f"Product not found"

def test_update_one_product_need_product_name(client, seller_access_token, one_saved_product):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.put("/sellers/Green%20Acres/products/1", headers=headers, json={
        "price": 5,
        "quantity": 20,
        "image_file": None,
        "description": "Delicious sweet corn!"
    })
    response_body = response.get_json()
    # Assert
    assert response.status_code == 400
    assert response_body["message"] == f"Request body must include name."

# DELETE 
def test_delete_one_product(client, seller_access_token, one_saved_product):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.delete("/sellers/Green%20Acres/products/1", headers=headers)
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body == f"Product Sweet Corn from {SELLER_STORE_NAME} successfully deleted."
    assert Product.query.get(1) == None

def test_delete_one_product_need_jwt(client, one_saved_product):
    # Act
    response = client.delete("/sellers/Green%20Acres/products/1")
    response_body = response.get_json()
    # Assert
    assert response.status_code == 401
    assert "Missing JWT" in response_body["msg"]

def test_delete_one_product_need_correct_jwt(client, seller_access_token, one_saved_product):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.delete("/sellers/Happy%20Cows/products/1", headers=headers)
    response_body = response.get_json()
    # Assert
    assert response.status_code == 403


def test_delete_one_nonexistent_product_fails(client, seller_access_token):
    # Act
    headers = {"Authorization": f"Bearer {seller_access_token}"}
    response = client.delete("/sellers/Green%20Acres/products/2", headers=headers)
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert response_body["message"] == f"Product not found"