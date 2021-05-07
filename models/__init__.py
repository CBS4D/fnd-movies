from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class BasicOperations(object):
    """
    crud on model object
    """

    @classmethod
    def search_object(cls, **kwargs):
        try:
            query = db.session.query(cls).filter_by(**kwargs)
            return query
        except Exception as db_err:
            db.session.rollback()
            raise db_err

    def save_object(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_err:
            db.session.rollback()
            raise db_err

    def update_object(self, many=False):
        try:
            self.updated_date = datetime.utcnow()
            if many:
                db.session.add_all(many)
                db.session.commit()
            else:
                db.session.add(self)
                db.session.commit()
        except Exception as db_err:
            db.session.rollback()
            raise db_err

    def delete_object(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as db_err:
            db.session.rollback()
            raise db_err
