import traceback
import os
from datetime import datetime
from copy import deepcopy

from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from models import db
from models.movie_model import MovieModel, GenreModel
from schemas.movie_schema import MovieSchema, GenreSchema, MovieUpdateSchema
from middleware.auth import is_admin
from config import get_config

CONFIG = get_config(os.getenv("ENV", "development"))


class Movies(Resource):

    # method_decorators = [is_admin, jwt_required()]

    def get_existing_genres(self, genres):
        try:
            result = GenreModel.query.filter(GenreModel.genre_name.in_(genres)).all()
            return [row.to_json() for row in result], result
        except Exception as e:
            raise e

    def get(self):
        """
        get single movie record for provided movie id
        request argument: id=<integere>
        """

        try:
            movie_id = request.args.get('id')
            if not movie_id:
                return make_response(jsonify(
                {"result": "failed", "reason": "no data provided"}), 400)

            db_data = MovieModel.search_object(id=movie_id).first()
            
            if not db_data:
                return make_response(jsonify(
                {"result": "failed", "reason": "no record found"}), 404)

            movie_schema = MovieSchema()
            genre_schema = GenreSchema(many=True)
            result = movie_schema.dump(db_data)
            result['genre'] = genre_schema.dump(db_data.genre)

            return make_response(jsonify(result), 200)
        except ValidationError as v_e:
            return v_e.messages, 400

        except IntegrityError as db_e:
            return make_response(jsonify(
                {"result": "failed", "reason": "duplicate user_name/email value"}), 400)

        except Exception as e:
            print(f"Exception in Movies GET as {e}")
            return make_response(jsonify([]), 500)

    def post(self):
        """
        create movie record for the data provided by the user
        """

        try:
            data = request.get_json()
            movie_schema = MovieSchema(exclude=("id","genres"))
            valid_data = movie_schema.load(data)
            
            movie_model = MovieModel()
            movie_model.movie_name = valid_data["movie_name"]
            movie_model.director_name = valid_data["director_name"]
            movie_model.imdb_score = valid_data["imdb_score"]
            movie_model.popularity = valid_data["popularity"]
            # movie_model.genre = valid_data["genre"]
            movie_model.created_date = datetime.utcnow()

            genres = [genre.strip().lower() for genre in valid_data["genre"]]
            json_genres, db_genre = self.get_existing_genres(genres)

            genre_copy = deepcopy(genres)
            for genre in genres:
                for gnr in json_genres:
                    if genre == gnr['genre_name']:
                        genre_copy.remove(genre)
                        break

            # new genres
            for genre in genre_copy:
                genre_model = GenreModel()
                genre_model.genre_name = genre
                movie_model.genre.append(genre_model)

            # already present genres
            for gnr in db_genre:
                movie_model.genre.append(gnr)
            movie_model.save_object()

            return make_response(jsonify({"result": "success", "id": movie_model.id}), 201)
        except ValidationError as v_e:
            return v_e.messages, 400

        except IntegrityError as db_e:
            return make_response(jsonify(
                {"result": "failed", "reason": "duplicate movie_name/director_name value"}), 400)

        except Exception as e:
            print(f"Exception in Movies POST as {e}")
            return make_response(jsonify([]), 500)

    def put(self):
        """
        update movie record data if it already exists, with new data provided by user
        """

        try:
            data = request.get_json()
            movie_schema = MovieUpdateSchema(partial=True)
            valid_data = movie_schema.load(data)
            
            existing_movie_record = MovieModel.search_object(id=valid_data["id"]).first()
            existing_movie_record.delete_object()
            existing_movie_dump = movie_schema.dump(existing_movie_record)

            if not existing_movie_record:
                return make_response(jsonify(
                {"result": "failed", "reason": "record not found to update"}), 404)
            
            new_genres = valid_data.get('genres')
            if new_genres:
                new_genres = [genre.strip().lower() for genre in valid_data["genres"]]
                del valid_data['genres']
                json_genres, db_genre = self.get_existing_genres(new_genres)

            new_movie_record = MovieModel()
            for column_name, value in existing_movie_dump.items():
                setattr(new_movie_record, column_name, value)

            for column_name, value in valid_data.items():
                setattr(new_movie_record, column_name, value)

            
            if new_genres:
                genre_copy = deepcopy(new_genres)

                for genre in new_genres:
                    for gnr in json_genres:
                        if genre == gnr['genre_name']:
                            genre_copy.remove(genre)
                            break
                # new genres
                for genre in genre_copy:
                    genre_model = GenreModel()
                    genre_model.genre_name = genre
                    new_movie_record.genre.append(genre_model)

                # already present genres
                for gnr in db_genre:
                    new_movie_record.genre.append(gnr)

            new_movie_record.update_object()
            
            return make_response(jsonify({"result": "success"}), 200)
        except ValidationError as v_e:
            return v_e.messages, 400

        except IntegrityError as db_e:
            return make_response(jsonify(
                {"result": "failed", "reason": "movie_name/director_name value"}), 400)

        except Exception as e:
            print(f"Exception in Movies PUT as {e}")
            return make_response(jsonify([]), 500)

    def delete(self):
        """
        delete single movie record for the provided id in url.
        request argument: id=<integere>
        """

        try:
            movie_id = request.args.get('id')
            if not movie_id:
                return make_response(jsonify(
                {"result": "failed", "reason": "no data provided"}), 400)

            db_data = MovieModel.search_object(id=movie_id).first()
            if not db_data:
                return make_response(jsonify(
                {"result": "failed", "reason": "no record found"}), 404)
            db_data.delete_object()
            return make_response(jsonify({"result": "success"}), 200)
        except ValidationError as v_e:
            return v_e.messages, 400

        except IntegrityError as db_e:
            return make_response(jsonify(
                {"result": "failed", "reason": "duplicate movie_name/director_name value"}), 400)

        except Exception as e:
            print(f"Exception in Movies DELETE as {e}")
            return make_response(jsonify([]), 500)


class MoviesList(Resource):

    def get_result(self, queries, page_number, page_size):
        try:
            result = MovieModel.query.filter(
                *queries
            ).paginate(page_number, page_size, False)
            return result.items, result.total
        except Exception as e:
            raise e

    def get(self):
        """
        get multiple movie record for the filters provided by user
        """

        try:
            movie_name = request.args.get('name')
            director_name = request.args.get('director')
            imdb_score = request.args.get('score')
            popularity = request.args.get('popularity')
            page_number = int(request.args.get("page_number", 1))
            page_size = int(request.args.get("page_size", 10))
            genre = request.args.get('genre')

            queries = []
            if movie_name:
                queries.append(MovieModel.movie_name.ilike(f"%{movie_name}%"))
            if director_name:
                queries.append(MovieModel.director_name.ilike(f"%{director_name}%"))
            if imdb_score:
                queries.append(MovieModel.imdb_score >= imdb_score)
            if popularity:
                queries.append(MovieModel.popularity >= popularity)
            if genre:
                queries.append(
                    MovieModel.genre.any(genre_name=genre.strip().lower()))

            data, total = self.get_result(queries, page_number, page_size)

            movie_schema = MovieSchema(many=True, exclude=('genre',))
            result = movie_schema.dump(data)

            return make_response(jsonify({"total": total, "result": result}), 200)
        except ValidationError as v_e:
            return v_e.messages, 400

        except IntegrityError as db_e:
            return make_response(jsonify(
                {"result": "failed", "reason": "duplicate movie_name/director_name value"}), 400)

        except Exception as e:
            print(f"Exception in Movies GET as {e}")
            return make_response(jsonify([]), 500)
