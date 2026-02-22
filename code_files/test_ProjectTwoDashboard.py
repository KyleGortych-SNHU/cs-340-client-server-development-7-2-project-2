"""
Test script for ProjectTwoDashboardApp.py

Maintainer: Kyle Gortych
Date: 02/22/2026
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd


class TestProjectTwoDashboard(unittest.TestCase):
    """Tests for the Project Two Grazioso Salvare Dashboard."""

    @classmethod
    def setUpClass(cls):
        """Mock environment and CRUD before importing the app."""

        # Sample record
        cls.sample_record = {
            "_id": "abc123",
            "age_upon_outcome": "2 years",
            "animal_id": "A123456",
            "animal_type": "Dog",
            "breed": "Labrador Retriever Mix",
            "color": "Yellow",
            "date_of_birth": "2024-01-01",
            "datetime": "2026-01-15 10:00:00",
            "monthyear": "2026-01-15T10:00:00",
            "name": "Buddy",
            "outcome_subtype": "",
            "outcome_type": "Transfer",
            "sex_upon_outcome": "Intact Female",
            "location_lat": 30.75,
            "location_long": -97.48,
            "age_upon_outcome_in_weeks": 104.0,
        }

        cls.mock_crud_instance = MagicMock()
        cls.mock_crud_instance.read.return_value = [cls.sample_record.copy()]

        # Patch global os.getenv before module import
        cls.patcher_env = patch("os.getenv", return_value="dummy_pass")

        # Patch CRUD where it is defined
        cls.patcher_crud = patch(
            "CRUD_Python_Module.CRUD",
            return_value=cls.mock_crud_instance
        )

        # Prevent logo file check issues
        cls.patcher_logo = patch("os.path.exists", return_value=False)

        cls.patcher_env.start()
        cls.patcher_crud.start()
        cls.patcher_logo.start()

        # Import after patching
        import ProjectTwoDashboardApp as app_module
        cls.app_module = app_module

    @classmethod
    def tearDownClass(cls):
        cls.patcher_env.stop()
        cls.patcher_crud.stop()
        cls.patcher_logo.stop()

    # DataFrame setup tests
    def test_dataframe_loads(self):
        self.assertIsInstance(self.app_module.df, pd.DataFrame)

    def test_id_column_removed(self):
        self.assertNotIn("_id", self.app_module.df.columns)

    def test_dataframe_column_count(self):
        # 16 original - 1 (_id) = 15
        self.assertEqual(len(self.app_module.df.columns), 15)

    # Query builder tests
    def test_build_query_water_rescue(self):
        query = self.app_module.build_rescue_query('water')
        self.assertEqual(query["animal_type"], "Dog")
        self.assertIn("Labrador Retriever Mix", query["breed"]["$in"])
        self.assertIn("Chesapeake Bay Retr Mix", query["breed"]["$in"])
        self.assertIn("Newfoundland", query["breed"]["$in"])
        self.assertEqual(query["sex_upon_outcome"], "Intact Female")
        self.assertEqual(query["age_upon_outcome_in_weeks"]["$gte"], 26)
        self.assertEqual(query["age_upon_outcome_in_weeks"]["$lte"], 156)

    def test_build_query_mountain_rescue(self):
        query = self.app_module.build_rescue_query('mountain')
        self.assertEqual(query["animal_type"], "Dog")
        self.assertIn("German Shepherd", query["breed"]["$in"])
        self.assertIn("Alaskan Malamute", query["breed"]["$in"])
        self.assertIn("Old English Sheepdog", query["breed"]["$in"])
        self.assertIn("Siberian Husky", query["breed"]["$in"])
        self.assertIn("Rottweiler", query["breed"]["$in"])
        self.assertEqual(query["sex_upon_outcome"], "Intact Male")

    def test_build_query_disaster_rescue(self):
        query = self.app_module.build_rescue_query('disaster')
        self.assertEqual(query["animal_type"], "Dog")
        self.assertIn("Doberman Pinscher", query["breed"]["$in"])
        self.assertIn("Golden Retriever", query["breed"]["$in"])
        self.assertIn("Bloodhound", query["breed"]["$in"])
        self.assertEqual(query["sex_upon_outcome"], "Intact Male")
        self.assertEqual(query["age_upon_outcome_in_weeks"]["$gte"], 20)
        self.assertEqual(query["age_upon_outcome_in_weeks"]["$lte"], 300)

    def test_build_query_reset(self):
        query = self.app_module.build_rescue_query('reset')
        self.assertEqual(query, {})

    # Callback tests
    def test_update_dashboard_calls_crud_read(self):
        self.mock_crud_instance.read.reset_mock()
        result = self.app_module.update_dashboard('water')
        self.mock_crud_instance.read.assert_called_once()
        self.assertIsInstance(result, list)

    def test_update_dashboard_reset(self):
        result = self.app_module.update_dashboard('reset')
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_update_graphs_with_data(self):
        from dash import dcc
        view_data = [
            {"breed": "Labrador Retriever Mix", "name": "Buddy"},
            {"breed": "Labrador Retriever Mix", "name": "Max"},
            {"breed": "Newfoundland", "name": "Bear"},
        ]
        result = self.app_module.update_graphs(view_data)
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dcc.Graph)

    def test_update_graphs_empty_data(self):
        from dash import html
        result = self.app_module.update_graphs([])
        self.assertIsInstance(result, html.Div)

    def test_update_graphs_none_data(self):
        from dash import html
        result = self.app_module.update_graphs(None)
        self.assertIsInstance(result, html.Div)

    def test_update_map_with_data(self):
        from dash import dcc
        record = self.sample_record.copy()
        record.pop("_id", None)
        result = self.app_module.update_map([record], [0])
        self.assertIsInstance(result, dcc.Graph)

    def test_update_map_empty_data(self):
        from dash import html
        result = self.app_module.update_map([], None)
        self.assertIsInstance(result, html.Div)

    def test_update_styles_with_selection(self):
        result = self.app_module.update_styles(["breed"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['if']['column_id'], "breed")

    def test_update_styles_no_selection(self):
        result = self.app_module.update_styles([])
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
