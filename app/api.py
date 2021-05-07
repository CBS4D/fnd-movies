"""
Api and resource binding
"""

from flask import Blueprint
from flask_restful import Api
from routes.user_account import AdminUser, UserLogin, BasicUser
from routes.movies import Movies, MoviesList
# Create Blueprint:

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_bp, catch_all_404s=True)

# Add API Routes:

api.add_resource(AdminUser, '/admin-user', methods=['POST'], endpoint='create admin account')
api.add_resource(AdminUser, '/admin-key', methods=['GET'], endpoint='create admin key')
api.add_resource(UserLogin, '/login', methods=['POST'], endpoint='admin login')

api.add_resource(BasicUser, '/user', methods=['POST'], endpoint='create basic user account')


api.add_resource(Movies, '/movie', methods=['GET'], endpoint='retrieve movie data')
api.add_resource(Movies, '/movie', methods=['POST'], endpoint='store movie data')
api.add_resource(Movies, '/movie', methods=['PUT'], endpoint='update movie data')
api.add_resource(Movies, '/movie', methods=['DELETE'], endpoint='delete movie data')

api.add_resource(MoviesList,  '/movies', methods=['GET'], endpoint='get requested/all movies data')
