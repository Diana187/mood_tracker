import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from datetime import datetime
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

import random
from faker import Faker

faker = Faker()

def df_for_chart(num_users=10, count=100):

    users = [f"{faker.first_name()} {faker.last_name()}" for _ in range(num_users)]
    tags = ['foo', 'bar', 'buzz', 'boo', 'puk', 'srenk']
    # times = [faker.date_time_between(start_date=past, end_date='now',).strftime('%Y-%m-%d %H:%M:%S') for _ in range(count)]
    times = []
    for i in range(count):
        time = faker.date_time_between_dates(
            datetime_start=datetime(2016, 1, 1),
            datetime_end=datetime(2016, 7, 21),
            tzinfo=None,
        )
        times.append(time)

    d = {
        'names': [random.choice(users) for _ in range(count)],
        'times': times,
        'moods': [random.randrange(-2, 3) for _ in range(count)],
    }
    df = pd.DataFrame(data=d)
    df_tags = pd.DataFrame({'tags': tags})
    df = df.merge(df_tags, how='cross')
    df = df.sample(count).reset_index().drop(columns=['index'])
    df['times'] = pd.to_datetime(df['times'])
    df.sort_values(by='times', inplace=True)

    return df

df = df_for_chart(count=1000)


app = Dash(__name__)
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# добавить простой стиль

default_value = 10

app.layout = dbc.Container([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dbc.Row([
        dbc.Col([
            # html.H1(children='Title of Dash App', style={'textAlign':'center'}),
            dcc.Dropdown(df.tags.unique(), df.tags.unique(), id='dropdown-selection', multi=True),
        ], width={'size': 6, 'order': 2}),
        dbc.Col([
            dcc.Dropdown(df.names.unique(), df.names.unique()[0], id='dropdown-selection_name'),
        ],
        width={'size': 6, 'order': 2}),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='input_count',
                type='number',
                placeholder='Enter the number of records',
                value=default_value
            ),
            dcc.Graph(id='graph-content'),
        ], 
        width=12),
    ]),
])

# сейчас df генерирует новые тестовые данные: добавляю тег - данные обновляются
# когда меняем теги и имена пусть не генерирует новые данные, а только когда даём новый каунт

@callback(
    Output('graph-content', 'figure'),
    [Input('dropdown-selection', 'value'),
    Input('dropdown-selection_name', 'value'),
# добавить инпут
    Input('input_count', 'value')],
    prevent_initial_call=True
)

# добавить ещё один аргумент
def update_graph(selected_tags, selected_name, record_count):
    df = df_for_chart(count=record_count)
    dff = df[df['tags'].isin(selected_tags) & (df.names == selected_name)]
    # dff = df[df.tags.isin(selected_tags) & df.names.isin(selected_names)]
    # dff = df[(df.tags == selected_tag) & (df.names == selected_name)]
    return px.line(dff, x='times', y='moods')

if __name__ == '__main__':
    app.run(debug=True)
