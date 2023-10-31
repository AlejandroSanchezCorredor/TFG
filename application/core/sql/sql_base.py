from datetime import date, datetime
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_mixins import AllFeaturesMixin

from .sql_output import OutputMixin
from .sql_smart_query import MySmartQueryMixin

Base = declarative_base()


class BaseModel(Base, OutputMixin, AllFeaturesMixin, MySmartQueryMixin):
    """
    This class includes all the common fields in the rest of the
    database tables.
    """
    __abstract__ = True
    __table_args__ = {'mysql_default_charset': 'utf8', 'mysql_collate': 'utf8_bin'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    @staticmethod
    def base_schema():
        schema = {'exclude': ['created_on', 'updated_on']}
        return schema

    # @staticmethod
    # def set_attrib_listener(target, value, old_value, initiator):
    #     try:
    #         if target.__table__.c[initiator.key].type.python_type == datetime:
    #             return datetime.strptime(value, '%Y-%m-%d %H:%M:%SZ')
    #         elif target.__table__.c[initiator.key].type.python_type == date:
    #             return datetime.strptime(value, '%Y-%m-%d').date()
    #
    #         return target.__table__.c[initiator.key].type.python_type(value)
    #     except:
    #         pass
    #
    #     return value
    #
    # @classmethod
    # def __declare_last__(cls):
    #     for column in cls.__table__.columns.values():
    #         if column not in ['id', 'created_on', 'updated_on']:
    #             db.event.listen(
    #                 getattr(cls, column.key),
    #                 "set",
    #                 cls.set_attrib_listener,
    #                 retval=True,
    #             )

