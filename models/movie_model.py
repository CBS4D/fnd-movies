from datetime import datetime as dt

from models import db, BasicOperations


movie_genre = db.Table('movie_genre_details', db.Model.metadata,
    db.Column('movie_id', db.Integer, db.ForeignKey('movie_details.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre_details.id'))
)


class MovieModel(db.Model, BasicOperations):

    __tablename__ = 'movie_details'

    __table_args__ = (
        db.UniqueConstraint('movie_name', 'director_name'),
      )
    
    id = db.Column(db.Integer, primary_key=True, index=True)
    movie_name = db.Column(db.String)
    director_name = db.Column(db.String)
    imdb_score = db.Column(db.Numeric)
    popularity = db.Column(db.Numeric)
    created_date = db.Column(db.DateTime, default=dt.utcnow)
    updated_date = db.Column(db.DateTime)

    genre = db.relationship("GenreModel",
        secondary=movie_genre, backref=db.backref('movies'))

    

class GenreModel(db.Model, BasicOperations):

    __tablename__ = "genre_details"

    id = db.Column(db.Integer, primary_key=True, index=True)
    genre_name = db.Column(db.String)

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

