import copy
import inspect
import logging
import re
import json


from application.core.configuration_loader import get_configuration
from pynamodb.attributes import *
from pynamodb.attributes import MapAttribute, DynamicMapAttribute, UnicodeSetAttribute, UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model
from datetime import datetime
import pytz


configuration = get_configuration()
logger = logging.getLogger()


class BaseModel(Model):
    """
    This class includes all the common fields in the rest of the
    database tables.
    """
    class Meta:
        region = configuration.AWS_REGION
        abstract = True

    creation_datetime = UTCDateTimeAttribute(null=False, default=datetime.now(pytz.utc))
    update_datetime = UTCDateTimeAttribute(null=False, default=datetime.now(pytz.utc))

    @staticmethod
    def base_schema():
        schema = {'exclude': ['creation_datetime', 'update_datetime']}
        return schema

    def save(self, *args, **kwargs):
        if getattr(self.__class__, 'update_datetime', None):
            self.update_datetime = datetime.now(pytz.utc)
        super(BaseModel, self).save(*args, **kwargs)

    def update(self, actions, *args, **kwargs):
        if getattr(self.__class__, 'update_datetime', None):
            update_datetime = datetime.now(pytz.utc)
            actions.append(
                self.__class__.update_datetime.set(update_datetime)
            )
        super(BaseModel, self).update(actions, *args, **kwargs)

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def from_schema(self, schema):
        def get_value(column):
            value = getattr(self, column)
            attr_instance = self.get_attributes()[column]
            return self._attr2obj(value)

        include = schema['include'] \
            if 'include' in schema else list(self.attribute_values)
        exclude = schema.get('exclude', [])

        columns = [x for x in include if x not in exclude]
        ret_dict = {c: get_value(c) for c in columns}

        return ret_dict

    def to_dict(self):
        print("El referencias")
        ret_dict = {}

        for name, attr_value in self.attribute_values.items():
            ret_dict[name] = self._attr2obj(attr_value)

        return ret_dict

    def _attr2obj(self, attr):
        # compare with list class. It is not ListAttribute.
        if isinstance(attr, list):
            _list = []
            for l in attr:
                _list.append(self._attr2obj(l))
            return _list
        elif isinstance(attr, set):
            return list(attr)
        elif isinstance(attr, MapAttribute):
            _dict = {}
            for k, v in attr.attribute_values.items():
                _dict[k] = self._attr2obj(v)
            if isinstance(attr, DynamicMapAttribute):
                _dict.pop('attribute_values', None)
            return _dict
        elif isinstance(attr, datetime):
            return attr.isoformat()
        else:
            return attr

    # https://github.com/pynamodb/PynamoDB/issues/152
    def __iter__(self):
        for name, attr in self.get_attributes().items():
            if isinstance(attr, MapAttribute):
                if getattr(self, name):
                    yield name, getattr(self, name).as_dict()
            elif isinstance(attr, UTCDateTimeAttribute):
                if getattr(self, name):
                    yield name, attr.serialize(getattr(self, name))
            elif isinstance(attr, UnicodeSetAttribute):
                if getattr(self, name):
                    yield name, list(self.attribute_values.get(name))
            else:
                yield name, attr.serialize(getattr(self, name))


