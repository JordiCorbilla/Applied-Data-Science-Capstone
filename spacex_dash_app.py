# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 13:41:22 2024

@author: jordi coll corbilla
"""

import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_data = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_data['Payload Mass (kg)'].max()
min_payload = spacex_data['Payload Mass (kg)'].min()

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'All Sites'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
        ],
        value='All Sites',
        placeholder="Select a launch site",
        searchable=True
    ),
    html.Br(),

    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={i: str(i) for i in range(0, 11000, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'All Sites':
        fig = px.pie(
            spacex_data,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered_data = spacex_data[spacex_data['Launch Site'] == selected_site]
        success_data = (
            filtered_data.groupby(['Launch Site', 'class'])
            .size()
            .reset_index(name='count')
        )
        fig = px.pie(
            success_data,
            values='count',
            names='class',
            title=f'Total Successful Launches for {selected_site}'
        )
    return fig

@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_data = spacex_data[spacex_data['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
    if selected_site == 'All Sites':
        fig = px.scatter(
            filtered_data,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Success Count on Payload Mass for All Sites'
        )
    else:
        site_data = filtered_data[filtered_data['Launch Site'] == selected_site]
        fig = px.scatter(
            site_data,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Success Count on Payload Mass for {selected_site}'
        )
    return fig

if __name__ == '__main__':
    app.run_server(mode='external', port=8050)
