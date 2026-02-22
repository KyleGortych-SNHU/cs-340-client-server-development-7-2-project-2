"""
Module Six Milestone

Date: 2/15/2026
Maintainer: Kyle Gortych
"""

from dash import Dash, dash_table, html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import os
import plotly.express as px

from CRUD_Python_Module import CRUD

# Model MongoDB Connection via CRUD Module
# Load credentials from environment variables
username = "aacuser"
password = os.getenv("AAC_PASS")


if not username or not password:
    raise Exception("MongoDB credentials not set. Please set AAC_USER and AAC_PASS environment variables.")

shelter = CRUD(username, password, db_name='aac', collection_name='animals')

# Retrieve ALL documents (unfiltered view)
df = pd.DataFrame.from_records(shelter.read({}))

# Remove MongoDB ObjectId column to prevent DataTable crash
if '_id' in df.columns:
    df.drop(columns=['_id'], inplace=True)

# Initialize Dash app
app = Dash(__name__)

# View Dashboard Layout
app.layout = html.Div([

    html.Center(html.H1("CS-340 Milestone 6-1 Kyle Gortych")),
    html.Hr(),

    # Interactive Data Table
    dash_table.DataTable(
        id='datatable-id',
        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
        data=df.to_dict('records'),
        page_size=10,
        sort_action='native',
        filter_action='native',
        row_selectable='single',
        selected_rows=[0],  # Default to first row
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
    ),

    html.Br(),
    html.Hr(),

    # Geolocation Map Container
    html.Div(id='map-id')
])

# Controller callbacks
@app.callback(
    Output('map-id', 'children'),
    [
        Input('datatable-id', 'derived_virtual_data'),
        Input('datatable-id', 'derived_virtual_selected_rows')
    ]
)
def update_map(viewData, selected_rows):

    if viewData is None or len(viewData) == 0:
        return html.Div("No data to display on the map.")

    dff = pd.DataFrame(viewData)

    # Default to first row if nothing selected
    row = selected_rows[0] if selected_rows else 0

    # Extract column names
    lat_col = str(dff.columns[13])
    lon_col = str(dff.columns[14])
    breed_col = str(dff.columns[4])
    name_col = str(dff.columns[9])

    # Create Plotly map figure
    fig = px.scatter_map(
        dff.iloc[[row]],
        lat=lat_col,
        lon=lon_col,
        hover_name=breed_col,
        hover_data={name_col: True},  # Animal Name
        zoom=10,
        height=500
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return dcc.Graph(figure=fig)

# Run server
if __name__ == '__main__':
    app.run(debug=True)
