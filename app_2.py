import ssl
import time

import random
from datetime import datetime as dt

import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, callback, dcc, html, ctx
from faker import Faker

import fake_db

ssl._create_default_https_context = ssl._create_unverified_context

faker = Faker()

# def df_for_chart(num_users=10, count=100):

#     users = [f"{faker.first_name()} {faker.last_name()}" for _ in range(num_users)]
#     tags = ['foo', 'bar', 'buzz', 'boo', 'puk', 'srenk']
#     times = [
#         faker.date_time_between(start_date=dt(2020, 10, 1, 12, 0, 0),
#                                 end_date=dt.now(),).strftime('%Y-%m-%d %H:%M:%S') for _ in range(count)
#     ]
#     dates_to_unixtime = [int(time.mktime(dt.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple())) for s in times]

#     d = {
#         'names': random.choices(users, k=count),
#         'moods': random.choices(list(range(-2, 3)), k=count),
#         'tags': random.choices(tags, k=count),
#         'times': times,
#         'unix_dates': dates_to_unixtime,
#     }
#     df = pd.DataFrame(data=d)
#     df.sort_values(by='times', inplace=True)

#     # column_names = df.columns
#     # print(list(column_names))

#     return df


import sqlite3
from sqlite3 import Error
from database import DATABASE_NAME
DATABASE_NAME = 'fake_db.sqlite'

 
def df_for_chart_from_db():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
    except Error as e:
        print(e)

    query = '''SELECT records.record_date, users.username, tags.tag, moods.mood_rate FROM records
        INNER JOIN records_to_tags ON records.record_id = records_to_tags.record_id
        INNER JOIN tags ON records_to_tags.tag_id = tags.tag_id
        INNER JOIN users ON records.user_id = users.user_id
        INNER JOIN moods ON records.mood_id = moods.mood_id;'''

    df = pd.read_sql(query, conn)
    df = df.rename(columns={
        'record_date': 'times',
        'username': 'names',
        'tag': 'tags',
        'mood_rate': 'moods'
    })

    dates_to_unixtime = [int(time.mktime(dt.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple())) for s in df['times']]
    df['unix_dates'] = dates_to_unixtime
    df.sort_values(by='times', inplace=True)

    return df




df = df_for_chart_from_db()


app = Dash(__name__)
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

default_value = 100
initial_df = df_for_chart_from_db()
initial_tags = initial_df.tags.unique()

modal = dbc.Modal(
    [
        dbc.ModalHeader('Confirmation'),
        dbc.ModalBody('Do you want to regenerate the dataframe?'),
        dbc.ModalFooter(
        dbc.Button('Yes', id='confirm-button')
        ),
    ],
    id='modal',
    is_open=False,
)
store = dcc.Store(id='modal-state')



app.layout = dbc.Container([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dbc.Row([
        dbc.Col([
            dbc.Accordion([
                dbc.AccordionItem(
                    [dcc.Dropdown(df.tags.unique(), df.tags.unique(), id='dropdown-selection-tag', multi=True)],
                    title='Tags',
                ),
            ]),
        ], width={'size': 6, 'order': 2}),
        dbc.Col([
            dbc.Accordion([
                dbc.AccordionItem(
                    [dcc.Dropdown(df.names.unique(), df.names.unique()[0], id='dropdown-selection-name'),],
                    title='Names',
                ),
            ]),
        ], width={'size': 6, 'order': 2}),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Input(
                id='input_count',
                type='number',
                placeholder='Enter the number of records',
                value=default_value
            ),
        ], 
        width={'size': 6, 'order': 2}),
        dbc.Col([
            dbc.Button('update dataframe', id='popup-button'),
                modal,
                dcc.Store(id='df-store'),
        ], 
        width={'size': 6, 'order': 2}),
    ]),
    html.Br(),
    html.Div([
        dcc.RangeSlider(
            id='my-dates-range-slider',
            min=df.unix_dates.unique().tolist()[0],
            max=df.unix_dates.unique().tolist()[-1],
            value=(df.unix_dates.unique().tolist()[0], df.unix_dates.unique().tolist()[-1]),
            step=None,
            marks={t : 
                   {"label": str(d.split(' ')[0]), 
                    "style": {"transform": "rotate(45deg)",
                              'font_family': 'Arial',
                              'font_size': '3px',
                              'text_align': 'center'
                              }
                    } for t, d  in zip(df['unix_dates'], df['times'])
            },
        ),
    ], style={'marginBottom': '1em'}),
    html.Br(),
    dbc.Row([
        dbc.Col([
             dcc.Graph(id='graph-content'),],
             width=12),
    ]),
])

@app.callback(
    Output('modal', 'is_open'),
    [Input('popup-button', 'n_clicks'),
     Input('confirm-button', 'n_clicks')],
    [State('modal', 'is_open')],
)
def toggle_modal(popup_clicks, confirm_clicks, is_open):
    if popup_clicks:
        return not is_open
    return is_open

@callback(
    Output('graph-content', 'figure'),
    Output('dropdown-selection-tag', 'options', allow_duplicate=True),
    Output('dropdown-selection-tag', 'value', allow_duplicate=True),
    Output('my-dates-range-slider', 'marks', allow_duplicate=True),
    Output('my-dates-range-slider', 'value', allow_duplicate=True),
    [Input('dropdown-selection-tag', 'value'),
    Input('dropdown-selection-name', 'value'),
    Input('df-store', 'data'),
    Input('my-dates-range-slider', 'value'),],
    prevent_initial_call=True
)
def update_graph(selected_tags, selected_name, graph_data, dates_slider):

    # будет проблема с датами: в каком виде скормить датафрейму дату, чтобы можно было

    kwargs = dict()

    kwargs['selected_tags'] = selected_tags
    kwargs['selected_name'] = selected_name


    df = pd.DataFrame(graph_data)

    # tag_filter = df['tags'].isin(selected_tags)
    # names_filter = df.names == selected_name
    
    # заменить эту штуку ниже
    if len(dates_slider) == 1:
        kwargs['one_date'] = dates_slider[0]
        # 1 вопросик
        # вызов функции из fake_db create_query_string()
        # dates_filter = df['unix_dates'] == dates_slider[0]
    else:
        kwargs['two_dates'] = (dates_slider[0], dates_slider[1])
        # dates_filter = (dates_slider[0] <= df['unix_dates']) & (df['unix_dates'] <= dates_slider[1])

    
    if ctx.triggered_id == 'dropdown-selection-name':
        # вместо dff будем вызвывать функцию из fake_db create_query_string()
        kwargs = {k:v for (k, v) in kwargs.items() if k=='selected_name'}
        full_query = fake_db.create_query_string(kwargs)

        dff = pd.read_sql(full_query, conn)
        tags_values = sorted(dff.tags.unique())
        slider_values = dates_slider

    elif ctx.triggered_id == 'my-dates-range-slider':
        # тут использую словарь, в котором лежит всё (он у меня уже есть)
        dff = df[tag_filter & names_filter & dates_filter]
        dff_tags = df[names_filter & dates_filter]
        tags_values = sorted(dff_tags.tags.unique())
        slider_values = dates_slider
    else:
        dff = df[tag_filter & names_filter & dates_filter]
        tags_values = selected_tags
        if not tags_values:
            raise PreventUpdate
        # довильтровать датафрейм пандасом
        dff_slider = df[tag_filter & names_filter]
        slider_values = sorted(dff_slider.unix_dates)
        slider_values = [slider_values[0], slider_values[-1]]

    dff_names = df[names_filter]


    if dff.empty:
        raise PreventUpdate

    # tags_options = dff_names.tags.unique() (здесь фильтровано по имени, пока забудем)
    tags_options = fake_db.get_all_tags()


    marks = {t : 
                {"label": str(d.split(' ')[0]),
                 "style": {"transform": "rotate(45deg)",
                            'font_family': 'Arial',
                            'font_size': '3px',
                            'text_align': 'center'
                            }
                } for t, d  in zip(dff_names['unix_dates'], dff_names['times'])
    }

    return px.line(dff, x='times', y='moods'), tags_options, tags_values, marks, slider_values


@callback(
    Output('dropdown-selection-name', 'options'),
    Output('dropdown-selection-name', 'value'),
    Output('dropdown-selection-tag', 'options'),
    Output('dropdown-selection-tag', 'value'),
    Output('df-store', 'data'),
    Output('my-dates-range-slider', 'value'),
    Output('my-dates-range-slider', 'marks'),
    Input('confirm-button', 'n_clicks'),
    State('input_count', 'value'),
    suppress_callback_exceptions=True
)
def reset_data(confirm_clicks, record_count):

# получить record_count из инпута, передать в regenerate_db как параметр
# 2 шага: пересоздать базу, забрать данные селектом () df_for_chart_from_db

# посмотреть, новая ли база, фильтруется ли, всё ли работает

    fake_db.regenerate_db(record_count)
    df = df_for_chart_from_db()

    tags = df.tags.unique()
    names = df.names.unique()
    dates = df.unix_dates.unique()

    marks = {t : 
                {"label": str(d.split(' ')[0]), 
                 "style": {"transform": "rotate(45deg)",
                            'font_family': 'Arial',
                            'font_size': '3px',
                            'text_align': 'center'
                            }
                } for t, d  in zip(df['unix_dates'], df['times'])
    }

    return names, names[0], tags, tags, df.to_dict('list'), [dates[0], dates[-1]], marks

if __name__ == '__main__':
    df = df_for_chart_from_db()
    # print(df)
    app.run(debug=True)
