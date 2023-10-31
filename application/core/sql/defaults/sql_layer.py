from application.core.http.http_error import HTTPError
from application.core.sql.sql_base import BaseModel
from application.core.sql.sql_session import db_get_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class SQLLayer(object):
    def __call__(self, orig_func):

        def open_db_connection():
            BaseModel.set_session(db_get_session())

        def close_db_connection():
            BaseModel.session.close()

        def wrapper(*args, **kwargs):
            open_db_connection()
            try:
                res = orig_func(*args, **kwargs)
                BaseModel.session.commit()
                return res
            except (NoResultFound, MultipleResultsFound):
                raise HTTPError(404)
            finally:
                close_db_connection()

        return wrapper

