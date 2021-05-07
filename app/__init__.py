# inbuild imports
import os

# external imports
from flask import Flask
from flask_cors import CORS
# from flask_jwt_extended import JWTManager

# our created imports
from config import get_config
from models import db
from schemas import ma
from middleware.auth import jwt

def create_app(config_name):
    """
    Flask app object creation and attaching different extensions to it
    accept config name for flask app config
    returns flask app object with extensions
    """

    app = Flask(__name__)
    CORS(app)
    # jwt = JWTManager(app)
    jwt.init_app(app)
    app.config.update(get_config(config_name))
    # postgres database url for heroku deployment
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    
    #bind database objectc to flask app
    db.init_app(app)

    #bind marshmallow object to flask app
    ma.init_app(app)

    # add resources to flask app
    connect_resources(app)

    # using app context it will create tables
    # of all mentioned models if not created already
    with app.app_context():
        db.create_all()

    return app


def connect_resources(app):
    """
    Import different blueprints and register it to flask app
    """

    from app.api import api_bp as api_module
    app.register_blueprint(api_module)

