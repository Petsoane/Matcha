from pymongo import MongoClient
from bson.objectid import ObjectId

class DB:

	def __init__(self):
		client = MongoClient()
		db = client['matcha']
		self.__users = db['users']
		self.__posts = db['posts']
	
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

	# Update the users information
	def update_user(self, user_id, values):
		items = values.items()
		for key, value in items:
			if key == '_id':
				continue
			self.__users.update_one({'_id' : user_id}, {'$set': { key: value}})


	# Add a post to the posts table
	def add_post(self, post):
		self.__posts.insert_one(post)

	# Get all the posts from the table.
	def get_posts(self):
		return self.__posts.find()

	# Get a single post
	def get_post(self, post_id):
		post_id = ObjectId(post_id)
		print(post_id)

		return self.__posts.find_one({'_id': post_id})


	# Update a single post.
	def update_post(self, post):
		self.__posts.update_one({'_id' : post['_id']}, {'$set': post})

	# delete a single entry
	def delete_post(self, post):
		self.__posts.delete_one({'_id': post['_id']})