# widget1.py - Beautiful Top Research Keywords Widget
from dash import html, dcc
import plotly.graph_objs as go
import plotly.express as px
from mongodb_utils import get_top_keywords
import numpy as np

def layout():
    # Get top keywords and counts from MongoDB
    try:
        keywords, counts = get_top_keywords()
    except Exception as e:
        keywords, counts = [], []
        
    # If nothing is returned, show a beautiful empty state
    if not keywords:
        figure = go.Figure()
        
        # Add a subtle background shape
        figure.add_shape(
            type="circle",
            x0=-0.4, y0=-0.4, x1=0.4, y1=0.4,
            fillcolor="rgba(52, 152, 219, 0.1)",
            line=dict(color="rgba(52, 152, 219, 0.3)", width=2),
            opacity=0.5
        )
        
        figure.update_layout(
            title={
                'text': "📊 Research Keywords Dashboard",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#2c3e50', 'family': 'Arial Black'}
            },
            xaxis={"visible": False, "range": [-1, 1]},
            yaxis={"visible": False, "range": [-1, 1]},
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[{
                "text": "🔍 No keywords available in the database<br><br>📚 Data will appear here once loaded",
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.5,
                "xanchor": "center",
                "yanchor": "middle",
                "showarrow": False,
                "font": {
                    "size": 16, 
                    "color": "#7f8c8d",
                    "family": "Arial"
                }
            }],
            margin={"l": 40, "r": 40, "t": 80, "b": 60}
        )
    else:
        # Create a stunning visualization with the data
        # Generate beautiful gradient colors
        colors = px.colors.qualitative.Set3[:len(keywords)]
        if len(keywords) > len(colors):
            # Extend colors if we have more keywords
            colors = colors * (len(keywords) // len(colors) + 1)
        
        # Create gradient effect based on values
        normalized_counts = np.array(counts) / max(counts)
        gradient_colors = []
        
        for i, norm_val in enumerate(normalized_counts):
            # Create gradient from light blue to dark blue based on value
            intensity = norm_val
            r = int(52 + (100 * (1 - intensity)))   # Red component
            g = int(152 + (50 * (1 - intensity)))   # Green component  
            b = int(219 + (36 * (1 - intensity)))   # Blue component
            gradient_colors.append(f'rgb({r},{g},{b})')
        
        # Create the main bar chart
        figure = go.Figure(data=[
            go.Bar(
                x=keywords,
                y=counts,
                marker=dict(
                    color=gradient_colors,
                    line=dict(color='white', width=2),
                    opacity=0.8
                ),
                text=counts,
                textposition='outside',
                textfont=dict(size=12, color='#2c3e50', family='Arial Bold'),
                hovertemplate='<b>%{x}</b><br>' +
                             '👥 Faculty Count: %{y}<br>' +
                             '📊 Percentage: %{customdata:.1f}%<extra></extra>',
                customdata=[count/sum(counts)*100 for count in counts],
                name="Research Keywords"
            )
        ])
        
        # Add trend line for top keywords
        # Smooth trend line over all keywords
        x_vals = list(range(len(keywords)))
        x_smooth = np.linspace(0, len(keywords)-1, 200)
        y_smooth = np.interp(x_smooth, x_vals, counts)

        figure.add_trace(go.Scatter(
            x=[keywords[int(i)] for i in x_smooth],  # Interpolated keyword names
            y=y_smooth,
            mode='lines',
            line=dict(color='rgba(231, 76, 60, 0.6)', width=2, dash='dot'),
            name='Distribution',
            showlegend=False,
            hoverinfo='skip'
        ))

        
        # Beautiful layout with modern styling
        figure.update_layout(
            title={
                'text': '📊 Top 25 Research Keywords Dashboard',
                'x': 0.5,
                'xanchor': 'center',
                'font': {
                    'size': 24, 
                    'color': '#2c3e50',
                    'family': 'Arial Black'
                },
                'pad': {'b': 25}
            },
            xaxis={
                'title': {
                    'text': '🔬 Research Keywords',
                    'font': {'size': 16, 'color': '#34495e', 'family': 'Arial Bold'}
                },
                'tickangle': 90,
                'tickfont': {'size': 11, 'color': '#2c3e50'},
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'rgba(0,0,0,0.1)',
                'zeroline': False,
                'automargin': True
            },
            yaxis={
                'title': {
                    'text': '👥 Number of Faculty Members',
                    'font': {'size': 16, 'color': '#34495e', 'family': 'Arial Bold'}
                },
                'tickfont': {'size': 12, 'color': '#2c3e50'},
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'rgba(0,0,0,0.1)',
                'zeroline': True,
                'zerolinecolor': 'rgba(0,0,0,0.3)',
                'zerolinewidth': 2
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500,
            margin={'l': 80, 'r': 60, 't': 100, 'b': 200},
            bargap=0.3,
            font={'family': 'Arial'},
            hovermode='x unified',
            hoverlabel={
                'bgcolor': 'white',
                'bordercolor': '#3498db',
                'font': {'size': 13, 'color': '#2c3e50'}
            },
            showlegend=False,
            # Add subtle animation
            transition={
                'duration': 800,
                'easing': 'cubic-in-out'
            }
        )
        
        # Add decorative shapes for visual appeal
        if len(keywords) > 0:
            max_count = max(counts)
            
            # Add subtle background rectangles for visual depth
            for i in range(0, len(keywords), 3):
                figure.add_shape(
                    type="rect",
                    x0=i-0.4, y0=0, x1=i+0.4, y1=max_count * 0.05,
                    fillcolor="rgba(52, 152, 219, 0.05)",
                    line=dict(width=0),
                    layer="below"
                )
        
        # Add annotation with statistics
        if counts:
            total_faculty = sum(counts)
            avg_per_keyword = total_faculty / len(keywords)
            
            figure.add_annotation(
                x=len(keywords) * 0.85,
                y=max(counts) * 0.9,
                text=f"📈 Total: {total_faculty} faculty<br>" +
                     f"📊 Avg: {avg_per_keyword:.1f} per keyword<br>" +
                     f"🔬 Top keyword: {keywords[0]} ({counts[0]})",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#3498db",
                ax=50,
                ay=-50,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#3498db",
                borderwidth=2,
                borderpad=10,
                font=dict(size=12, color="#2c3e50")
            )

    return html.Div(
        id="widget1",
        className="widget",
        children=[
            # Enhanced header section
            html.Div([
                html.H3(
                    "📊 Research Keywords Analytics", 
                    style={
                        "color": "#2c3e50", 
                        "marginBottom": "5px",
                        "fontSize": "26px",
                        "fontWeight": "bold",
                        "fontFamily": "Arial Black"
                    }
                ),
                html.P(
                    "Discover the most popular research areas across faculty members",
                    style={
                        "color": "#7f8c8d",
                        "marginBottom": "20px",
                        "fontSize": "14px",
                        "fontStyle": "italic"
                    }
                ),
                # Add stats cards if we have data
                html.Div([
                    html.Div([
                        html.H4(str(len(keywords)), style={"margin": "0", "color": "#3498db", "fontSize": "24px"}),
                        html.P("Keywords", style={"margin": "0", "color": "#7f8c8d", "fontSize": "12px"})
                    ], style={
                        "textAlign": "center",
                        "padding": "10px",
                        "backgroundColor": "rgba(52, 152, 219, 0.1)",
                        "borderRadius": "8px",
                        "marginRight": "10px",
                        "minWidth": "80px"
                    }),
                    html.Div([
                        html.H4(str(sum(counts)) if counts else "0", style={"margin": "0", "color": "#27ae60", "fontSize": "24px"}),
                        html.P("Total Faculty", style={"margin": "0", "color": "#7f8c8d", "fontSize": "12px"})
                    ], style={
                        "textAlign": "center",
                        "padding": "10px",
                        "backgroundColor": "rgba(39, 174, 96, 0.1)",
                        "borderRadius": "8px",
                        "marginRight": "10px",
                        "minWidth": "80px"
                    }),
                    html.Div([
                        html.H4(keywords[0] if keywords else "N/A", style={"margin": "0", "color": "#e74c3c", "fontSize": "16px"}),
                        html.P("Top Keyword", style={"margin": "0", "color": "#7f8c8d", "fontSize": "12px"})
                    ], style={
                        "textAlign": "center",
                        "padding": "10px",
                        "backgroundColor": "rgba(231, 76, 60, 0.1)",
                        "borderRadius": "8px",
                        "minWidth": "120px"
                    })
                ], style={
                    "display": "flex",
                    "marginBottom": "20px",
                    "flexWrap": "wrap"
                }) if keywords else html.Div()
            ]),
            
            # Enhanced chart container
            html.Div([
                dcc.Graph(
                    id="top-keywords-chart",
                    figure=figure,
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'research_keywords_chart',
                            'height': 500,
                            'width': 1000,
                            'scale': 2
                        }
                    }
                )
            ], style={
                "backgroundColor": "rgba(0,0,0,0)",
                "borderRadius": "10px",
                "padding": "10px"
            })
        ],
        style={
            "padding": "25px",
            "border": "none",
            "borderRadius": "15px",
            "backgroundColor": "#ffffff",
            "boxShadow": "0 8px 25px rgba(0,0,0,0.1)",
            "margin": "10px",
            "fontFamily": "Arial, sans-serif"
        }
    )

def register_callbacks(app):
    pass  # No interactivity needed for this static chart