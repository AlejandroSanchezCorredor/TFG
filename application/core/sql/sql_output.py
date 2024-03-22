import collections
import enum
import logging
from sqlalchemy import inspect
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import DeclarativeMeta
from datetime import datetime, date


class OutputMixin(object):
    __to_dict_allow_none__ = False
    __to_dict_ignore_fields__ = []
    __to_dict_ignore_unloaded__ = False

    def __iter__(self):
        return self.to_dict().items()

    def to_dict(self, rel=True, backref=[]):
        # if not backref:
        #     logging.warning('Calling deprecated to_dict method for table {}'.format(self.__table__))
        ins = inspect(self)
        res = {column.key: getattr(self, attr)
               for attr, column in self.__mapper__.c.items() if attr not in self.__to_dict_ignore_fields__}
        if not self.__to_dict_allow_none__:
            res = {key: value for key, value in res.items() if value is not None}

        if rel:
            for attr, relation in self.__mapper__.relationships.items():
                # Avoid recursive loop between to tables.
                if attr in self.__to_dict_ignore_fields__ \
                        or relation.mapper.local_table in backref \
                        or (self.__to_dict_ignore_unloaded__ and attr in ins.unloaded):
                    continue
                value = getattr(self, attr)
                if value is None:
                    if self.__to_dict_allow_none__:
                        res[relation.key] = None
                elif isinstance(value.__class__, DeclarativeMeta):
                    res[relation.key] = value.to_dict(backref=backref + [self.__table__])
                else:
                    res[relation.key] = [i.to_dict(backref=backref + [self.__table__]) for i in value]
        return res

    def from_schema(self, schema={}):
        def get_value(column):
            value = getattr(self, column)
            if isinstance(value, datetime):
                return f'{value.isoformat()}Z'
            elif isinstance(value, date):
                return f'{value.isoformat()}'
            elif isinstance(value, enum.Enum):
                return value.value
            return value

        def get_relation(key):
            value = getattr(self, key)
            if value is None:
                return None
            elif isinstance(value.__class__, DeclarativeMeta):
                return value.from_schema(schema['relations'][key])
            elif isinstance(value, collections.Iterable):
                return [x.from_schema(schema['relations'][key]) for x in value]

        # Include custom hybrid_properties
        # def get_default_schema(self):
        #     _keys = list(self.__mapper__.c.keys())
        #     for key, prop in inspect(self.__class__).all_orm_descriptors.items():
        #         if isinstance(prop, hybrid_property):
        #             _keys.append(key)
        #     return _keys

        # include = schema['include'] if 'include' in schema else get_default_schema(self)

        include = schema['include'] if 'include' in schema else list(self.__mapper__.c.keys())
        exclude = schema.get('exclude', [])
        properties = schema.get('properties', [])
        columns = [x for x in include + properties if x not in exclude]
        # columns = [x for x in include if x not in exclude]
        relations = schema.get('relations', {})

        fields = {c: get_value(c) for c in columns}
        relations = {c: get_relation(c) for c in relations}
        fields.update(relations)

        return fields