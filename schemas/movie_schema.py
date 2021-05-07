from collections.abc import Iterable

from schemas import ma
from marshmallow import fields, validate, ValidationError, post_dump, pre_dump


class GenreSchema(ma.Schema):

    class Meta:
        fields = ("id", "genre_name")
        load_only = ("id",)

    id = fields.Int(required=True)
    genre_name = fields.Str(required=True)

    @post_dump(pass_many=True)
    def return_as_list(self, data, **kwargs):
        list_format = []
        for obj in data:
            list_format.append(obj['genre_name'])
        return list_format

class MovieSchema(ma.Schema):

    class Meta:
        fields = ("id", "movie_name", "imdb_score", "director_name",
                  "popularity", "genre", "genres")

    id = fields.Int(required=True)
    movie_name = fields.Str(required=True)
    director_name = fields.Str(required=True)
    imdb_score = fields.Float(required=True)
    popularity = fields.Float(required=True)
    genre = fields.List(fields.Str, required=True)

    @pre_dump(pass_many=True)
    def add_genre_data(self, data, **kwargs):
        if isinstance(data, Iterable):
            genre_schema = GenreSchema(many=True)
            for movie in data:
                movie.genres = genre_schema.dump(movie.genre)

        return data


class MovieUpdateSchema(ma.Schema):

    class Meta:
        fields = ("id", "movie_name", "imdb_score", "director_name",
                  "popularity", "genre", "genres")

    id = fields.Int(required=True)
    movie_name = fields.Str(required=True)
    director_name = fields.Str(required=True)
    imdb_score = fields.Float(required=True)
    popularity = fields.Float(required=True)
    genre = fields.Nested(GenreSchema, required=True)

    @pre_dump(pass_many=True)
    def add_genre_data(self, data, **kwargs):
        if isinstance(data, Iterable):
            genre_schema = GenreSchema(many=True)
            for movie in data:
                movie.genres = genre_schema.dump(movie.genre)

        return data