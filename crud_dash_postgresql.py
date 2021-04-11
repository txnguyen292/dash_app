import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)
app.server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgres://vwvhbybspjcccl:464f589136edaaff748587a458e6455a0d5fdf9fa891ddfd1a16fc80cf8e9429@ec2-54-196-33-23.compute-1.amazonaws.com:5432/d9ujt986vme90j"


db = SQLAlchemy(app.server)

class Product(db.Model):
    __tablename__ = "productlist"

    Phone = db.Column(db.String(40), nullable=False, primary_key=True)
    Version = db.Column(db.String(40), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Sales = db.Column(db.Integer, nullable=False)

    def __init__(self, phone, version, price, sales):
        self.Phone = phone
        self.Version = version
        self.Price = price
        self.Sales = sales

#----------------------------------------------------------------------------------------------------------

app.layout = html.Div([
    html.Div([
        dcc.Input(
            id="adding-rows-name",
            placeholder="Enter a column name...",
            value='',
            style={"padding": 10}
        ),
        html.Button("Add Column", id="adding-columns-button", n_clicks=0)

    ], style={"height":50}),
    dcc.Interval(id="interval_pg", interval=86400000*7, n_intervals=0),
    html.Div(id="postgres_datatable"),
    html.Button("Add Row", id="editing-rows-button", n_clicks=0),
    html.Button("Save to PostgreSQL", id="save_to_postgres", n_clicks=0),

    # Create notification when saving to excel
    html.Div(id="placeholder", children=[]),
    dcc.Store(id="store", data=0),
    dcc.Interval(id="interval", interval=1000),
    dcc.Graph(id="my_graph")
])

#------------------------------------------------------------------------------------------------------

@app.callback(Output("postgrees_datatable", "children"),
                [Input("interval_pg", "n_intervals")])
def populate_datatable(n_intervals):
    df = pd.read_sql_table("productlist", con=db.engine)
    return [
        dash_table.DataTable(
            id="our-table",
            columns=[{
                "name": str(x),
                "id": str(x),
                "deletable": False,
            } if x == "Sales" or x == "Phone"
            else {
                "name": str(x),
                "id": str(x),
                "deletable": True,
            } for x in df.columns],
            data=df.to_dict("records"),
            editable=True,
            row_deletable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="single",
            page_action="none",
            style_table={"height": "300px", "overflowY": "auto"},
            style_cell={"textAlign": "left", "minWidth": "100px", "width": "100px", "maxWidth": "100px"},
            style_cell_conditional=[
                {
                    "if": {"column_id": c},
                    "textAlign": "right"
                } for c in ["Price", "Sales"]
            ]
        ),
    ]