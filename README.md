[![Build Status](https://travis-ci.org/PlotWatt/sql_query_dict.svg?branch=master)](https://travis-ci.org/PlotWatt/sql_query_dict)

# sql_query_dict
express sql queries as python dictionaries

### select()

select(tablename, columns, o, ...)

tablename is either a string tablename, or a string with comma seperated
table names.  table name aliases are ok: "users u, books b"

columns is either a string with comma seperated column names or an
iterable with string column names:

```
    "id"
    "users.id, users.name"
    ("users.id", "books.name")
```

o is a dictionary describing where clauses:

```
{"users.id": 10} => "WHERE users.id = 10"

{"id>": 10} => "WHERE id > 10"

{"id": (10, 20, 30)} => "WHERE id in (10, 20, 30)"
```
    

### Example

```
SQL, vals = sql_query_dict.select(
    't', 'z', {'x><': (10, 30), 'y': 1}
)
assert SQL == "SELECT z FROM t WHERE  (y = %s)  AND  ((x > %s) AND (x < %s)) "
assert vals == [1, 10, 30]
```
