import mysql.connector
import json


class UseDatabase:
	def __init__(self, config: dict):
		self.configuration = config

	def __enter__(self):
		try:
			self.conn = mysql.connector.connect(**self.configuration)
			self.cursor = self.conn.cursor()
			return self.cursor
		except mysql.connector.errors.InterfaceError as err:
			raise ConnectionErrors(err)
		except mysql.connector.errors.DatabaseError as err:
			raise ConnectionErrors(err)

	def __exit__(self, exc_type, exc_value, exec_trace):
		self.conn.commit()
		self.cursor.close()
		self.conn.close()
		if exc_type is mysql.connector.errors.ProgrammingError:
			raise SQLError(exc_value)
		if exc_type is mysql.connector.errors.DatabaseError:
			raise SQLError(exc_value)

class ConnectionErrors(Exception):
	pass


class SQLError(Exception):
	pass