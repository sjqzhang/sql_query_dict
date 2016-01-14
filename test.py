import pytest

import sql_query_dict


def test_escape_string_with_single_quote():
    assert sql_query_dict.quote_string("'a") == '"\'a"'


def test_escape_string_with_double_quote():
    assert sql_query_dict.quote_string('"a') == "'\"a'"


def test_escape_string_with_single_and_double_quote():
    assert sql_query_dict.quote_string(""" '" """) == """' \\\'" '"""


def test_escape_string():
    assert sql_query_dict.quote_string('a') == "'a'"


def test_split_key_compare():
    assert sql_query_dict._split_key_compare('key|=') == ('key', '|=')


def test_mysql_list_esc():
    assert sql_query_dict.mysql_list_esc([1, 2]) == "1,2"


def test_mysql_list_esc_string_numbers():
    assert sql_query_dict.mysql_list_esc(["1", "2"]) == "'1','2'"


def test_mysql_list_esc_string():
    assert sql_query_dict.mysql_list_esc(["a", "b"]) == "'a','b'"


def test_mysql_list_with_or_equals():
    assert sql_query_dict._mysql_clause('x|=', [1, 2, 3], '%s') == \
        " (x IN (1,2,3)) "


def test_mysql_list_with_none():
    assert sql_query_dict._mysql_clause('x', [None, False], '%s') == \
        ' ((x IS NULL) OR  (x IN (False)) ) '


def test_mysql_list_with_generator():
    assert sql_query_dict._mysql_clause(
        'x', (x for x in [1, 2, 3]), '%s'
    ) == " (x IN (1,2,3)) "


def test_parse_tablename():
    assert sql_query_dict._parse_tablename('xyz') == 'xyz'


def test_parse_tablename_err():
    with pytest.raises(TypeError):
        sql_query_dict._parse_tablename(1)


def test_parse_tablename_set():
    assert sql_query_dict._parse_tablename(set(['xyz', 'abc'])) in (
        'xyz,abc', 'abc,xyz'
    )


def test_mysql_with_gt_lt():
    SQL, vals = sql_query_dict.select(
        't', 'z', {'x><': (10, 30), 'y': 1}
    )
    # easiest way to handle both orderings of the clauses
    assert SQL in (
        "SELECT z FROM t WHERE  (y = %s)  AND  ((x > %s) AND (x < %s)) ",
        "SELECT z FROM t WHERE  ((x > %s) AND (x < %s))  AND  (y = %s) ",
    )
    assert vals in (
        [1, 10, 30],
        [10, 30, 1],
    )


def test_mysql_string_value():
    assert sql_query_dict._mysql_clause('x', 'the', '%s') == \
        " (x = %s) "


def test_mysql_like():
    assert sql_query_dict._mysql_clause('x~', 'the %', '%s') == \
        " (x LIKE %s) "


def test_mysql_not_like():
    assert sql_query_dict._mysql_clause('x!~', 'the %', '%s') == \
        " (x NOT LIKE %s) "


def test_mysql_not_in():
    assert sql_query_dict._mysql_clause('x!=', [1, 2, 3], '%s') == \
        " (x NOT IN (1,2,3)) "


def test_mysql_list_compare_with_none():
    assert sql_query_dict._mysql_clause(
        'x!=', [None, 1, 2, 3], '%s'
    ) == " ((x IS NOT NULL) AND  (x NOT IN (1,2,3)) ) "
    assert sql_query_dict._mysql_clause(
        'x',   [None, 1, 2, 3], '%s'
    ) == " ((x IS NULL) OR  (x IN (1,2,3)) ) "
