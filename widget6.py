# widget6.py - Dashboard widget (Fixed version)
from dash import html, dcc, Input, Output, State
from mongodb_utils import get_keywords_by_university, get_university_faculty_count
import plotly.graph_objs as go
import plotly.express as px

def layout():
    """Create the layout for Widget 6"""
    return html.Div(
        id="widget6",
        className="widget",
        children=[
            html.H3("🏫 University Research Keywords Explorer", 
                   style={"color": "#2c3e50", "marginBottom": "20px"}),
            
            html.P("Discover the top research keywords at any university", 
                  style={"color": "#7f8c8d", "marginBottom": "15px"}),
            
            html.Div([
                dcc.Input(
                    id="uni-input",
                    type="text",
                    placeholder="Enter University Name (e.g., University of Illinois)",
                    style={
                        "width": "300px",
                        "padding": "8px",
                        "marginRight": "10px",
                        "border": "1px solid #bdc3c7",
                        "borderRadius": "4px"
                    }
                ),
                html.Button(
                    "Search Keywords", 
                    id="uni-keyword-btn",
                    style={
                        "padding": "8px 16px",
                        "backgroundColor": "#3498db",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "4px",
                        "cursor": "pointer"
                    }
                ),
            ], style={"marginBottom": "20px"}),
            
            # Info display
            html.Div(id="uni-info", style={"marginBottom": "15px"}),
            
            # Chart - Optimized for vertical bars
            dcc.Graph(
                id="uni-keyword-chart",
                style={"height": "650px", "width": "100%"}  # Taller height for vertical bars
            )
        ],
        style={
            "padding": "20px",
            "border": "1px solid #ecf0f1",
            "borderRadius": "8px",
            "backgroundColor": "#ffffff",
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
        }
    )

def register_callbacks(app):
    """Register callbacks for Widget 6"""
    
    @app.callback(
        [Output("uni-keyword-chart", "figure"),
         Output("uni-info", "children")],
        Input("uni-keyword-btn", "n_clicks"),
        State("uni-input", "value"),
        prevent_initial_call=True
    )
    def update_university_keywords(n_clicks, university_name):
        """Update the keyword chart and info display"""
        
        if not n_clicks or not university_name:
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="Enter a university name and click 'Search Keywords'",
                xaxis={"visible": False},
                yaxis={"visible": False},
                annotations=[{
                    "text": "No data to display",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "xanchor": "center",
                    "yanchor": "middle",
                    "showarrow": False,
                    "font": {"size": 16, "color": "#7f8c8d"}
                }]
            )
            return empty_fig, ""
        
        university_name = university_name.strip()
        
        # Get keywords and faculty count
        keywords, counts = get_keywords_by_university(university_name, limit=15)
        faculty_count = get_university_faculty_count(university_name)
        
        # Create info display
        if not keywords:
            info_div = html.Div([
                html.P(f"❌ No research keywords found for '{university_name}'", 
                      style={"color": "#e74c3c", "fontWeight": "bold"}),
                html.P("Try checking the spelling or using a different university name.", 
                      style={"color": "#7f8c8d"})
            ])
            
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title=f"No Keywords Found for {university_name}",
                xaxis={"visible": False},
                yaxis={"visible": False},
                annotations=[{
                    "text": "No research keywords found for this university",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "xanchor": "center",
                    "yanchor": "middle",
                    "showarrow": False,
                    "font": {"size": 16, "color": "#e74c3c"}
                }]
            )
            return empty_fig, info_div
        
        else:
            info_div = html.Div([
                html.P(f"✅ Found {len(keywords)} top research keywords", 
                      style={"color": "#27ae60", "fontWeight": "bold", "margin": "0"}),
                html.P(f"📊 Based on {faculty_count} faculty members at {university_name}", 
                      style={"color": "#7f8c8d", "margin": "5px 0 0 0"})
            ])
        
        # Create vertical bar chart with proper scaling
        fig = go.Figure(data=[
            go.Bar(
                x=keywords,
                y=counts,
                marker=dict(
                    color=counts,
                    colorscale='viridis',
                    showscale=True,
                    colorbar=dict(title="Frequency", titleside="right")
                ),
                text=counts,
                textposition='outside',
                textfont=dict(size=12, color='#2c3e50'),
                hovertemplate='<b>%{x}</b><br>Frequency: %{y}<extra></extra>'
            )
        ])
        
        # Optimized layout for vertical bars with full visibility
        fig.update_layout(
            title={
                'text': f"Top Research Keywords at {university_name}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#2c3e50'}
            },
            xaxis={
                'title': 'Research Keywords',
                'title_font': {'size': 14},
                'tickangle': -45,          # Angled labels
                'tickfont': {'size': 10},  # Smaller font for long labels
                'automargin': True,        # Auto-adjust margins for labels
                'showgrid': False
            },
            yaxis={
                'title': 'Frequency (Number of Faculty)',
                'title_font': {'size': 14},
                'tickfont': {'size': 12},
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'rgba(0,0,0,0.1)'
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=600,  # Fixed height that works well
            margin={
                'b': 200,  # Large bottom margin for angled labels
                't': 80, 
                'l': 80, 
                'r': 100   # Right margin for value labels
            },
            bargap=0.3,  # More spacing between bars for readability
            font={'size': 12},
            showlegend=False
        )

        return fig, info_div


# ALTERNATIVE SOLUTIONS (choose one):

# SOLUTION 2: Use horizontal bar chart instead
def create_horizontal_chart(keywords, counts, university_name):
    """Alternative: Create horizontal bar chart to avoid label overlap"""
    fig = go.Figure(data=[
        go.Bar(
            y=keywords[::-1],  # Reverse order so highest is at top
            x=counts[::-1],
            orientation='h',
            marker=dict(
                color=counts[::-1],
                colorscale='viridis',
                showscale=True,
                colorbar=dict(title="Frequency")
            ),
            text=counts[::-1],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Frequency: %{x}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': f"Top Research Keywords at {university_name}",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis={
            'title': 'Frequency (Number of Faculty)',
            'title_font': {'size': 14}
        },
        yaxis={
            'title': 'Research Keywords',
            'title_font': {'size': 14},
            'tickfont': {'size': 11}
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin={'b': 60, 't': 80, 'l': 200, 'r': 80},  # More left margin for labels
        bargap=0.2
    )
    
    return fig

# SOLUTION 3: Wrap long labels
def wrap_labels(labels, max_length=15):
    """Wrap long labels to prevent overlap"""
    wrapped = []
    for label in labels:
        if len(label) > max_length:
            # Split at spaces and wrap
            words = label.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= max_length:
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            wrapped.append("<br>".join(lines))
        else:
            wrapped.append(label)
    
    return wrapped