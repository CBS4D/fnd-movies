import traceback

from functools import wraps

from flask_jwt_extended import JWTManager, get_jwt
from models.user_model import UserModel

jwt = JWTManager()


def is_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        check in database if a user account type is admin/basic
        """
        
        try:
            user_id = get_jwt().get('sub')

            if UserModel.search_object(id=user_id).first().user_type != 'admin':
                return {"status":"Unauthorized"},401
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return {"status":"Unauthorized"},401
    return wrapper
