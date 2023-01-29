from app import db
from app.models.seller import Seller
from flask import Blueprint, jsonify, abort, make_response, request

sellers_bp = Blueprint("sellers", __name__, url_prefix="/sellers")

# TODO - generalize this validate model fn
def validate_seller(cls, request_body):
    try:
        new_seller = cls.from_dict(request_body)
    except KeyError as e:
        # strip one pair of quotes off key
        key = str(e).strip("\'")
        abort(make_response(jsonify({"message": f"Request body must include {key}."}), 400))
    return new_seller


@sellers_bp.route("", methods=["POST"])
def create_seller():
    request_body = request.get_json()
    new_seller = validate_seller(Seller, request_body)

    db.session.add(new_seller)
    db.session.commit()

    return make_response(jsonify(f"Seller {new_seller.first_name} {new_seller.last_name}, owner of {new_seller.store_name} successfully created"), 201)

@sellers_bp.route("", methods=["GET"])
def get_all_sellers():
    sellers = Seller.query.all()
    sellers_response = []
    for seller in sellers:
        sellers_response.append(seller.to_dict())
    return jsonify(sellers_response)

# TODO - generalize this validate by id fn
def validate_id_and_get_entry(seller_id):
    try:
        seller_id = int(seller_id)
    except:
        abort(make_response({"message": f"Seller ID {seller_id} invalid"}, 400))
    
    seller = Seller.query.get(seller_id)
    if not seller:
        abort(make_response({"message": f"Seller ID {seller_id} not found"}, 404))
    
    return seller
    
    

@sellers_bp.route("/<seller_id>", methods=["GET"])
def get_one_seller_by_id(seller_id):
    seller = validate_id_and_get_entry(seller_id)
    return seller.to_dict()