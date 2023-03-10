from app import db
from app.routes.validation_functions import validate_request_and_create_obj, validate_current_user, validate_model_by_id
from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order
from app.models.cart import Cart
from app.models.cart_product import CartProduct
from flask import Blueprint, jsonify, abort, make_response, request
import stripe
import os

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")
stripe.api_key="sk_test_51McZSQAmweu3gL544pjHvx0hhbgTnzEeUDwUKP9ufhxKhaZRX8rDqKO4llb3xgZBIAqeLLeJFqrVDP45tF8NyeJD008l3rIZe4"



##################
# CUSTOMER ROUTES #
##################

# READ
@customers_bp.route("/<username>", methods=["GET"])
def get_one_seller_by_id(username):
    username = username.strip().replace("-", " ")
    customer = Customer.validate_by_username_and_get_entry(username)
    if not customer:
        abort(make_response({"message": f"Customer {username} not found"}, 404))
    return customer.to_dict()

# UPDATE
@customers_bp.route("/<username>", methods=["PUT"])
def update_one_customer(username):
    current_user = validate_current_user(username)
    request_body = request.get_json()
    try:
        current_user.username = request_body["username"]
        current_user.first_name = request_body["first_name"]
        current_user.last_name = request_body["last_name"]
        current_user.email = request_body["email"]
        current_user.address_1 = request_body["address_1"]
        current_user.city = request_body["city"]
        current_user.region = request_body["region"]
        current_user.postal_code = request_body["postal_code"]
    except KeyError as e:
        key = str(e).strip("\'")
        abort(make_response(jsonify({"message": f"Request body must include {key}."}), 400))
    
    db.session.commit()
    return make_response(jsonify(f"Customer {username} successfully updated."), 200)

# DELETE
@customers_bp.route("/<username>", methods=["DELETE"])
def delete_one_customer(username):
    current_user = validate_current_user(username)

    db.session.delete(current_user)
    db.session.commit()
    return make_response(jsonify(f"Customer {username} successfully deleted."), 200)

##################
# CART/ORDER ROUTES #
##################

# READ
@customers_bp.route("/<username>/cart", methods=["GET"])
def get_user_cart(username):
    current_user = validate_current_user(username)
    return current_user.get_cart_items()

# CREATE - ADD TO CART
@customers_bp.route("/<username>/cart/<int:product_id>", methods=["POST"])
def add_product_to_cart(username, product_id):
    current_user = validate_current_user(username)
    if not current_user.cart:
        current_user.cart = Cart()
    product = validate_model_by_id(Product, product_id)
    product.update_inventory()

    if product.quantity < 0:
            return make_response({"message": "Item is out of stock"}), 400

    # check if item is in cart & increase quantity accordingly
    cart_product = CartProduct.query.filter_by(cart_id=current_user.cart.id, product_id=product.id).first()
    print(cart_product)
    if cart_product:
        cart_product.quantity += 1
    else:
        cart_product = CartProduct(
            cart_id=current_user.cart.id,
            product_id=product.id,
            quantity=1
        )
    db.session.add(cart_product)
    db.session.commit()
    # TODO - decide on appropriate response body
    return {
        "cart_id": cart_product.cart_id,
        "product_id": cart_product.product_id,
        "available_inventory": product.quantity,
        "price": product.price
        }, 200

# DELETE - REMOVE FROM CART
@customers_bp.route("/<username>/cart/<int:product_id>", methods=["DELETE"])
def remove_product_from_cart(username, product_id):
    current_user = validate_current_user(username)
    product = validate_model_by_id(Product, product_id)
    cart_item = CartProduct.query.filter_by(
        cart_id=current_user.cart.id,
        product_id=product.id
    ).first()

    if cart_item:
        db.session.delete(cart_item)
    else:
        abort(make_response({"message": f"Cart item not found"}, 404))
    
    product.quantity += 1
    db.session.commit()
    return make_response(jsonify({"message": f"Product {product.name} successfully removed from {current_user.username}'s cart."}), 200)

# CHECKOUT
@customers_bp.route("/<username>/cart/checkout", methods=["POST"])
def checkout(username):
    current_user = validate_current_user(username)
    cart = current_user.cart
    if cart == []:
        abort(make_response({"message": f"Cart is empty"}, 404))
    
    try:
        cart_items = current_user.get_cart_items()
        line_items= []
        for item in cart_items:
            line_items.append({
                "price_data": {
                    "product_data": {
                        "name": item["name"],
                    },
                    "unit_amount": item["price"] * 100,
                    "currency": "usd",
                },
                "quantity": item["quantity"]
            })
        checkout_session = stripe.checkout.Session.create(
            line_items=line_items,
            mode="payment",
            success_url= os.environ.get("FRONTEND_URL") + f"/customers/{username}/order/success",
            cancel_url= os.environ.get("FRONTEND_URL") +  f"/customers/{username}/order/cancel",
        )
        return checkout_session.url

    except Exception as e:
        abort(make_response({"message": f"Could not complete checkout"}, 500))

# CONFIRM CHECKOUT
@customers_bp.route("/<username>/order/success", methods=["POST"])
def confirm_checkout(username):
    current_user = Customer.validate_by_username_and_get_entry(username)
    cart = current_user.cart
    if cart == []:
        abort(make_response({"message": f"Cart is empty"}, 404))
    
    cart.place_order()
    current_user.cart = Cart(customer_id=current_user.id)
    db.session.commit()
    return make_response(jsonify({"message": "Checkout complete."}), 200)
