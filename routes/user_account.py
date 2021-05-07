import traceback
import os
import secrets
from datetime import datetime

from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from models.user_model import UserModel, AdminKeys
from schemas.user_schema import UserSchema, LoginSchema
from config import get_config

CONFIG = get_config(os.getenv("ENV", "development"))


class AdminUser(Resource):

    def get(self):
        """
        generates admin key which is used when creating an admin account
        one key is used for each admin account.
        before creating admin account generate admin key from this enddpont
        """

        try:
            admin_key = secrets.token_hex(16)
            admin_key_data = AdminKeys()
            admin_key_data.admin_key = admin_key
            admin_key_data.created_date = datetime.utcnow()
            admin_key_data.save_object()

            return make_response(jsonify(
                {"admin_key": admin_key, "result": "success"}), 200)
        except Exception as e:
            print(f"Exception in AdminUser GET as {e}")
            return make_response(jsonify([]), 500)

    def post(self):
        """
        create admin user account using admin key generated using above endpoint
        """

        try:
            data = request.get_json()
            user_schema = UserSchema()
            valid_data = user_schema.load(data)
            
            admin_key_data = AdminKeys.search_object(
                admin_key=valid_data['admin_key']).first()

            if not admin_key_data:
                return make_response(jsonify(
                    {"result": "failed", "reason": "invalid admin key"}), 400)
            if admin_key_data.user_name:
                return make_response(jsonify(
                    {"result": "failed", "reason": "admin key already used"}), 400)

            new_user = UserModel()
            new_user.user_name = valid_data['user_name']
            new_user.email = valid_data['email']
            new_user.password = new_user.set_password(valid_data['password'])
            new_user.admin_key = valid_data['admin_key']
            new_user.user_type = 'admin'
            new_user.created_date = datetime.utcnow()
            new_user.save_object()

            admin_key_data.user_name = valid_data['user_name']
            admin_key_data.save_object()

            return make_response(jsonify({"result": "success"}), 201)
        except ValidationError as v_e:
            return v_e.messages, 400

        except IntegrityError as db_e:
            return make_response(jsonify(
                {"result": "failed", "reason": "duplicate user_name/email value"}), 400)

        except Exception as e:
            print(f"Exception in AdminUser POST as {e}")
            return make_response(jsonify([]), 500)


class UserLogin(Resource):

    def post(self):
        try:
            data = request.get_json()
            login_schema = LoginSchema()
            valid_data = login_schema.load(data)

            db_user = UserModel.search_object(
                user_name=valid_data['user_name']).first()

            if not db_user:
                return make_response(jsonify(
                    {"result": "failed", "reason": "user not found"}), 404)

            if not UserModel.check_password(db_user.password, valid_data['password']):
                return make_response(jsonify(
                    {"result": "failed", "reason": "incorrect password"}), 401)

            access_token = create_access_token(
                identity=db_user.id, fresh=True)
            
            return make_response(jsonify(
                {"result": "success", "auth_token": access_token}), 200)
        except ValidationError as v_e:
            return v_e.messages, 400

        except Exception as e:
            print(f"Exception in UserLogin POST as {e}")
            return make_response(jsonify([]), 500)


class BasicUser(Resource):

    def post(self):
        """
        create admin user account using admin key generated using above endpoint
        """

        try:
            data = request.get_json()
            user_schema = UserSchema(exclude=("admin_key",))
            valid_data = user_schema.load(data)
            
            new_user = UserModel()
            new_user.user_name = valid_data['user_name']
            new_user.email = valid_data['email']
            new_user.password = new_user.set_password(valid_data['password'])
            new_user.user_type = 'basic'
            new_user.created_date = datetime.utcnow()
            new_user.save_object()

            return make_response(jsonify({"result": "success"}), 201)
        except ValidationError as v_e:
            return v_e.messages, 400

        except IntegrityError as db_e:
            return make_response(jsonify(
                {"result": "failed", "reason": "duplicate user_name/email value"}), 400)

        except Exception as e:
            print(f"Exception in AdminUser POST as {e}")
            return make_response(jsonify([]), 500)