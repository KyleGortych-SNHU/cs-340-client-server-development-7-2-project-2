from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from CRUD_Python_Module import CRUD

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Module 5 Assignment Kyle Gortych"),
    html.Label("Username:"),
    dcc.Input(id="input_user", type="text", placeholder="Enter username"),
    html.Br(),
    html.Label("Password:"),
    dcc.Input(id="input_passwd", type="password", placeholder="Enter password"),
    html.Br(),
    html.Button("Submit", id="submit-val", n_clicks=0),
    html.Hr(),
    html.Div(id="query-out", style={'whiteSpace': 'pre-line'})
])

@app.callback(
    Output('query-out', 'children'),
    [
        Input('input_user', 'value'),
        Input('input_passwd', 'value'),
        Input('submit-val', 'n_clicks')
    ]
)

def update_output(username_input, password_input, n_clicks):
    if n_clicks > 0:
        username = username_input
        password = password_input

        try:
            crud = CRUD(username=username, password=password, db_name="aac")

            result = crud.read({"animal_type": "Dog", "name": "Lucy"})

            if result:
                formatted = "\n".join([str(doc) for doc in result])
                return f"Query Results:\n{formatted}"
            else:
                return "No results found for query."

        except Exception as e:
            return f"Error connecting to MongoDB:\n{str(e)}"

    return "Enter credentials and click Submit."

if __name__ == '__main__':
    app.run(debug=True)
