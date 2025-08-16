# widget2.py - Beautiful Top Faculty by KRC Widget
from dash import html, dcc
import plotly.graph_objs as go
import plotly.express as px
from mysql_utils import get_top_faculty_krc_full
import numpy as np

def layout():
    try:
        data = get_top_faculty_krc_full()
        names = [row["faculty_name"] for row in data]
        krcs = [round(row["krc"], 2) for row in data]
    except Exception as e:
        data, names, krcs = [], [], []
    
    if not data or not names:
        # Beautiful empty state
        figure = go.Figure()
        
        # Add decorative background elements
        figure.add_shape(
            type="circle",
            x0=-0.3, y0=-0.3, x1=0.3, y1=0.3,
            fillcolor="rgba(255, 193, 7, 0.1)",
            line=dict(color="rgba(255, 193, 7, 0.4)", width=2),
            opacity=0.6
        )
        
        figure.add_shape(
            type="star",
            x0=-0.1, y0=-0.1, x1=0.1, y1=0.1,
            fillcolor="rgba(255, 193, 7, 0.3)",
            line=dict(color="rgba(255, 193, 7, 0.8)", width=1)
        )
        
        figure.update_layout(
            title={
                'text': "⭐ Faculty Excellence Dashboard",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#2c3e50', 'family': 'Arial Black'}
            },
            xaxis={"visible": False, "range": [-1, 1]},
            yaxis={"visible": False, "range": [-1, 1]},
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[{
                "text": "📊 No faculty KRC data available<br><br>🔄 Data will appear here once loaded",
                "xref": "paper",
                "yref": "paper",
                "x": 0.5,
                "y": 0.3,
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
        # Create stunning KRC visualization
        
        # Generate beautiful gradient colors based on KRC values
        normalized_krcs = np.array(krcs) / max(krcs) if krcs else []
        
        # Color scheme: Gold to Deep Orange gradient for excellence
        gradient_colors = []
        for norm_val in normalized_krcs:
            # Gold (#FFD700) to Deep Orange (#FF4500) gradient
            intensity = norm_val
            r = int(255)
            g = int(215 - (70 * (1 - intensity)))   # 215 -> 145 -> 69
            b = int(7 * (1 - intensity))            # 7 -> 0
            gradient_colors.append(f'rgb({r},{g},{b})')
        
        # Create ranking colors (top 3 get special treatment)
        ranking_colors = []
        for i, krc in enumerate(krcs):
            if i == 0:  # Gold for #1
                ranking_colors.append('#FFD700')
            elif i == 1:  # Silver for #2
                ranking_colors.append('#C0C0C0')
            elif i == 2:  # Bronze for #3
                ranking_colors.append('#CD7F32')
            else:  # Gradient for others
                ranking_colors.append(gradient_colors[i])
        
        # Shortened names for better display
        display_names = []
        for name in names:
            if len(name) > 15:
                parts = name.split()
                if len(parts) >= 2:
                    display_names.append(f"{parts[0][0]}. {parts[-1]}")
                else:
                    display_names.append(name[:15] + "...")
            else:
                display_names.append(name)
        
        customdata = [[i+1, names[i]] for i in range(len(names))]

        # Create the main bar chart with ranking indicators
        figure = go.Figure()
        
        # Add bars with beautiful styling
        figure.add_trace(go.Bar(
            x=display_names,
            y=krcs,
            marker=dict(
                color=ranking_colors,
                line=dict(color='white', width=2),
                opacity=0.85,
                pattern=dict(
                    shape=["/", "\\", "x"] + [""] * (len(krcs) - 3) if len(krcs) > 3 else [""],
                    fgcolor="rgba(255,255,255,0.3)",
                    fgopacity=0.3,
                    size=8,
                    solidity=0.2
                )
            ),
            text=[f"{krc}" for krc in krcs],
            textposition='outside',
            textfont=dict(size=11, color='#2c3e50', family='Arial Bold'),
            hovertemplate='<b>%{customdata[1]}</b><br>' +        # name
                        '🏆 Rank: #%{customdata[0]}<br>' +    # rank
                        '⭐ KRC Score: %{y}<br>' +
                        '📊 Percentile: %{meta:.1f}%<extra></extra>',
            customdata=customdata,                              # (rank, name)
            meta=[krc/max(krcs)*100 for krc in krcs] if krcs else [],
            name="Faculty KRC"
        ))

        # Add trend line for performance analysis - FIXED VERSION
        # if len(krcs) >= 5:
        #     x_indices = np.arange(len(krcs))
        #     trend_coeffs = np.polyfit(x_indices, krcs, 2)  # Quadratic fit
        #     trend_line = np.polyval(trend_coeffs, x_indices)

        #     figure.add_trace(go.Scatter(
        #         x=display_names,         # Use the bar labels for x!
        #         y=trend_line,            # Fitted y values
        #         mode='lines',
        #         line=dict(color='rgba(231, 76, 60, 0.7)', width=3, dash='dot'),
        #         name='Performance Trend',
        #         showlegend=False,
        #         hoverinfo='skip'
        #     ))

        # Add ranking badges for top 3
        for i in range(min(3, len(krcs))):
            badge_colors = ['#FFD700', '#C0C0C0', '#CD7F32']
            badge_symbols = ['🥇', '🥈', '🥉']
            
            figure.add_annotation(
                x=display_names[i],
                y=krcs[i] + max(krcs) * 0.05,
                text=f"{badge_symbols[i]}",
                showarrow=False,
                font=dict(size=20),
                bgcolor=badge_colors[i],
                bordercolor="white",
                borderwidth=2,
                borderpad=4,
                opacity=0.9
            )
        
        # Beautiful layout configuration
        figure.update_layout(
            title={
                'text': '⭐ Top 25 Faculty KRC Scores Rankings',
                'x': 0.5,
                'xanchor': 'center',
                'font': {
                    'size': 24, 
                    'color': '#2c3e50',
                    'family': 'Arial Black'
                },
                'pad': {'b': 20}
            },
            xaxis={
                'title': {
                    'text': '👨‍🎓 Faculty Members',
                    'font': {'size': 16, 'color': '#34495e', 'family': 'Arial Bold'}
                },
                'tickangle': 90,
                'tickfont': {'size': 10, 'color': '#2c3e50', 'family': 'Arial'},
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'rgba(0,0,0,0.1)',
                'zeroline': False,
                'automargin': True,
                'categoryorder': 'trace'  # Maintain original order
            },
            yaxis={
                'title': {
                    'text': '📈 Keyword-Relevant Citations (KRC)',
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
            height=550,
            margin={'l': 90, 'r': 60, 't': 100, 'b': 200},
            bargap=0.2,
            font={'family': 'Arial'},
            hovermode='x unified',
            hoverlabel={
            'bgcolor': 'white',
            'bordercolor': '#f39c12',
            'font': {'size': 13, 'color': '#2c3e50'}
            # 'borderwidth': 2,    # <-- Remove or comment this out
            },

            showlegend=False,
            # Add subtle animation
            transition={
                'duration': 1000,
                'easing': 'cubic-in-out'
            }
        )
        
        # Add statistical insights annotation
        if krcs:
            avg_krc = np.mean(krcs)
            top_krc = max(krcs)
            median_krc = np.median(krcs)
            
            figure.add_annotation(
                x=len(display_names) * 0.85,
                y=max(krcs) * 0.8,
                text=f"📊 Analytics<br>" +
                     f"🏆 Top Score: {top_krc}<br>" +
                     f"📈 Average: {avg_krc:.1f}<br>" +
                     f"📊 Median: {median_krc:.1f}<br>" +
                     f"👥 Total Faculty: {len(krcs)}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#f39c12",
                ax=60,
                ay=-60,
                bgcolor="rgba(255,255,255,0.95)",
                bordercolor="#f39c12",
                borderwidth=2,
                borderpad=12,
                font=dict(size=11, color="#2c3e50", family="Arial Bold")
            )
        
        # Add performance zones
        if krcs:
            max_krc = max(krcs)
            # Excellence zone (top 25%)
            # figure.add_hrect(
            #     y0=max_krc * 0.75, y1=max_krc,
            #     fillcolor="rgba(39, 174, 96, 0.1)",
            #     layer="below",
            #     annotation_text="Excellence Zone",
            #     annotation_position="top right",
            #     annotation_font_color="#27ae60"
            # )
            
            # # High Performance zone (50-75%)
            # figure.add_hrect(
            #     y0=max_krc * 0.5, y1=max_krc * 0.75,
            #     fillcolor="rgba(243, 156, 18, 0.1)",
            #     layer="below",
            #     annotation_text="High Performance",
            #     annotation_position="top right",
            #     annotation_font_color="#f39c12"
            # )

    return html.Div(
        id="widget2",
        className="widget",
        children=[
            # Enhanced header with stats
            html.Div([
                html.H3(
                    "⭐ Faculty Excellence Dashboard", 
                    style={
                        "color": "#2c3e50", 
                        "marginBottom": "5px",
                        "fontSize": "26px",
                        "fontWeight": "bold",
                        "fontFamily": "Arial Black"
                    }
                ),
                html.P(
                    "Ranking faculty members by Keyword-Relevant Citations (KRC) - A measure of research impact and relevance",
                    style={
                        "color": "#7f8c8d",
                        "marginBottom": "20px",
                        "fontSize": "14px",
                        "fontStyle": "italic",
                        "lineHeight": "1.4"
                    }
                ),
                
                # Stats cards for KRC data
                html.Div([
                    html.Div([
                        html.H4("🏆", style={"margin": "0 0 5px 0", "fontSize": "20px"}),
                        html.H4(names[0] if names else "N/A", style={"margin": "0", "color": "#f39c12", "fontSize": "14px", "fontWeight": "bold"}),
                        html.P("Top Performer", style={"margin": "0", "color": "#7f8c8d", "fontSize": "11px"})
                    ], style={
                        "textAlign": "center",
                        "padding": "15px 10px",
                        "backgroundColor": "rgba(243, 156, 18, 0.1)",
                        "borderRadius": "10px",
                        "marginRight": "10px",
                        "minWidth": "120px",
                        "border": "2px solid rgba(243, 156, 18, 0.3)"
                    }),
                    html.Div([
                        html.H4(f"{max(krcs):.1f}" if krcs else "0", style={"margin": "0", "color": "#e74c3c", "fontSize": "20px"}),
                        html.P("Highest KRC", style={"margin": "0", "color": "#7f8c8d", "fontSize": "11px"})
                    ], style={
                        "textAlign": "center",
                        "padding": "15px 10px",
                        "backgroundColor": "rgba(231, 76, 60, 0.1)",
                        "borderRadius": "10px",
                        "marginRight": "10px",
                        "minWidth": "100px",
                        "border": "2px solid rgba(231, 76, 60, 0.3)"
                    }),
                    html.Div([
                        html.H4(f"{np.mean(krcs):.1f}" if krcs else "0", style={"margin": "0", "color": "#3498db", "fontSize": "20px"}),
                        html.P("Average KRC", style={"margin": "0", "color": "#7f8c8d", "fontSize": "11px"})
                    ], style={
                        "textAlign": "center",
                        "padding": "15px 10px",
                        "backgroundColor": "rgba(52, 152, 219, 0.1)",
                        "borderRadius": "10px",
                        "marginRight": "10px",
                        "minWidth": "100px",
                        "border": "2px solid rgba(52, 152, 219, 0.3)"
                    }),
                    html.Div([
                        html.H4(str(len(names)), style={"margin": "0", "color": "#27ae60", "fontSize": "20px"}),
                        html.P("Total Faculty", style={"margin": "0", "color": "#7f8c8d", "fontSize": "11px"})
                    ], style={
                        "textAlign": "center",
                        "padding": "15px 10px",
                        "backgroundColor": "rgba(39, 174, 96, 0.1)",
                        "borderRadius": "10px",
                        "minWidth": "100px",
                        "border": "2px solid rgba(39, 174, 96, 0.3)"
                    })
                ], style={
                    "display": "flex",
                    "marginBottom": "25px",
                    "flexWrap": "wrap",
                    "gap": "10px"
                }) if names else html.Div()
            ]),
            
            # Enhanced chart container
            html.Div([
                dcc.Graph(
                    id="krc-bar",
                    figure=figure,
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'faculty_krc_rankings',
                            'height': 600,
                            'width': 1200,
                            'scale': 2
                        }
                    }
                )
            ], style={
                "backgroundColor": "rgba(0,0,0,0)",
                "borderRadius": "12px",
                "padding": "15px",
                "border": "1px solid rgba(0,0,0,0.05)"
            }),
            
            # Add legend explanation
            html.Div([
                html.P("📋 Legend:", style={"fontWeight": "bold", "marginBottom": "10px", "color": "#2c3e50"}),
                html.Div([
                    html.Span("🥇", style={"marginRight": "5px"}),
                    html.Span("Gold: #1 Rank", style={"marginRight": "20px", "fontSize": "12px"}),
                    html.Span("🥈", style={"marginRight": "5px"}),
                    html.Span("Silver: #2 Rank", style={"marginRight": "20px", "fontSize": "12px"}),
                    html.Span("🥉", style={"marginRight": "5px"}),
                    html.Span("Bronze: #3 Rank", style={"fontSize": "12px"})
                ], style={"color": "#7f8c8d"})
            ], style={
                "marginTop": "15px",
                "padding": "15px",
                "backgroundColor": "rgba(236, 240, 241, 0.5)",
                "borderRadius": "8px",
                "border": "1px solid rgba(189, 195, 199, 0.3)"
            }) if names else html.Div()
        ],
        style={
            "padding": "25px",
            "border": "none",
            "borderRadius": "15px",
            "backgroundColor": "#ffffff",
            "boxShadow": "0 10px 30px rgba(0,0,0,0.1)",
            "margin": "10px",
            "fontFamily": "Arial, sans-serif"
        }
    )

def register_callbacks(app):
    pass