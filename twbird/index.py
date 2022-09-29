import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State

from app import app
from app import server
from apps import user_management

dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem('User Management', href='/user_management'),
    ],
    nav=True,
    label='Explore'
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row([
                    dbc.Col(dbc.NavbarBrand('Admin', className='ml-2'))
                ],
                    align='center',
                ),
                href='/user_management'
            ),
            dbc.NavbarToggler(id='navbar-toggler2'),
            dbc.Collapse(
                dbc.Nav(
                    [dropdown],
                    className='ml-auto',
                    navbar=True
                ),
                id='navbar-collapse2',
                navbar=True
            )
        ]
    ),
    color='dark',
    dark=True,
    className='mb-4'
)


def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


for i in [2]:
    app.callback(
        Output(f'navbar-collapse{i}', 'is_open'),
        Input(f'navbar-toggler{i}', 'n_clicks'),
        State(f'navbar-collapse{i}', 'is_open')
    )(toggle_navbar_collapse)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content'),
])


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/user_management':
        return user_management.layout
    else:
        return user_management.layout


if __name__ == '__main__':
    app.run_server(host='0.0.0.0',
                   port=9155,
                   threaded=True,
                   debug=True,
                   use_reloader=True,
                   dev_tools_ui=True,
                   dev_tools_hot_reload=True)
