"""
CRUD Python Module for 
"""

from pymongo import MongoClient 
from bson.objectid import ObjectId 

# add for better testing
from pymongo.errors import PyMongoError

import urllib.parse

class CRUD: 
    """ 
    CRUD operations for Animal collection in MongoDB 
    """ 

    def __init__(self, username, password, db_name='aac', host='localhost', port=27017, collection_name='animals'): 
        """
        Initialize MongoDB connection.

        param username: MongoDB username
        param password: MongoDB password
        param db_name: Database name
        param host: MongoDB host
        param port: MongoDB port
        param collection_name: Collection name
        """

        # URL encode username/password for MongoDB URI
        username = urllib.parse.quote_plus(username)
        password = urllib.parse.quote_plus(password)

         
        # Initialize Connection via try excpetion
        try: 
            self.client = MongoClient(
                f'mongodb://{username}:{password}@{host}:{port}/{db_name}?authSource=admin'
            )

            # authentication check
            self.client.admin.command('ping')

            self.database = self.client[db_name] 
            self.collection = self.database[collection_name] 

            print(f"Connected to MongoDB database '{db_name}', collection '{collection_name}'")

        except PyMongoError as e:
            raise Exception(f"Error connecting to MongoDB: {e}")

    def create(self, data):
        """
        Insert a document into the collection.

        param data: dict of key/value pair
        return: True if insert was successful, False otherwise
        """
        if not isinstance(data, dict) or not data: 
            raise ValueError("Data must be a non empty dictionary")

        try:
            self.collection.insert_one(data)
            return True
        except PyMongoError as e:
            print(f"Insert has failed: {e}")
            return False

    def read(self, query):
        """
        Query documents from the collection

        param query: query a dict of key/value pairs to match documents
        return: list of documents matching the query
        """
        if not isinstance(query, dict):
            raise ValueError("Query must be a dict")

        try:
            cursor = self.collection.find(query)
            return list(cursor)
        except PyMongoError as e:
            print(f"Read operation failed: {e}")
            return []

    def update(self, query, new_values):
        """
        Update documents in the collection.

        param query: Dictornary to match documents
        param new_values: Dictornary of update values
        return: Number of ducoments modified
        """
        if not isinstance(query, dict) or not isinstance(new_values, dict):
            raise ValueError("Query and new_values must be dictionaries")
        try:
            result = self.collection.update_many(query, new_values)
            return result.modified_count
        except PyMongoError as error:
            print(f"Update operation failed: {error}")
            return 0

    def delete(self, query):
        """
        Delete document from the collection.

        param query: dictionary to match documents
        retrun: Number of documents deleted
        """
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary")

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as error:
            print(f"Delete operation failed: {error}")
            return 0
