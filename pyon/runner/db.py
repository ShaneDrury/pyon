"""
Should be able to use multiple backends as long as they implement the Python
Database Specification v2.0 (PEP 249). Sqlite3 is default as it doesn't
require the user to run a database server.
"""


class ListType(object):
    def __init__(self, d):
        self.data = d

    def __repr__(self):
        expr = "("
        for d in self.data:
            expr += "{};".format(d)
        expr = expr[:-1]
        expr += ")"
        return expr


def adapt_list_type(list_type_obj):
    data = list_type_obj.data
    expr = ""
    for d in data:
        expr += "{};".format(d)
    expr = expr[:-1]
    return expr.encode('ascii')


def convert_float_list(s):
    data = tuple(map(float, s.split(b";")))
    return data


def convert_int_list(s):
    data = tuple(map(int, s.split(b";")))
    return data


# class Database(object):
#     """
#     """
#     def __init__(self, db_name, username):
#         self.db_name = db_name
#         self.username = username
#         self.db_conn = None
#         self.cur = None
#
#     def _make_connection(self):
#         self.db_conn = psycopg2.connect(database=self.db_name,
#                                         user=self.username)
#         self.cur = self.db_conn.cursor()
#
#     def _close_connection(self):
#         self.cur.close()
#         self.db_conn.close()
#
#     def __enter__(self):
#         self._make_connection()
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self._close_connection()
