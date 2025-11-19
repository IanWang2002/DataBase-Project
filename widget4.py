from dash import html, dcc, Input, Output, State
import dash
import mysql_utils
import random

def layout():
    return html.Div([
        html.Div([
            html.H3("🌟 Faculty Spotlight", style={
                "color": "#6366f1", "fontWeight": "bold",
                "marginBottom": "12px", "fontFamily": "Inter, sans-serif",
                "fontSize": "20px", "letterSpacing": ".01em"
            }),
            html.Button(
                "🎲 Next Faculty",
                id="w4-next-faculty",
                n_clicks=0,
                style={
                    "background": "linear-gradient(90deg, #06b6d4 0%, #6366f1 100%)",
                    "color": "white", "border": "none", "borderRadius": "8px",
                    "padding": "8px 22px", "fontWeight": "600", "fontSize": "15px",
                    "boxShadow": "0 2px 8px rgba(6,182,212,.09)", "marginBottom": "8px",
                    "transition": "background .25s"
                }
            ),
            dcc.Loading(html.Div(id="w4-faculty-spotlight"), color="#6366f1"),
        ], style={
            "background": "rgba(236,240,241,0.38)",
            "borderRadius": "14px",
            "padding": "20px 20px 18px 20px",
            "marginBottom": "24px",
            "boxShadow": "0 6px 22px rgba(99,102,241,0.09)",
            "maxWidth": "430px",
            "margin": "0 auto"
        }),

        html.Hr(style={
            "borderTop": "2px dashed #a5b4fc", "margin": "40px 0 30px 0"
        }),

        html.Div([
            html.H3("✏️ Update Faculty Position", style={
                "color": "#06b6d4", "fontWeight": "bold", "marginBottom": "16px"
            }),
            html.Div([
                dcc.Input(
                    id="w4-faculty-name",
                    type="text",
                    placeholder="Faculty Name",
                    style={
                        "marginRight": "10px", "borderRadius": "8px", "border": "1.5px solid #d1d5db",
                        "padding": "10px", "fontSize": "14px", "width": "180px"
                    }
                ),
                dcc.Input(
                    id="w4-new-position",
                    type="text",
                    placeholder="New Position",
                    style={
                        "marginRight": "10px", "borderRadius": "8px", "border": "1.5px solid #d1d5db",
                        "padding": "10px", "fontSize": "14px", "width": "180px"
                    }
                ),
                html.Button(
                    "✨ Update Position",
                    id="w4-update-position",
                    n_clicks=0,
                    style={
                        "background": "linear-gradient(90deg, #06b6d4 0%, #6366f1 100%)",
                        "color": "white", "border": "none", "borderRadius": "8px",
                        "padding": "10px 22px", "fontWeight": "700", "fontSize": "15px", "letterSpacing": ".03em",
                        "boxShadow": "0 2px 8px rgba(6,182,212,.09)", "cursor": "pointer", "transition": "all .15s"
                    }
                ),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "10px", "gap": "6px"}),
            html.Div(id="w4-update-result", style={"marginTop": "18px"})
        ], style={
            "background": "rgba(255,255,255,0.98)", "borderRadius": "16px",
            "padding": "30px 24px", "boxShadow": "0 8px 32px rgba(6,182,212,0.08)",
            "maxWidth": "540px", "margin": "0 auto"
        }),
    ], style={
        "maxWidth": "900px", "margin": "0 auto", "background": "none", "padding": "24px"
    })

def get_random_faculty():
    data = mysql_utils.get_faculty_analytics() or []
    if not data:
        return None
    return random.choice(data)

def make_faculty_card(fac):
    # Debug print to see what data we have
    print(f"Widget Debug - Faculty data received: {fac}")
    print(f"Widget Debug - Email value: '{fac.get('email')}' (type: {type(fac.get('email'))})")
    print(f"Widget Debug - University value: '{fac.get('university')}' (type: {type(fac.get('university'))})")
    print(f"Widget Debug - Position value: '{fac.get('position')}' (type: {type(fac.get('position'))})")
    
    return html.Div([
        html.Div([
            html.Div("👤", style={
                "fontSize": "34px", "marginRight": "18px",
                "background": "linear-gradient(90deg,#6366f1 0%,#06b6d4 80%)",
                "borderRadius": "50%", "width": "46px", "height": "46px",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "color": "white", "boxShadow": "0 2px 7px rgba(99,102,241,0.11)"
            }),
            html.Div([
                html.H4(fac['name'], style={
                    "margin": "0", "fontWeight": "bold",
                    "fontFamily": "Inter,sans-serif", "fontSize": "18px"
                }),
                # Add position back
                html.Div(
                    f"📌 {fac.get('position') or 'Position Not Listed'}",
                    style={"color": "#6366f1", "fontSize": "13.5px", "marginTop": "1px"}
                ),
                html.Div(
                    f"🏫 {fac.get('university') or 'University Not Listed'}",
                    style={"color": "#06b6d4", "fontSize": "13px"}
                ),
                # Fix email display logic - more explicit
                html.Div(
                    f"✉️ {fac.get('email') if fac.get('email') is not None and fac.get('email') != '' else 'Email not available'}",
                    style={"color": "#374151", "marginTop": "6px", "fontSize": "13px"}
                )
            ])
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "5px"}),
        html.Div([
            html.Div("✨ This faculty is randomly featured. Click again to meet someone new!", style={
                "fontSize": "12px", "color": "#64748b", "marginTop": "8px"
            })
        ])
    ], style={
        "background": "rgba(255,255,255,0.97)", "padding": "18px", "borderRadius": "12px",
        "boxShadow": "0 2px 8px rgba(99,102,241,0.10)", "marginTop": "3px",
        "transition": "all .18s", "animation": "fadeIn 0.7s"
    })



def register_callbacks(app):
    @app.callback(
        Output("w4-faculty-spotlight", "children"),
        Input("w4-next-faculty", "n_clicks")
    )
    def show_faculty_spotlight(n):
        fac = get_random_faculty()
        if not fac:
            return html.Div("No faculty data found.", style={"color": "#f59e0b"})
        return make_faculty_card(fac)

    @app.callback(
        Output("w4-update-result", "children"),
        Input("w4-update-position", "n_clicks"),
        State("w4-faculty-name", "value"),
        State("w4-new-position", "value"),
    )
    def update_faculty_position(n, faculty_name, new_position):
        if not n:
            return ""
        if not faculty_name or not new_position:
            return html.Div("⚠️ Please provide both faculty name and new position.", style={"color": "#f59e0b", "fontWeight": "500"})
        result = mysql_utils.update_faculty_position(faculty_name, new_position)
        if isinstance(result, dict) and "error" in result:
            return html.Div(f"❌ Error: {result['error']}", style={"color": "#e74c3c", "fontWeight": "bold"})
        return html.Div([
            html.Div("✅ Position updated!", style={"fontWeight": "bold", "color": "#10b981", "fontSize": "16px"}),
            html.Div([
                html.Span("👤 ", style={"fontSize": "16px"}),
                html.Span(f"{result['name']}"),
                html.Br(),
                html.Span("📌 ", style={"fontSize": "15px"}),
                html.Span(f"New Position: {result['position']}"),
                html.Br(),
                html.Span("✉️ ", style={"fontSize": "15px"}),
                html.Span(f"{result['email']}")
            ], style={"color": "#374151", "marginTop": "8px", "fontSize": "13.5px"})
        ])

# If you want the animation "fadeIn" effect, add this CSS to your project:
'''
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px);}
  to { opacity: 1; transform: none;}
}
'''

