from .sql_base import Base
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy import String, Text, Integer, Numeric, inspect
# import re
# from sqlalchemy_mixins.smartquery import RELATION_SPLITTER, OPERATOR_SPLITTER
# from .sql_smart_query import And, Or

CONDITIONS_RELATION_SPLITTER = '.'


def db_get_or_create(model, defaults=None, **kwargs):
    instance = model.where(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        instance.save()
        return instance, True


def get_class_by_tablename(tablename):
  """Return class reference mapped to table.

  :param tablename: String with name of table.
  :return: Class reference or None.
  """
  for c in Base.registry._class_registry.values():
    if hasattr(c, '__tablename__') and c.__tablename__ == tablename:
      return c

  return None


def get_class_by_polymorphic_identity(identity):
  """Return class reference mapped to table.

  :param identity: String with identity of polymorphic table.
  :return: Class reference or None.
  """

  for c in Base.registry._class_registry.values():
      if hasattr(c, '__mapper_args__') and c.__mapper_args__.get('polymorphic_identity', None) == identity:
          print(c)
          print(c.__class__)
          return c

  return None


def get_schema_by_tablename(tablename, schema=None):
    def _get_simple_input_type(type):
        if isinstance(type, String) or isinstance(type, Text):
            return 'text'
        elif isinstance(type, Integer) or isinstance(type, Numeric):
            return 'number'

        return 'text'

    columns_schema = []

    if tablename:
        _infrastructure_model = get_class_by_tablename(tablename)
        include = schema['include'] if 'include' in schema else list(_infrastructure_model.__mapper__.c.keys())
        exclude = schema.get('exclude', [])
        columns = [x for x in include if x not in exclude]

        for c in _infrastructure_model.__table__.columns:
            if c.key in c.key in columns:
                columns_schema.append({
                    'name': c.key,
                    'type': _get_simple_input_type(c.type),
                    'required': not c.nullable,
                    'restriction': c.type.length if isinstance(c.type, String) else None
                })

    return columns_schema


def mapping_entities_attributes(master_obj, slave_obj):
    for column in master_obj.__mapper__.columns:
        if column.key != 'id' and column.key != 'created_on' and column.key != 'updated_on':
            setattr(slave_obj, column.key, getattr(master_obj, column.key))

    return slave_obj


def inspect_target_changes(target, mapper):
    state = inspect(target)

    for attr in state.attrs:
        hist = attr.load_history()

        # TODO: Revision
        if hist.has_changes():
            # Ignore relations
            if attr.key in mapper.c:
                return True

    return False


# def smart_filter_with_permissions(base_filter, conditions):
#     """Conditions are mapped to the format needed.
#       - dots (.) are replaced by three underscores (___)
#       - if a condition does not contain an operation (__OP), operation is based on the value
#         - if the value is a list, operation is __in
#         - if other case, no operation is added (will use the default equals)
#
#     This method also performs the following optimization (see task FM-893):
#     If _base_filter includes a key1=value1 and conditions includes a key1__in=[...,value1,...]
#     then conditions[key1__in] is removed.
#     This case is commonly seen when querying data for a specific machine
#
#     :param base_filter: Original filter (either a dictionary or an SmartFilter object)
#     :param conditions: Filter from the permissions
#     :return: An SmartFilter object (And or Or) with the merge of the original base filter
#     and the permissions conditions
#     """
#
#     def merge_and_simplify(_base_filter, _conditions):
#         def get_key(old_key, old_key_value):
#             regex = '\w{}\w+$'.format(OPERATOR_SPLITTER)
#             suffix_op = ''
#             if isinstance(old_key_value, list) and not re.search(regex, old_key):
#                 suffix_op = '{}in'.format(OPERATOR_SPLITTER)
#
#             return old_key.replace(CONDITIONS_RELATION_SPLITTER, RELATION_SPLITTER) + suffix_op
#
#         def iterate_filter(current_filter):
#             if isinstance(current_filter, dict):
#                 for k, v in current_filter.items():
#                     yield (k, v)
#             elif isinstance(current_filter, And):
#                 for item in current_filter.items:
#                     yield from iterate_filter(item)
#
#         _conditions = {get_key(k, v): v for k, v in _conditions.items()}
#
#         for key, value in iterate_filter(_base_filter):
#             in_key = f'{key}{OPERATOR_SPLITTER}in'
#             if in_key in _conditions and value in _conditions[in_key]:
#                 del _conditions[in_key]
#
#         return And(_base_filter, _conditions)
#
#     if conditions is True or conditions == []:
#         return base_filter
#
#     if isinstance(conditions, list):
#         return Or(*[merge_and_simplify(base_filter, cond) for cond in conditions])
#     return merge_and_simplify(base_filter, conditions)
