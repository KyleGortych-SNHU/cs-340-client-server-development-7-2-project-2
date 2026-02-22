"""
Test script for CRUD_Python_Module.py 
and ModuleFiveAssignmentApp.py

Maintainer: Kyle Gortych
Date: 02/15/2026
"""

import unittest
from unittest.mock import patch, MagicMock

from CRUD_Python_Module import CRUD
from ModuleFiveAssignmentApp import app  # Dash app

# Module Tests CRUD
class TestCRUD(unittest.TestCase):

    @patch("CRUD_Python_Module.MongoClient")
    def test_crud_operations(self, mock_mongo):
        # Mock the database and collection
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_mongo.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        # Create a CRUD instance (password/username don't matter due to mock)
        crud = CRUD(username="user", password="pass")

        test_doc = {"name": "Luna", "species": "Cat", "age": 5}

        # Test create
        crud.create(test_doc)
        mock_collection.insert_one.assert_called_with(test_doc)

        # Test read
        mock_collection.find.return_value = [test_doc]
        result = crud.read({"name": "Luna"})
        self.assertEqual(result, [test_doc])

        # Test update
        mock_collection.update_many.return_value.modified_count = 1
        updated_count = crud.update({"name": "Luna"}, {"$set": {"age": 6}})
        self.assertEqual(updated_count, 1)

        # Test delete
        mock_collection.delete_many.return_value.deleted_count = 1
        deleted_count = crud.delete({"name": "Luna"})
        self.assertEqual(deleted_count, 1)

# Dash App Tests
class TestDashApp(unittest.TestCase):

    @patch("ModuleFiveAssignmentApp.CRUD")
    def test_dash_callback(self, mock_crud_class):
        # Mock the CRUD instance returned by the app
        mock_crud = MagicMock()
        mock_crud.read.return_value = [{"name": "Lucy", "animal_type": "Dog"}]
        mock_crud_class.return_value = mock_crud

        # Use Dash test client
        test_client = app.test_client()

        # Simulate callback input
        # Dash 2.0+ allows callable callbacks directly
        from ModuleFiveAssignmentApp import update_output

        response_text = update_output("user", "pass", n_clicks=1)
        self.assertIn("Lucy", response_text)

        # Test zero clicks and should prompt for credentials
        response_text = update_output("user", "pass", n_clicks=0)
        self.assertIn("Enter credentials", response_text)

# Run tests
if __name__ == "__main__":
    unittest.main()
