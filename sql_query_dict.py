import re
import types
import sqlalchemy


def escape_string(string):
    return sqlalchemy.text(string)


def quote_string(string):
    return '"{}"'.format(str(escape_string(string)))


def mysql_list(l):
    return ','.join(map(str, l))


def _escape(x):
    if isinstance(x, basestring):
        return quote_string(x)
    else:
        return str(x)


def mysql_list_esc(l):
    return ','.join(map(_escape, l))


def _is_iterable(i):
    try:
        iter(i)
        return True
    except TypeError:
        return False


def is_number(x):
    try:
        float(x)
        return True
    except TypeError:
        return False


def _mysql_is_list(val):
    return _is_iterable(val) and not isinstance(val, basestring)


def _mysql_isval(val):
    """ These types should either be ignored or have already been
    inserted into the SQL directly and dont need sqlalchemy to do
    it for us. """
    if _mysql_is_list(val):
        return False
    elif isinstance(val, mysql_col):
        return False
    elif val in [None, mysql_now, mysql_ignore]:
        return False
    return True


class mysql_now:
    pass


class mysql_col(str):
    pass


class mysql_ignore(str):
    pass


def _mysql_simple_clause_list(key, compare, val):
    esc = mysql_list_esc(val)
    if esc == 'None':
        return ' (1) '
    elif esc == '':
        return ' (0) '

    if compare == '!=':
        compare = 'NOT IN'
    else:
        compare = 'IN'
    return ' ({0} {1} ({2})) '.format(key, compare, esc)


def _mysql_clause_list(key, compare, val):
    # convert generator to list
    if isinstance(val, types.GeneratorType):
        val = list(val)

    if None in val:
        val = filter(lambda x: x is not None, val)
        clause = _mysql_simple_clause_list(key, compare, val)

        if compare == '!=':
            compare = 'IS NOT'
            logic = 'AND'
        else:
            compare = 'IS'
            logic = 'OR'

        return " (({key} {compare} NULL) {logic} {clause}) ".format(
            key=key, compare=compare, logic=logic, clause=clause
        )
    else:
        return _mysql_simple_clause_list(key, compare, val)


def _mysql_simple_clause(key, compare, val):
    # default to '=' operator, and check for other comparison operators in
    # the key name
    if compare == '><':
        return ' (({0} > %s) AND ({0} < %s)) '.format(
            key
        )

    # check for now object or mysql_col object.
    # mysql_col will not get quoted, which is useful for
    # a k : v pair such as:
    #   'house_id' : mysql_col('houses.id'),
    if val == mysql_now:
        val = 'NOW()'
    elif isinstance(val, mysql_col):
        val = val
    else:
        val = '%s'

    return ' ({0} {1} {2}) '.format(key, compare, val)


def _split_key_compare(key):
    key, compare = re.match('([^<>=~!]*)([<>=~!]*)', key).groups()
    if compare == '':
        compare = '='
    return key, compare


def _mysql_clause(key, val):
    key, compare = _split_key_compare(key)

    if _mysql_is_list(val) and compare != '><':
        return _mysql_clause_list(key, compare, val)
    elif val is None:
        if compare == '!=':
            return ' ({0} IS NOT NULL) '.format(key)
        else:
            return ' ({0} IS NULL) '.format(key)
    else:
        return _mysql_simple_clause(key, compare, val)


def _flatten_between(keys, vals):
    new_vals = []
    for key, val in zip(keys, vals):
        if key[-2:] == '><':
            new_vals.extend(val)
        else:
            new_vals.append(val)
    return new_vals


def _mysql_other_fields(extra=None, order_by=None, limit=None, offset=None):
    ret = ''
    if order_by is not None:
        ret += ' ORDER BY %s ' % order_by
    if limit is not None:
        ret += ' LIMIT %d ' % limit
    if offset is not None:
        ret += ' OFFSET %d ' % offset
    if extra is not None:
        ret += ' ' + extra

    return ret


def select(tablename, cols, o=None, j=None, extra=None,
           order_by=None, limit=None, offset=None):
    o = o or {}
    j = j or {}

    # if o is a number or string, treat it as an id
    if not _is_iterable(o) or isinstance(o, basestring):
        o = {'id': long(o)}

    # ensure that keys and vals are in the same order, so they match up
    keys = o.keys()
    vals = [o[key] for key in keys]

    SQL = "SELECT {0} FROM {1} WHERE ".format(mysql_list(cols), tablename)
    SQL += ' AND '.join(
        _mysql_clause(key, val) for key, val in zip(keys, vals)
        if val is not mysql_ignore
    ) or '1'
    if j:
        SQL += ''.join(
            " AND ({0} = {1}) ".format(k, v) for k, v in j.iteritems()
        )

    # flatten tuple of values when >< operator (like a between) is used
    vals = _flatten_between(keys, vals)

    vals = filter(_mysql_isval, vals)

    SQL += _mysql_other_fields(
        extra=extra, order_by=order_by, limit=limit, offset=offset
    )

    return SQL, vals


def update(tablename, where, properties):
    # ensure that keys and vals are in the same order, so they match up
    set_keys = properties.keys()
    set_vals = [properties[key] for key in set_keys
                if properties[key] != mysql_now]
    properties = ", ".join(
        ' {0} = {1} '.format(key, val == mysql_now and 'NOW()' or '%s')
        for key, val in zip(set_keys, set_vals)
    )

    if is_number(where) or isinstance(where, (list, tuple)):
        where = {'id': where}
    elif not isinstance(where, dict):
        raise ValueError('where should be a number, list, tuple or dict')

    where_items = where.items()
    where_sql = ' AND '.join(
        _mysql_clause(k, v) for k, v in where_items
        if v is not mysql_ignore
    )
    where_vals = [v for k, v in where_items if _mysql_isval(v)]

    vals = set_vals + where_vals

    SQL = "UPDATE {tablename} SET {properties} WHERE {where_sql}".format(
        **locals()
    )

    return SQL, vals


def delete(tablename, properties):
    if isinstance(properties, list):
        properties = {'id': properties}
    if not _is_iterable(properties) or isinstance(properties, basestring):
        properties = {'id': long(properties)}

    keys = properties.keys()
    vals = [properties[key] for key in keys
            if properties[key] != mysql_now]
    where = ' AND '.join(
        _mysql_clause(key, val) for key, val in zip(keys, vals)
        if val is not mysql_ignore
    )

    SQL = "DELETE FROM {tablename} WHERE {where}".format(**locals())

    vals = [val for val in vals if not _mysql_is_list(val)]

    return SQL, vals


def insert(tablename, o, replace_into=False):
    # ensure that keys and vals are in the same order, so they match up
    keys = o.keys()
    vals = [o[key] for key in keys]

    SQL = "%s INTO %s (%s) VALUES (%s)" % (
        "REPLACE" if replace_into else "INSERT",
        tablename,
        ', '.join(keys),
        ', '.join(val == mysql_now and 'NOW()' or '%s' for val in vals)
    )

    # remove now objects to list passed to mysql_execute
    vals = filter(lambda val: val != mysql_now, vals)

    return SQL, vals
