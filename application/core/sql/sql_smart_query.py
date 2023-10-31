from sqlalchemy_mixins.smartquery import SmartQueryMixin, _parse_path_and_make_aliases, DESC_PREFIX, RELATION_SPLITTER
from sqlalchemy_mixins.smartquery import smart_query as smart_query_orig
from sqlalchemy_mixins.eagerload import _flatten_schema, _eager_expr_from_flat_schema, JOINED

from sqlalchemy import and_, or_
from sqlalchemy.orm import contains_eager
from sqlalchemy.sql import operators
from collections import OrderedDict
from itertools import chain


def smart_query(cls, query, smart_filter, sort_attrs=None, schema=None):
    if not sort_attrs:
        sort_attrs = []
    if not schema:
        schema = {}

    # noinspection PyProtectedMember
    # root_cls = query._joinpoint_zero().class_  # for example, User or Post
    root_cls = cls

    attrs = list(smart_filter.keys()) + \
        list(map(lambda s: s.lstrip(DESC_PREFIX), sort_attrs))
    aliases = OrderedDict({})
    _parse_path_and_make_aliases(root_cls, '', attrs, aliases)

    loaded_paths = []
    for path, al in aliases.items():
        relationship_path = path.replace(RELATION_SPLITTER, '.')
        query = query.outerjoin(al[0], al[1]) \
            .options(contains_eager(relationship_path, alias=al[0]))
        loaded_paths.append(relationship_path)

    # Apply 'smart filters'
    aliases_map = {k: v[0] for k, v in aliases.items()}
    query = query.filter(smart_filter.query_filter(root_cls, aliases_map))

    for attr in sort_attrs:
        if RELATION_SPLITTER in attr:
            prefix = ''
            if attr.startswith(DESC_PREFIX):
                prefix = DESC_PREFIX
                attr = attr.lstrip(DESC_PREFIX)
            parts = attr.rsplit(RELATION_SPLITTER, 1)
            entity, attr_name = aliases[parts[0]][0], prefix + parts[1]
        else:
            entity, attr_name = root_cls, attr
        try:
            query = query.order_by(*entity.order_expr(attr_name))
        except KeyError as e:
            raise KeyError("Incorrect order path `{}`: {}".format(attr, e))

    if schema:
        flat_schema = _flatten_schema(schema)
        not_loaded_part = {path: v for path, v in flat_schema.items()
                           if path not in loaded_paths}
        query = query.options(*_eager_expr_from_flat_schema(
            not_loaded_part))

    return query


def transform_schema(schema, is_root=True):
    if schema is None:
        return None
    if 'relations' not in schema:
        return {} if is_root else JOINED
    return {k: transform_schema(schema['relations'][k], False) for k in schema['relations']}


class SmartFilter(object):
    def __init__(self, operator, *items):
        self.operator = operator
        self.items = items

    def keys(self):
        _items_keys = [list(it.keys()) for it in self.items]
        return list(set(chain(*_items_keys)))

    def query_filter(self, root_cls, aliases_map):
        query_subfilters = []
        for item in self.items:
            if isinstance(item, SmartFilter):
                sf = item.query_filter(root_cls, aliases_map)
            else:
                item_subfilters = []
                for attr, value in item.items():
                    if RELATION_SPLITTER in attr:
                        parts = attr.rsplit(RELATION_SPLITTER, 1)
                        entity, attr_name = aliases_map[parts[0]], parts[1]
                    else:
                        entity, attr_name = root_cls, attr
                    try:
                        item_subfilters.append(*entity.filter_expr(**{attr_name: value}))
                    except KeyError as e:
                        raise KeyError("Incorrect filter path `{}`: {}"
                                       .format(attr, e))
                sf = and_(*item_subfilters)
            query_subfilters.append(sf)
        return self.operator(*query_subfilters)


class And(SmartFilter):
    def __init__(self, *items):
        super().__init__(and_, *items)

    def __repr__(self):
        return 'And{}'.format(self.items)


class Or(SmartFilter):
    def __init__(self, *items):
        super().__init__(or_, *items)

    def __repr__(self):
        return 'Or{}'.format(self.items)


class MySmartQueryMixin(SmartQueryMixin):
    __abstract__ = True

    # _operators = dict(**SmartQueryMixin._operators, ne=operators.neg)  # Add ne operator

    @classmethod
    def smart_query(cls, filters=None, sort_attrs=None, schema=None):
        if isinstance(filters, SmartFilter):
            return smart_query(cls, cls.query, filters, sort_attrs, transform_schema(schema))
        return smart_query_orig(cls.query, filters, sort_attrs, transform_schema(schema))

    @classmethod
    def where(cls, smart_filter=None, **kwargs):
        if smart_filter:
            return cls.smart_query(smart_filter)
        return super().where(**kwargs)
