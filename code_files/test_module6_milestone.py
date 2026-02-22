"""
Test script for ModuleSixMilestoneApp.py

Maintainer: Kyle Gortych
Date: 02/15/2026
"""

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

class TestModuleSixDashboard(unittest.TestCase):

    @patch("ModuleSixMilestoneApp.os.getenv", return_value="dummy_pass")
    @patch("ModuleSixMilestoneApp.CRUD")
    def test_dataframe_loads_and_callback(self, mock_crud_class, mock_getenv):
        # Mock CRUD read return value with 15 columns for callback safety
        mock_crud = MagicMock()
        mock_crud.read.return_value = [
            {
                "_id": "123",
                "name": "Buddy",
                "animal_type": "Dog",
                "breed": "Labrador",
                "age": 3,
                "weight": 25,
                "color": "Yellow",
                "arrival_date": "2026-01-01",
                "adopted": False,
                "microchip": "ABC123",
                "vaccinated": True,
                "spayed_neutered": True,
                "location_lat": 30.75,
                "location_long": -97.48,
                "shelter_id": "S001"
            }
        ]
        mock_crud_class.return_value = mock_crud

        # Import the module after mocking
        import ModuleSixMilestoneApp as app_module

        # Verify dataframe exists
        self.assertTrue(isinstance(app_module.df, pd.DataFrame))

        # Verify _id column removed
        self.assertNotIn("_id", app_module.df.columns)

        # Verify dataframe has correct number of columns excluding _id
        self.assertEqual(len(app_module.df.columns), 14)

        # Test the update_map callback with mock data
        viewData = app_module.df.to_dict("records")
        selected_rows = [0]

        # Call callback directly
        map_output = app_module.update_map(viewData, selected_rows)

        # Verify callback returns a dcc.Graph or html.Div
        from dash import dcc, html
        self.assertTrue(isinstance(map_output, dcc.Graph) or isinstance(map_output, html.Div))

        # If output is a Graph, inspect the figure directly
        if isinstance(map_output, dcc.Graph):
            fig = map_output.figure
            fig_data = fig.data[0]
            self.assertAlmostEqual(fig_data.lat[0], 30.75)
            self.assertAlmostEqual(fig_data.lon[0], -97.48)


if __name__ == "__main__":
    unittest.main()
