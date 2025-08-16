from dash import html, dcc, Input, Output, State
from mysql_utils import update_faculty_interest

def layout():
    return html.Div(
        id="widget5",
        className="widget",
        children=[
            html.H3("🔬 Update Faculty Research Interest", style={
                "color": "#6366f1", "fontWeight": "bold", "fontSize": "23px", "marginBottom": "15px"
            }),
            html.P("Edit a faculty member's research focus and keep the database up to date.", style={
                "color": "#6b7280", "fontSize": "13.5px", "marginBottom": "18px"
            }),
            html.Div([
                dcc.Input(
                    id="faculty-name",
                    type="text",
                    placeholder="Faculty Name",
                    style={
                        "marginRight": "10px", "borderRadius": "8px", "border": "1.5px solid #d1d5db",
                        "padding": "10px", "fontSize": "14px", "width": "180px"
                    }
                ),
                dcc.Input(
                    id="faculty-interest",
                    type="text",
                    placeholder="New Research Interest",
                    style={
                        "marginRight": "10px", "borderRadius": "8px", "border": "1.5px solid #d1d5db",
                        "padding": "10px", "fontSize": "14px", "width": "220px"
                    }
                ),
                html.Button(
                    "✨ Update Interest",
                    id="update-btn",
                    n_clicks=0,
                    style={
                        "background": "linear-gradient(90deg, #6366f1 0%, #06b6d4 100%)",
                        "color": "white", "border": "none", "borderRadius": "8px",
                        "padding": "10px 24px", "fontWeight": "700", "fontSize": "15px",
                        "boxShadow": "0 2px 8px rgba(99,102,241,.09)", "cursor": "pointer"
                    }
                ),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "8px", "gap": "6px"}),
            html.Div(id="update-result", style={"marginTop": "18px"})
        ],
        style={
            "background": "rgba(255,255,255,0.98)", "borderRadius": "16px",
            "padding": "30px 24px", "boxShadow": "0 8px 32px rgba(6,182,212,0.07)",
            "margin": "0 auto"
        }
    )

def register_callbacks(app):
    @app.callback(
        Output("update-result", "children"),
        Input("update-btn", "n_clicks"),
        State("faculty-name", "value"),
        State("faculty-interest", "value")
    )
    def update_interest(n_clicks, name, interest):
        if not n_clicks:
            return ""
        if not name or not interest:
            return html.Div(
                "⚠️ Please provide both faculty name and new research interest.",
                style={"color": "#f59e0b", "fontWeight": "bold", "fontSize": "14px"}
            )
        result = update_faculty_interest(name.strip(), interest)
        if result.get("success"):
            prev_interest = result.get("prev_interest")
            return html.Div([
                html.Div("✅ Research interest updated!", style={"color": "#10b981", "fontWeight": "bold", "fontSize": "16px"}),
                html.Div([
                    html.Span("👤 ", style={"fontSize": "16px"}),
                    html.Span(f"{name.strip()}"),
                    html.Br(),
                    html.Br(),
                    html.Span("Interest Added: ", style={"color": "#06b6d4"}),
                    html.Span(f"{interest}", style={"fontWeight": "bold", "color": "#06b6d4"})
                ], style={"color": "#374151", "marginTop": "8px", "fontSize": "13.5px"})
            ])
        else:
            return html.Div(
                f"❌ Could not update — {result.get('message', 'please check if the name is correct.')}",
                style={"color": "#e74c3c", "fontWeight": "bold", "fontSize": "14px"}
            )
