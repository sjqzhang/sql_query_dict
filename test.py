import sql_query_dict


def test_escape_string():
    assert sql_query_dict.quote_string('a') == '"a"'


def test_mysql_list_esc():
    assert sql_query_dict.mysql_list_esc([1, 2]) == "1,2"


def test_mysql_list_esc_string_numbers():
    assert sql_query_dict.mysql_list_esc(["1", "2"]) == '"1","2"'


def test_mysql_list_esc_string():
    assert sql_query_dict.mysql_list_esc(["a", "b"]) == '"a","b"'


def test_mysql_list_with_none():
    assert sql_query_dict._mysql_clause('x', [None, False]) == \
        ' ((x IS NULL) OR  (x IN (False)) ) '


def test_mysql_list_with_generator():
    assert sql_query_dict._mysql_clause('x', (x for x in [1, 2, 3])) == \
        " (x IN (1,2,3)) "


def test_mysql_with_gt_lt():
    SQL, vals = sql_query_dict.select(
        't', 'z', {'x><': (10, 30), 'y': 1}
    )
    assert SQL == \
        "SELECT z FROM t WHERE  (y = %s)  AND  ((x > %s) AND (x < %s)) "
    assert vals == [1, 10, 30]


def test_mysql_not_in():
    assert sql_query_dict._mysql_clause('x!=', [1, 2, 3]) == \
        " (x NOT IN (1,2,3)) "


def test_mysql_list_compare_with_none():
    assert sql_query_dict._mysql_clause(
        'x!=', [None, 1, 2, 3]
    ) == " ((x IS NOT NULL) AND  (x NOT IN (1,2,3)) ) "
    assert sql_query_dict._mysql_clause(
        'x',   [None, 1, 2, 3]
    ) == " ((x IS NULL) OR  (x IN (1,2,3)) ) "
