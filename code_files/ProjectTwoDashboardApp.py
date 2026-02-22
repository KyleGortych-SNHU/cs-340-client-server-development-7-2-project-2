"""
Project Two
CS-340 Client/Server Development (7-2)

Dashboard for Grazioso Salvare to identify dogs suitable for
search-and-rescue training using Austin Animal Center Outcomes data.
Implements MVC pattern with MongoDB model, Dash widgets View,
and CRUD module queries Controller.

Date: 2/22/2026
Maintainer: Kyle Gortych
"""

from dash import Dash, dash_table, html, dcc
from dash.dependencies import Input, Output
import pandas as pd
import os
import base64
import plotly.express as px

from CRUD_Python_Module import CRUD

# Data Manipulation & Model

# MongoDB credentials
username = "aacuser"
password = os.getenv("AAC_PASS")

if not username or not password:
    raise Exception(
        "MongoDB credentials not set. "
        "Please set AAC_PASS environment variable."
    )

# Connect to database via CRUD Module
shelter = CRUD(username, password, db_name='aac', collection_name='animals')

# Retrieve ALL documents (unfiltered starting view)
df = pd.DataFrame.from_records(shelter.read({}))

# Remove MongoDB ObjectId column to prevent DataTable crash
if '_id' in df.columns:
    df.drop(columns=['_id'], inplace=True)

# Dashboard Layout & View

# Initialize Dash app
app = Dash(__name__)

# Encode the Grazioso Salvare logo for inline display
logo_path = os.path.join(os.path.dirname(__file__), 'Grazioso Salvare Logo.png')
if os.path.exists(logo_path):
    encoded_image = base64.b64encode(open(logo_path, 'rb').read()).decode()
    logo_element = html.Img(
        src=f'data:image/png;base64,{encoded_image}',
        style={'height': '100px', 'margin': '10px'}
    )
else:
    logo_element = html.Div("(Logo not found)")

# Dashboard Layout
app.layout = html.Div([

    # Header with logo and unique identifier
    html.Center([
        logo_element,
        html.B(html.H1("Grazioso Salvare Animal Search-and-Rescue Dashboard")),
        html.H1("CS-340 Project Two"),
        html.H2("Created by Kyle Gortych"),
    ]),
    html.Hr(),

    # Interactive filter options with radio buttons for rescue type
    html.Div([
        html.Label("Select Rescue Type Filter:", style={'fontWeight': 'bold', 'fontSize': '16px'}),
        dcc.RadioItems(
            id='filter-type',
            options=[
                {'label': ' Water Rescue', 'value': 'water'},
                {'label': ' Mountain or Wilderness Rescue', 'value': 'mountain'},
                {'label': ' Disaster or Individual Tracking', 'value': 'disaster'},
                {'label': ' Reset (Show All)', 'value': 'reset'},
            ],
            value='reset',
            inline=True,
            style={'margin': '10px 0'},
            inputStyle={'marginRight': '5px', 'marginLeft': '15px'},
        ),
    ]),
    html.Hr(),

    # Interactive data table
    dash_table.DataTable(
        id='datatable-id',
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": True}
            for i in df.columns
        ],
        data=df.to_dict('records'),
        page_size=10,
        sort_action='native',
        filter_action='native',
        column_selectable='single',
        row_selectable='single',
        selected_rows=[0],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={
            'backgroundColor': '#2c3e50',
            'color': 'white',
            'fontWeight': 'bold'
        },
    ),

    html.Br(),
    html.Hr(),

    # Charts: pie chart and geolocation map side by side
    html.Div(
        className='row',
        style={'display': 'flex'},
        children=[
            html.Div(
                id='graph-id',
                className='col s12 m6',
                style={'width': '50%'},
            ),
            html.Div(
                id='map-id',
                className='col s12 m6',
                style={'width': '50%'},
            ),
        ]
    ),
])


# Interaction between Components & Controller

def build_rescue_query(filter_type):
    """
    Build a MongoDB query dict based on the selected rescue type.

    Rescue type breed/age/sex criteria from the Grazioso Salvare
    Dashboard Specifications (Preferred Dog Breeds Table).
    """
    if filter_type == 'water':
        return {
            "animal_type": "Dog",
            "breed": {"$in": [
                "Labrador Retriever Mix",
                "Chesapeake Bay Retr Mix",
                "Newfoundland",
            ]},
            "sex_upon_outcome": "Intact Female",
            "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156},
        }
    elif filter_type == 'mountain':
        return {
            "animal_type": "Dog",
            "breed": {"$in": [
                "German Shepherd",
                "Alaskan Malamute",
                "Old English Sheepdog",
                "Siberian Husky",
                "Rottweiler",
            ]},
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {"$gte": 26, "$lte": 156},
        }
    elif filter_type == 'disaster':
        return {
            "animal_type": "Dog",
            "breed": {"$in": [
                "Doberman Pinscher",
                "German Shepherd",
                "Golden Retriever",
                "Bloodhound",
                "Rottweiler",
            ]},
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {"$gte": 20, "$lte": 300},
        }
    else:
        # Reset — return all animals
        return {}


@app.callback(
    Output('datatable-id', 'data'),
    [Input('filter-type', 'value')]
)
def update_dashboard(filter_type):
    """Filter the data table based on the selected rescue type."""
    query = build_rescue_query(filter_type)
    filtered = pd.DataFrame.from_records(shelter.read(query))

    if '_id' in filtered.columns:
        filtered.drop(columns=['_id'], inplace=True)

    return filtered.to_dict('records')


@app.callback(
    Output('graph-id', 'children'),
    [Input('datatable-id', 'derived_virtual_data')]
)
def update_graphs(viewData):
    """Display a pie chart of breed distribution from the current data table."""
    if viewData is None or len(viewData) == 0:
        return html.Div("No data available for chart.")

    dff = pd.DataFrame.from_dict(viewData)

    if 'breed' not in dff.columns:
        return html.Div("Breed column not found.")

    fig = px.pie(
        dff,
        names='breed',
        title='Preferred Animals by Breed',
        hole=0.3,
    )
    fig.update_layout(margin={"r": 10, "t": 40, "l": 10, "b": 10})

    return [dcc.Graph(figure=fig)]


@app.callback(
    Output('datatable-id', 'style_data_conditional'),
    [Input('datatable-id', 'selected_columns')]
)
def update_styles(selected_columns):
    """Highlight a selected column in the data table."""
    if not selected_columns:
        return []
    return [
        {'if': {'column_id': i}, 'background_color': '#D2F3FF'}
        for i in selected_columns
    ]


@app.callback(
    Output('map-id', 'children'),
    [
        Input('datatable-id', 'derived_virtual_data'),
        Input('datatable-id', 'derived_virtual_selected_rows'),
    ]
)
def update_map(viewData, selected_rows):
    """Update the geolocation map based on the selected row in the data table."""
    if viewData is None or len(viewData) == 0:
        return html.Div("No data to display on the map.")

    dff = pd.DataFrame(viewData)

    # Default to first row if nothing selected
    row = selected_rows[0] if selected_rows else 0

    # Safely clamp row index
    if row >= len(dff):
        row = 0

    # Use column names by position for compatibility with the dataset
    lat_col = str(dff.columns[13])
    lon_col = str(dff.columns[14])
    breed_col = str(dff.columns[4])
    name_col = str(dff.columns[9])

    # Create Plotly scatter map
    fig = px.scatter_map(
        dff.iloc[[row]],
        lat=lat_col,
        lon=lon_col,
        hover_name=breed_col,
        hover_data={name_col: True},
        zoom=10,
        height=500,
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return dcc.Graph(figure=fig)


# Run server
if __name__ == '__main__':
    app.run(debug=True)
