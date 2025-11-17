# app.py

import dash
from dash import html, dcc, Input, Output, State, callback_context
import widget1, widget2, widget3, widget4, widget5, widget6
import mysql_utils

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Academic World Dashboard"
server = app.server   # 👈 ADD THIS LINE

# Header Section
header = html.Div(
    className="header",
    children=[
        html.H1("Academic World Dashboard", className="title"),
        html.P("Explore keywords, researchers, and collaborations across universities."),
    ]
)

# Dashboard Layout (Grid)
grid_layout = html.Div(
    id="grid",
    className="dashboard-grid",
    children=[
        widget1.layout(),
        widget2.layout(),
        widget3.layout(),
        widget4.layout(),
        widget5.layout(),
        widget6.layout()
    ]
)

# Final Layout
app.layout = html.Div(
    id="root",
    className="page-root",
    children=[header, grid_layout]
)

# 🧠 Callback Registration (One per widget)
widget1.register_callbacks(app)
widget2.register_callbacks(app)
widget3.register_callbacks(app)
widget4.register_callbacks(app)
widget5.register_callbacks(app)
widget6.register_callbacks(app)

# 🚀 Launch App (only for local debugging)
if __name__ == "__main__":
    app.run(debug=True)
