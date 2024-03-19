import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from datetime import datetime
from dash import Dash, html, dcc, callback, callback_context, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime as dt

import random
from faker import Faker
 
faker = Faker()

def df_for_chart(num_users=10, count=100):

    users = [f"{faker.first_name()} {faker.last_name()}" for _ in range(num_users)]
    tags = ['foo', 'bar', 'buzz', 'boo', 'puk', 'srenk']
    times = [
        faker.date_time_between(start_date=dt(2020, 10, 1, 12, 0, 0),
                                end_date=dt.now(),).strftime('%Y-%m-%d %H:%M:%S') for _ in range(count)
    ]
    d = {
        'names': random.choices(users, k=count),
        'moods': random.choices(list(range(-2, 3)), k=count),
        'tags': random.choices(tags, k=count),
        'times': times
    }
    df = pd.DataFrame(data=d)
    # добавила из Сашиного дока app_2.py
    df.sort_values(by='times', inplace=True)

    return df

    # times = []
    # for i in range(count):
    #     time = faker.date_time_between_dates(
    #         datetime_start=datetime(2016, 1, 1),
    #         datetime_end=datetime(2016, 7, 21),
    #         tzinfo=None,
    #     )
    #     times.append(time)

    # d = {
    #     'names': [random.choice(users) for _ in range(count)],
    #     'times': times,
    #     'moods': [random.randrange(-2, 3) for _ in range(count)],
    # }
    # df = pd.DataFrame(data=d)
    # df_tags = pd.DataFrame({'tags': tags})
    # df = df.merge(df_tags, how='cross')
    # df = df.sample(count).reset_index().drop(columns=['index'])
    # df['times'] = pd.to_datetime(df['times'])
    # df.sort_values(by='times', inplace=True)

    # return df

df = df_for_chart(count=1000)


app = Dash(__name__)
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

default_value = 10
# добавила из Сашиного дока app_2.py
initial_df = df_for_chart()
initial_tags = initial_df.tags.unique().tolist()

app.layout = dbc.Container([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dbc.Row([
        dbc.Col([
            dbc.Accordion([
                dbc.AccordionItem(
                    [dcc.Dropdown(df.tags.unique(), df.tags.unique(), id='dropdown-selection', multi=True)],
                    title='Tags',
                ),
            ]),
        ], width={'size': 6, 'order': 2}),
        #     dcc.Dropdown(df.tags.unique(), df.tags.unique(), id='dropdown-selection', multi=True),
        # ], width={'size': 6, 'order': 2}),
        dbc.Col([
            dbc.Accordion([
                dbc.AccordionItem(
                    [dcc.Dropdown(df.names.unique(), df.names.unique()[0], id='dropdown-selection_name'),],
                    title='Names',
                ),
            ]),
        ], width={'size': 6, 'order': 2}),
        #     dcc.Dropdown(df.names.unique(), df.names.unique()[0], id='dropdown-selection_name'),
        # ],
        # width={'size': 6, 'order': 2}),
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
    dcc.Store(id='df-store'),
])

# сейчас df генерирует новые тестовые данные: добавляю тег - данные обновляются
# когда меняем теги и имена пусть не генерирует новые данные, а только когда даём новый каунт

# в функцию update_graph нужно добавить if else блок, где логика будет такой:
# данные перегенерируются только при изменении значения input_count
# при изменении в браузере dropdown-selection или dropdown-selection_name, данные остаются без изменений
# как понять, какая штука триггерит обратный вызов?
# опа https://dash.plotly.com/determining-which-callback-input-changed
# dash.callback_context, но всё равно не совсем понимаю, как именно нужно применить


@callback(
    Output('graph-content', 'figure'),
    [Input('dropdown-selection', 'value'),
    Input('dropdown-selection_name', 'value'),
    Input('input_count', 'value')],
    # добавила из Сашиного дока app_2.py
    State('df-store', 'data'),
    prevent_initial_call=True
)

def update_graph(selected_tags, selected_name, record_count):

    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'input_count':
        df = df_for_chart(count=record_count)
    else:
        dff = df[df['tags'].isin(selected_tags) & (df.names == selected_name)]

# как создать датафрейм из набора строк, из него потом сделать датафрейм
# https://pynative.com/pandas-create-dataframe-from-list/
# 131 строчка становится двумя смысловыми шагами

    # df = df_for_chart(count=record_count)
    # dff = df[df['tags'].isin(selected_tags) & (df.names == selected_name)]
    
    # dff = df[df.tags.isin(selected_tags) & df.names.isin(selected_names)]
    # dff = df[(df.tags == selected_tag) & (df.names == selected_name)]
    return px.line(dff, x='times', y='moods')

# добавила из Сашиного дока app_2.py
@callback(
    Output('dropdown-selection-name', 'options'),
    Output('dropdown-selection-name', 'value'),
    Output('dropdown-selection-tag', 'options'),
    Output('dropdown-selection-tag', 'value'),
    Output('df-store', 'data'),
    Input('input_count', 'value'),
    suppress_callback_exceptions=True
)

def reset_data(record_count):
    df = df_for_chart(count=record_count)
        
    tags = df.tags.unique().tolist()
    names = df.names.unique().tolist()

    return names, names[0], tags, tags, df.to_dict('records')

if __name__ == '__main__':
    app.run(debug=True)
