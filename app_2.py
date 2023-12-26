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


app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.tags.unique(), df.tags.unique(), id='dropdown-selection', multi=True),
    dcc.Dropdown(df.names.unique(), df.names.unique()[0], id='dropdown-selection_name'),
    dcc.Graph(id='graph-content')
])
# посмотреть на кор компоненты (в телеграм) и https://dash.plotly.com/dash-html-components
# https://plotly.com/examples/ 
# https://community.plotly.com/t/holiday-community-app-building-challenge/70393/4?_gl=1*1yqa3g6*_ga*NDU4NDk4MjQ0LjE3MDIzMjMyOTc.*_ga_6G7EE0JNSC*MTcwMzEwNTkyNy40LjEuMTcwMzEwNjAwOS40Ni4wLjA
# склонировать репозиторий, посмотреть, что будет, если я удалю лэйаут или меняю:
# узнать, как оно ломается и какие компоненты что дают

@callback(
    Output('graph-content', 'figure'),
    [Input('dropdown-selection', 'value'),
    Input('dropdown-selection_name', 'value')],
    prevent_initial_call=True
)

# на 1 таймстамп должен быть 1 человек

# посмотреть ссылку на стаковерфлоу и исправить функцию (передавали строку, а теперь список)
# https://stackoverflow.com/questions/12096252/use-a-list-of-values-to-select-rows-from-a-pandas-dataframe
def update_graph(selected_tag, selected_name):
    dff = df[(df.tags == selected_tag) & (df.names == selected_name)]
    return px.line(dff, x='times', y='moods')

if __name__ == '__main__':
    app.run(debug=True)
