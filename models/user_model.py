from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, BasicOperations


class AdminKeys(db.Model, BasicOperations):

    __tablename__ = 'admin_keys'

    id = db.Column(db.Integer, primary_key=True, index=True)
    admin_key = db.Column(db.String)
    user_name = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=dt.utcnow)

class UserModel(db.Model, BasicOperations):

    __tablename__ = 'user_details'

    id = db.Column(db.Integer, primary_key=True, index=True)
    user_name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    user_type = db.Column(db.String)
    admin_key = db.Column(db.String)
    created_date = db.Column(db.DateTime, default=dt.utcnow)
    updated_date = db.Column(db.DateTime)
    deleted = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        return generate_password_hash(password)

    @staticmethod
    def check_password(db_password, user_password):
        return check_password_hash(db_password, user_password)
