import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input,Output,State
from dash import dash_table
import pandas as pd

from app import app, pgdb
from db.models import Follower

layout = html.Div(style={'padding': '35px 25px'}, children=[
    dbc.Alert(id='alert-rm-follower',
              dismissable=True,
              is_open=False,
              color='warning',
              duration=2000),

    dbc.Alert(id='alert-add-follower',
              dismissable=True,
              is_open=False,
              color='warning',
              duration=2000),

    dbc.Row([
        dbc.Col([
            dbc.Input(type='text',
                      id='add-followers-text',
                      placeholder='Enter comma separated list of twitter followers',
                      value='',
                      debounce=True,
                      style={'padding': 10}),
            dbc.Button('add',
                       id='add-followers-btn',
                       color='info',
                       size='sm',
                       outline=True,
                       className='mt-3')
        ], width=6, className='me-3')
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Label('Following Users',
                      id='label-user-table',
                      html_for='user-table'),
            dcc.Interval(id='interval-user-table', n_intervals=0, interval=3000),
            html.Div(id='user-table'),
            html.Div(id='user-table-deleted')
        ], width=6, className='mt-3')
    ]),

])

@app.callback(
    Output('user-table', 'children'),
    Input('interval-user-table', 'n_intervals')
)
def load_user_table(n_intervals):
    df = pd.read_sql_table('follower', con=pgdb.engine)
    df = df[['name']]
    return [
        dash_table.DataTable(
            id='table-followers',
            columns=[{
                'id': str(x),
                'name': str(x),
                'deletable': True
            } for x in df.columns],
            data=df.to_dict('records'),
            editable=False,
            row_deletable=True,
            filter_action='native',
            sort_action='native',
            sort_mode='single',
            page_action='none',
            style_table={'height': '300px', 'overflowY': 'auto'},
            style_cell={'textAlign': 'left', 'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'}
        )
    ]

@app.callback(
    Output('alert-rm-follower', 'is_open'),
    Output('alert-rm-follower', 'children'),
    Input('table-followers', 'data_previous'),
    State('table-followers', 'data'),
    State('alert-rm-follower', 'is_open'),
    prevent_initial_call=True
)
def show_removed_rows(previous, current, do_alert):
    if previous is None:
        raise dash.exceptions.PreventUpdate
    else:
        delete_follower_names = [row['name'] for row in previous if row not in current]
        row_to_delete = pgdb.session.query(Follower).filter(Follower.name == delete_follower_names[0]).one()
        pgdb.session.delete(row_to_delete)
        pgdb.session.commit()
        return not do_alert, f'info: user={delete_follower_names[0]} deleted' if not do_alert else dash.no_update

@app.callback(
    Output('alert-add-follower', 'is_open'),
    Output('alert-add-follower', 'children'),
    Input('add-followers-btn', 'n_clicks'),
    Input('add-followers-text', 'value'),
    State('alert-add-follower', 'is_open'),
    prevent_initial_call=True
)
def add_followers(n_clicks, csvfollowers, do_alert):

    added = []
    if n_clicks and n_clicks>0:
        new_followers = csvfollowers.split(',')
        for str_follower in new_followers:
            follower = Follower(name=str_follower)
            already_exists = Follower.query.filter_by(name=str_follower).first()
            if already_exists:
                continue
            follower.add(follower)
            added.append(str_follower)

    if not added:
        raise dash.exceptions.PreventUpdate
    else:
        return [not do_alert, f"info: user(s)={csvfollowers} added"]


