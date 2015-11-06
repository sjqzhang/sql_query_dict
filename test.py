import sql_query_dict


def test_escape_string():
    assert sql_query_dict.quote_string('a') == '"a"'


def test_mysql_list_esc():
    assert sql_query_dict.mysql_list_esc([1, 2]) == "1,2"


def test_mysql_list_esc_string_numbers():
    assert sql_query_dict.mysql_list_esc(["1", "2"]) == '"1","2"'


def test_mysql_list_esc_string():
    assert sql_query_dict.mysql_list_esc(["a", "b"]) == '"a","b"'
