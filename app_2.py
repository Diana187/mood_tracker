import ssl
import datetime, time

import random
from datetime import datetime as dt

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, callback, dcc, html
from faker import Faker

ssl._create_default_https_context = ssl._create_unverified_context

faker = Faker()

def df_for_chart(num_users=10, count=100):

    users = [f"{faker.first_name()} {faker.last_name()}" for _ in range(num_users)]
    tags = ['foo', 'bar', 'buzz', 'boo', 'puk', 'srenk']
    times = [
        faker.date_time_between(start_date=dt(2020, 10, 1, 12, 0, 0),
                                end_date=dt.now(),).strftime('%Y-%m-%d %H:%M:%S') for _ in range(count)
    ]
    dates_to_unixtime = [int(time.mktime(datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').timetuple())) for s in times]

    d = {
        'names': random.choices(users, k=count),
        'moods': random.choices(list(range(-2, 3)), k=count),
        'tags': random.choices(tags, k=count),
        'times': times,
        'unix_dates': dates_to_unixtime,
    }
    df = pd.DataFrame(data=d)
    df.sort_values(by='times', inplace=True)

    return df

df = df_for_chart(count=1000)


app = Dash(__name__)
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

default_value = 10
initial_df = df_for_chart()
initial_tags = initial_df.tags.unique().tolist()

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
    # пытаюсь добавить слайдер
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
                               }} for t, d  in zip(df['unix_dates'], df['times'])
            },
        ),
    ]),
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
    [Input('dropdown-selection-tag', 'value'),
    Input('dropdown-selection-name', 'value'),
    Input('df-store', 'data'),
    Input('my-dates-range-slider', 'value'),],
    prevent_initial_call=True
)
def update_graph(selected_tags, selected_name, graph_data, dates_slider):

    df = pd.DataFrame(graph_data)
    tag_filter = df['tags'].isin(selected_tags)
    names_filter = df.names == selected_name
    dates_filter = (dates_slider[0] <= df['unix_dates']) & (df['unix_dates'] <= dates_slider[1])

    dff = df[tag_filter & names_filter & dates_filter]
    return px.line(dff, x='times', y='moods')

@callback(
    Output('dropdown-selection-name', 'options'),
    Output('dropdown-selection-name', 'value'),
    Output('dropdown-selection-tag', 'options'),
    Output('dropdown-selection-tag', 'value'),
    Output('df-store', 'data'),
# добавила аутпут слайдера
    Output('my-dates-range-slider', 'value'),
    Output('my-dates-range-slider', 'marks'),
    Input('confirm-button', 'n_clicks'),
    State('input_count', 'value'),

    suppress_callback_exceptions=True
)
def reset_data(confirm_clicks, record_count):
    df = df_for_chart(count=record_count)

    tags = df.tags.unique().tolist()
    names = df.names.unique().tolist()

    dates = df.unix_dates.unique().tolist()

    marks = {t : 
                {"label": str(d.split(' ')[0]), 
                    "style": {"transform": "rotate(45deg)",
                            'font_family': 'Arial',
                            'font_size': '3px',
                            'text_align': 'center'
                            }} for t, d  in zip(df['unix_dates'], df['times'])
    }


    # dates = (dates[0] <= df['start_utime']) & (df['start_utime'] <= dates[1])
    # dates = df_fil.start_dt.sort_values().dt.strftime('%Y-%m-%d %H:%M:%S')
    # dates = dates.unique().tolist()

    # return names, names[0], tags, tags, df.to_dict('records')
    return names, names[0], tags, tags, df.to_dict('list'), [dates[0], dates[-1]], marks

if __name__ == '__main__':
    app.run(debug=True)
