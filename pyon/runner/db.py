"""
Database stuff!
"""


# class Database(object):
#     """
#     Rewritten to just use a database backend.
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
