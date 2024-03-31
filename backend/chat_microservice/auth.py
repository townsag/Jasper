import functools

from flask import (
    Blueprint, g, jsonify, request
)
from werkzeug.security import check_password_hash, generate_password_hash

from chat_microservice.db import check_name_unique, insert_new_user, select_user

from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import get_jwt, jwt_required

from chat_microservice.db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# @bp.before_app_request
# def load_logged_in_user():
#     user_id = session.get('user_id')

#     if user_id is None:
#         g.user = None
#     else:
#         g.user = get_db().execute(
#             'SELECT * FROM user WHERE id = ?', (user_id,)
#         ).fetchone()


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if "username" not in data:
        return jsonify({"msg": "request json must include \"username\""}), 400
    if "password" not in data:
        return jsonify({"msg": "request json must include \"password\""}), 400
    username = data["username"]
    password = data["password"]
    # ToDo: add some cleaning to prevent sql injection attacks
    if not check_name_unique(username=username):
        return jsonify({"msg":"username unavailable"}), 422

    password_hash = generate_password_hash(password)
    user_id = insert_new_user(username=username, password_hash=password_hash)

    # Create an access token with custom claims
    access_token = create_access_token(
        identity=user_id, additional_claims={'username': username}
    )

    return jsonify(access_token=access_token), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if "username" not in data:
        return jsonify({"msg": "request json must include \"username\""}), 400
    if "password" not in data:
        return jsonify({"msg": "request json must include \"password\""}), 400
    username = data["username"]
    password = data["password"]

    data = select_user(username=username)
    if not data:
        return jsonify({"msg":"no user with this username"}), 401
    if not check_password_hash(data["password"],password):
        return jsonify({"msg":"username or password incorrect"}), 401
    
    user_id = data["user_id"]
    username = data["username"]
    access_token = create_access_token(
        identity=user_id, additional_claims={'username': username}
    )
    return jsonify(access_token=access_token), 200


@auth_bp.route("/whoami", methods=["GET"])
@jwt_required()
def who_am_i():
    username = get_jwt()["username"]
    return jsonify({"username": username}), 200

