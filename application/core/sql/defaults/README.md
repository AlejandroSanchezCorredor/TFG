## [LIST] Dynamic filters in base GET methods

[comment]: <> (https://github.com/absent1706/sqlalchemy-mixins)
[comment]: <> (> https://github.com/absent1706/sqlalchemy-mixins/blob/master/sqlalchemy_mixins/smartquery.py)

For the list calls in the query string the following values can be used:
 - ```_page=2 -> page equal to 2 (por defecto es 1)```
 - ```_page_size=30 -> page size equal to 30 (default is 20)```
 - ```_order_by=username -> sort by user name```
 - ```_order_by=-company,username -> sort first by company (DESC) and then by username```
 - ```_filter_username=@grupovermon.com -> filter so that the user name includes @grupovermon.com```
 - ```_fields=field1,field2 -> get only field1 and field2 fields (overwrite the schema)```

By default the filters use the ilike operator, you can specify another operator by placing it at the end of the field to be filtered preceded by 2 trailing slashes:
 - ```_filter_username__exact=jialonso@grupovermon.com -> filter so that the user name is exactly the same as the user name. jialonso@grupovermon.com```

You can also use the dot operator to enter a relation (in both sort and filter). For example:
 - ```_filter_company.code__exact=GV -> filter so that the company code is GV```
 - ```_order_by=company.code -> sort by company code.```

The complete list of operators for the filters is as follows.
```
_operators = {
    'isnull': lambda c, v: (c == None) if v else (c != None),
    'exact': operators.eq,
    'ne': operators.ne,  # not equal or is not (for None)

    'gt': operators.gt,  # greater than , >
    'ge': operators.ge,  # greater than or equal, >=
    'lt': operators.lt,  # lower than, <
    'le': operators.le,  # lower than or equal, <=

    'in': operators.in_op,
    'between': lambda c, v: c.between(v[0], v[1]),

    'like': operators.like_op,
    'ilike': operators.ilike_op,
    'startswith': operators.startswith_op,
    'istartswith': lambda c, v: c.ilike(v + '%'),
    'endswith': operators.endswith_op,
    'iendswith': lambda c, v: c.ilike('%' + v),

    'year': lambda c, v: extract('year', c) == v,
    'month': lambda c, v: extract('month', c) == v,
    'day': lambda c, v: extract('day', c) == v
}
```

The operator 'isnull' is a bit special because it compares against None and is used like this:
 - ```_filter_company.code__isnull -> Company code is not null```
 - ```_filter_company.code__isnull=1 -> Company code is null```


**EXAMPLES > QUERY controller**

- ```_filter = And(Or({'name__ilike': '%fr%', 'name__ilike': '%sp%'}), {'id__in': [212,213,214]})```
- ```_filter = Or({'name__like': '%fr%', 'name__like': '%sp%'})```
