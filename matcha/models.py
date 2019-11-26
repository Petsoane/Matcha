from pymongo import MongoClient

class DB:

	def __init__(self):
		client = MongoClient()
		db = client['matcha']
		self.__users = db['users']
	
	def get_user(self, query):
		''' This function will get a single users information'''
		user = self.__users.find_one(query)

		return user
	
	# Add the user the database
	def register_user(self, details):
		self.__users.insert_one(details)

	# Get all the users from the database
	def users(self, query={}):
		return self.__users.find(query)