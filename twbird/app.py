import dash
import dash_bootstrap_components as dbc
from config.base_settings import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from flask_sqlalchemy import SQLAlchemy

external_stylesheets = [dbc.themes.LUX, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"]
external_scripts = [
    {'src': 'https://cdn.plot.ly/plotly-latest.min.js'},
    {'src': 'https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js'},
    {'src': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js'},
]

app = dash.Dash(__name__,
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets,
                title='User Management')

app.config.suppress_callback_exceptions = True
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.server.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

server = app.server

pgdb = SQLAlchemy(server)



