import logging

import dash
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from config import Config
import pandas as pd
import argparse


def init_dashboard(dash_app, data_dir):
    df = pd.read_csv(data_dir, index_col=0)
    #
    # df = df[df['State'] != 'United States']
    # df = df[["Week Ending Date", "State", "Observed Number", "Upper Bound Threshold", "Average Expected Count",
    #          "Total Excess Estimate", "Percent Excess Estimate"]]

    date_col = dash_app.server.config["DATE_COL"]
    ratio_cols = dash_app.server.config["RATIO_COLS"]
    dropdown_col = dash_app.server.config["DROP_DOWN_COL"]

    # make the data frame sorted by the date
    df[date_col] = pd.to_datetime(df[date_col], format='%Y-%m-%d')
    df = df.sort_values(date_col)

    # parse date range
    daterange = list(df[date_col].unique())

    # parse RATIO_COLS values, which is the groups of the data
    groups = ratio_cols + ["Disable"] if ratio_cols else None

    # parse dropdown values
    targets = list(df[dropdown_col].unique()) + ["All"] if dropdown_col else None

    # parse the other columns as the data shown in the graph as options
    data_cols = [col for col in df.columns if col not in [date_col, dropdown_col] + groups]

    controls = dbc.Card(
        [
            # the filter
            html.H4("Target:") if targets is not None else None,
            dcc.Dropdown(
                targets,
                "All",
                id='dropdown_filter',
                multi=False
            ) if targets is not None else None,

            # the date range picker
            html.H4("Date Range:"),
            dcc.DatePickerRange(
                id='daterangepicker',
                min_date_allowed=pd.Timestamp(min(daterange)),
                max_date_allowed=pd.Timestamp(max(daterange)),
                start_date=pd.Timestamp(min(daterange)),
                end_date=pd.Timestamp(max(daterange))
            ),

            # the group by picker
            html.H4("Group by:") if groups is not None else None,
            dcc.RadioItems(
                groups,
                groups[0],
                inline=True,
                id='groupby_radio',
                inputStyle={"marginLeft": "10px", "marginRight": "3px"}
            ) if groups is not None else None,

            # the data column to visualize
            html.H4("Data Options:"),
            dcc.Checklist(
                data_cols,
                [data_cols[0], data_cols[1]],
                inline=False,
                id='data_checklist'
            ),
            dcc.Input(id="none", value=None, style={'display': 'none'}),

            html.H4("Plots:"),
            dcc.RadioItems(
                ["Line", "Scatter"],
                "Line",
                inline=True,
                id='plot_radio',
                inputStyle={"marginLeft": "10px", "marginRight": "3px"}
            ),
            html.Hr()
        ]
    )

    dash_app.layout = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.H1(
                            dash_app.server.config["SITE_NAME"],
                            style={"margin": "10px"}
                        )
                    ),
                    dbc.Col(
                        html.H3(
                            f"By {dash_app.server.config['AUTHOR']}"
                        )
                    )
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [controls]
                        ),
                        width=12, xs=12, sm=12, md=12, lg=6
                    ),
                    dbc.Col(
                        html.Div(
                            [dcc.Graph(id="graph")]
                        ),
                        width=12, xs=12, sm=12, md=12, lg=6
                    )
                ]
            ),
        ]
    )

    @callback(
        Output('graph', 'figure'),
        # get the dates from the date range picker
        Input('daterangepicker', 'start_date'),
        Input('daterangepicker', 'end_date'),
        Input('data_checklist', 'value'),
        Input('plot_radio', 'value'),
        Input('dropdown_filter', 'value') if targets is not None else Input('none', 'value'),
        Input('groupby_radio', 'value') if groups is not None else Input('none', 'value'),
    )
    def update_graph(start_date, end_date, column_names, plot, target, group):
        try:
            data = df

            if target:
                if target != "All":
                    data = data[data[dropdown_col] == target]
                else:
                    data = df

            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            # data[date_col] = pd.to_datetime(df[date_col], format='%y-%m-%d')

            data = data[(data[date_col] >= start_date) & (data[date_col] <= end_date)]

            fig = go.Figure()

            if group and group != "Disable":
                for column_name in column_names:
                    for group_name, group_df in data.groupby(group):
                        fig.add_trace(
                            go.Scatter(
                                x=group_df[date_col],
                                y=group_df[column_name],
                                mode='lines' if plot == "Line" else 'markers',
                                name=column_name + " of " + group_name
                            )
                        )
            else:
                for column_name in column_names:
                    fig.add_trace(
                        go.Scatter(
                            x=data[date_col],
                            y=data[column_name],
                            mode='lines' if plot == "Line" else 'markers',
                            name=column_name
                        )
                    )

            return fig
        except Exception as e:
            return html.Div(f"An error occurred: {e}")

    return dash_app


if __name__ == '__main__':
    app = Dash(__name__)
    app.server.config.from_object(Config)

    parser = argparse.ArgumentParser(description='Specify the Host and Port for run the web application')
    parser.add_argument('--host', type=str,
                        help='The host on which the web server will listen')
    parser.add_argument('--port', type=int,
                        help='The port on which the web server will listen')
    parser.add_argument('--debug', type=bool, help='The DEBUG option of Flask.run')
    args = parser.parse_args()

    dash_app = init_dashboard(app, app.server.config['DATA_DIR'])

    dash_app.run(
        debug=args.debug,
        host=args.host,
        port=args.port,
    )
# 	dash_app.run(debug=True, host=dash_app.server.config['APP_HOST'], port=dash_app.server.config['APP_PORT'])
