import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from datetime import datetime
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

import random
from faker import Faker

faker = Faker()

def df_for_chart(num_users=10, count=100, past='-3mo'):

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

# добавить поле для ввода
# сложить лэйаут в внешний контейнер
# добавить кнопку (см ноушен, инпут для количества юзеров)
# оба дропдауна сложить в одну строчку: слева и справа, чтобы делили экран на пополам;
# сложить в dbc.row, объявляю две колонки и в каждой колонце по дропдауну
# посмотреть доку, чтобы задать ширину
# добавить простой стиль
app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.tags.unique(), df.tags.unique(), id='dropdown-selection', multi=True),
    dcc.Dropdown(df.names.unique(), df.names.unique()[0], id='dropdown-selection_name'),
    dcc.Graph(id='graph-content')
])

# добавить инпут
@callback(
    Output('graph-content', 'figure'),
    [Input('dropdown-selection', 'value'),
    Input('dropdown-selection_name', 'value')],
    prevent_initial_call=True
)

def update_graph(selected_tags, selected_name):
    # dff = df[df.tags.isin(selected_tags) & df.names.isin(selected_names)]
    dff = df[df['tags'].isin(selected_tags) & (df.names == selected_name)]
    # dff = df[(df.tags == selected_tag) & (df.names == selected_name)]
    return px.line(dff, x='times', y='moods')

if __name__ == '__main__':
    app.run(debug=True)
