from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
from neo4j_utils import Neo4jUtils
import math
import numpy as np

PREFIX = "widget3"

def layout():
    return html.Div(
        id=PREFIX,
        className="widget",
        children=[
            html.H3("🔍 Research Focus Graph", 
                   style={"color": "#2c3e50", "marginBottom": "20px", "fontWeight": "bold"}),
            
            html.P("Explore faculty research networks and publication connections", 
                  style={"color": "#7f8c8d", "marginBottom": "15px", "fontSize": "14px"}),
            
            html.Div([
                dcc.Input(
                    id=f"{PREFIX}-input", 
                    type="text", 
                    placeholder="Enter Faculty Name (e.g., Jiawei Han)",
                    style={
                        'width': '65%', 
                        'marginRight': '10px',
                        'padding': '10px',
                        'border': '2px solid #3498db',
                        'borderRadius': '25px',
                        'fontSize': '14px',
                        'outline': 'none',
                        'boxShadow': '0 2px 5px rgba(52, 152, 219, 0.2)'
                    }
                ),
                html.Button("🔍 Search", 
                           id=f"{PREFIX}-btn", 
                           style={
                               'width': '30%',
                               'padding': '10px 20px',
                               'backgroundColor': "#ffffff",
                               'color': 'white',
                               'border': 'none',
                               'borderRadius': '25px',
                               'fontSize': '14px',
                               'fontWeight': 'bold',
                               'cursor': 'pointer',
                               'boxShadow': '0 4px 8px rgba(52, 152, 219, 0.3)',
                               'transition': 'all 0.3s ease'
                           })
            ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),
            
            # Enhanced status div
            html.Div(id=f"{PREFIX}-status", style={
                'padding': '15px', 
                'backgroundColor': "#ffffff", 
                'marginBottom': '15px',
                'borderRadius': '10px',
                'border': 'none',
                'fontSize': '14px',
                'fontWeight': '500',
                'color': '#2c3e50',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }),
            
            dcc.Graph(
                id=f"{PREFIX}-graph", 
                config={
                    "displayModeBar": False,
                    "scrollZoom": True,
                    "doubleClick": "reset"
                },
                style={'height': '700px', 'borderRadius': '10px', 'overflow': 'hidden'}
            )
        ],
        style={
            "padding": "25px",
            "border": "none",
            "borderRadius": "15px",
            "backgroundColor": "#ffffff",
            "boxShadow": "0 8px 25px rgba(0,0,0,0.1)",
            "margin": "10px"
        }
    )

def _placeholder(message, message_type="info"):
    """Create a beautiful placeholder figure with a message"""
    colors = {
        "info": "#3498db",
        "error": "#e74c3c", 
        "warning": "#f39c12",
        "success": "#27ae60"
    }
    
    bg_colors = {
        "info": "rgba(52, 152, 219, 0.1)",
        "error": "rgba(231, 76, 60, 0.1)", 
        "warning": "rgba(243, 156, 18, 0.1)",
        "success": "rgba(39, 174, 96, 0.1)"
    }
    
    fig = go.Figure()
    
    # Add a subtle background circle
    fig.add_shape(
        type="circle",
        x0=-0.5, y0=-0.5, x1=0.5, y1=0.5,
        fillcolor=bg_colors.get(message_type, bg_colors["info"]),
        line=dict(color=colors.get(message_type, colors["info"]), width=2),
        opacity=0.3
    )
    
    fig.update_layout(
        annotations=[{
            "text": message,
            "xref": "paper",
            "yref": "paper",
            "x": 0.5,
            "y": 0.5,
            "showarrow": False,
            "font": {
                "size": 18, 
                "color": colors.get(message_type, colors["info"]),
                "family": "Arial, sans-serif"
            },
            "align": "center"
        }],
        xaxis={"visible": False, "range": [-1, 1]},
        yaxis={"visible": False, "range": [-1, 1]},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"l": 40, "r": 40, "t": 40, "b": 40}
    )
    return fig

def _create_research_graph(faculty_name, publications, db):
    """Create a beautiful research focus visualization"""
    if not publications:
        return _placeholder(f"No publications found for {faculty_name}", "warning")
    
    fig = go.Figure()
    
    # Enhanced color palette
    colors = {
        'faculty': "#e1e73c",          # Yellow
        'publication': '#3498db',       # Blue  
        'keyword': '#27ae60',          # Green
        'edge_pub': 'rgba(52, 152, 219, 0.6)',    # Blue edges
        'edge_kw': 'rgba(39, 174, 96, 0.4)'       # Green edges
    }
    
    # Calculate positions for publications in a more organic layout
    pub_positions = {}
    n_pubs = len(publications)
    
    if n_pubs == 1:
        # Single publication - place to the right
        pub_positions[publications[0]["id"]] = {
            "x": 2, "y": 0, 
            "title": publications[0]["title"], 
            "cites": publications[0].get("cites", 0)
        }
    else:
        # Multiple publications - use golden spiral for better distribution
        for i, pub in enumerate(publications):
            pub_id = pub["id"]
            title = pub["title"]
            cites = pub.get("cites", 0)
            
            # Golden spiral positioning
            golden_angle = math.pi * (3 - math.sqrt(5))  # Golden angle
            radius = 1.5 + 0.3 * math.sqrt(i)  # Spiral outward
            theta = i * golden_angle
            
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            
            pub_positions[pub_id] = {
                "x": x, "y": y, "title": title, "cites": cites
            }
    
    # Draw elegant connections from faculty to publications
    for pub_id, pos in pub_positions.items():
        # Calculate line width based on citations (more prominent for highly cited papers)
        line_width = max(2, min(6, pos["cites"] / 50))
        
        fig.add_trace(go.Scatter(
            x=[0, pos["x"]], y=[0, pos["y"]], 
            mode="lines",
            line={
                "width": line_width, 
                "color": colors['edge_pub'],
                "dash": "solid"
            },
            hoverinfo="none",
            showlegend=False
        ))
    
    # Add beautiful publication nodes with size based on citations
    pub_x = [pos["x"] for pos in pub_positions.values()]
    pub_y = [pos["y"] for pos in pub_positions.values()]
    pub_sizes = [max(20, min(40, pos["cites"] / 30)) for pos in pub_positions.values()]
    pub_text = [f"{pos['title'][:40]}..." if len(pos['title']) > 40 else pos['title'] 
                for pos in pub_positions.values()]
    pub_hover = [f"<b>{pos['title']}</b><br>📊 Citations: {pos['cites']}<br>🔗 Click to explore" 
                 for pos in pub_positions.values()]
    
    fig.add_trace(go.Scatter(
        x=pub_x, y=pub_y,
        mode="markers+text",
        marker={
            "size": pub_sizes,
            "color": colors['publication'],
            "line": {"width": 3, "color": "white"},
            "opacity": 0.8,
            "symbol": "circle"
        },
        text=pub_text,
        textposition="top center",
        textfont={"size": 10, "color": "#2c3e50", "family": "Arial"},
        hovertext=pub_hover,
        hoverinfo="text",
        name="Publications",
        showlegend=False
    ))
    
    # Add keywords with improved positioning and styling
    keyword_x, keyword_y, keyword_text, keyword_hover, keyword_sizes = [], [], [], [], []
    
    for pub_id, pub_pos in pub_positions.items():
        keywords = db.get_keywords_for_publication(pub_id)
        if not keywords:
            continue
            
        # Position keywords in a more natural cluster around publication
        n_keywords = len(keywords)
        if n_keywords == 1:
            # Single keyword - place below publication
            kw_positions = [(0, -0.6)]
        else:
            # Multiple keywords - arrange in a semi-circle
            kw_positions = []
            for j in range(n_keywords):
                angle = math.pi * (j / (n_keywords - 1)) - math.pi/2  # Semi-circle from bottom
                radius = 0.5 + 0.1 * (j % 2)  # Slight radius variation
                kw_x = radius * math.cos(angle)
                kw_y = radius * math.sin(angle) - 0.3  # Offset downward
                kw_positions.append((kw_x, kw_y))
        
        for j, kw in enumerate(keywords):
            kw_name = kw.get("kw", "Unknown")
            kw_score = kw.get("score", 0)
            
            if j < len(kw_positions):
                offset_x, offset_y = kw_positions[j]
                kw_x = pub_pos["x"] + offset_x
                kw_y = pub_pos["y"] + offset_y
                
                keyword_x.append(kw_x)
                keyword_y.append(kw_y)
                keyword_text.append(kw_name[:12])
                keyword_hover.append(f"<b>{kw_name}</b><br>⭐ Score: {kw_score:.2f}")
                keyword_sizes.append(max(12, min(18, kw_score * 20)))
                
                # Draw curved connection from publication to keyword
                fig.add_trace(go.Scatter(
                    x=[pub_pos["x"], kw_x], y=[pub_pos["y"], kw_y],
                    mode="lines",
                    line={
                        "width": 2, 
                        "color": colors['edge_kw'],
                        "dash": "dot"
                    },
                    hoverinfo="none",
                    showlegend=False
                ))
    
    # Add beautiful keyword nodes
    if keyword_x:
        fig.add_trace(go.Scatter(
            x=keyword_x, y=keyword_y,
            mode="markers+text",
            marker={
                "size": keyword_sizes,
                "color": colors['keyword'],
                "line": {"width": 2, "color": "white"},
                "opacity": 0.7,
                "symbol": "diamond"
            },
            text=keyword_text,
            textposition="middle center",
            textfont={"size": 9, "color": "gray", "family": "Arial Black"},
            hovertext=keyword_hover,
            hoverinfo="text",
            name="Keywords",
            showlegend=False
        ))
    
    # Add the central faculty node with enhanced styling
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode="markers+text",
        marker={
            "size": 50,
            "color": colors['faculty'],
            "line": {"width": 4, "color": "white"},
            "opacity": 0.9,
            "symbol": "star"
        },
        text=[faculty_name.split()[-1]],  # Show last name only for cleaner look
        textposition="bottom center",
        textfont={"size": 16, "color": "#2c3e50", "family": "Arial Black"},
        hovertext=f"<b>👨‍🎓 {faculty_name}</b><br>🏫 Faculty Member<br>📚 {len(publications)} Publications",
        hoverinfo="text",
        name="Faculty",
        showlegend=False
    ))
    
    # Create a beautiful layout with improved styling
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis={
            "visible": False, 
            "range": [-4, 4],
            "scaleanchor": "y",
            "scaleratio": 1
        },
        yaxis={
            "visible": False, 
            "range": [-4, 4]
        },
        margin={"l": 40, "r": 40, "t": 60, "b": 40},
        title={
            "text": f"🔬 Research Network: {faculty_name}",
            "x": 0.5,
            "font": {
                "size": 20,
                "color": "#2c3e50",
                "family": "Arial Black"
            }
        },
        hoverlabel={
            "bgcolor": "white",
            "bordercolor": "#3498db",
            "font": {"size": 12, "color": "#2c3e50"}
        },
        # Add subtle animations
        transition={
            'duration': 500,
            'easing': 'cubic-in-out'
        }
    )
    
    # Add a subtle grid pattern in the background
    fig.add_shape(
        type="circle",
        x0=-3.5, y0=-3.5, x1=3.5, y1=3.5,
        line=dict(color="rgba(52, 152, 219, 0.1)", width=1, dash="dot"),
        fillcolor="rgba(0,0,0,0)"
    )
    
    fig.add_shape(
        type="circle",
        x0=-3.5, y0=-3.5, x1=3.5, y1=3.5,
        line=dict(
            color="rgba(52, 152, 219, 0.6)",   # More saturated, less transparent
            width=3,                           # Thicker line
            dash="dot"
        ),
        fillcolor="rgba(0,0,0,0)"
    )

    
    return fig

def register_callbacks(app):
    @app.callback(
        [Output(f"{PREFIX}-graph", "figure"),
         Output(f"{PREFIX}-status", "children")],
        Input(f"{PREFIX}-btn", "n_clicks"),
        State(f"{PREFIX}-input", "value")
    )
    def update_graph(n_clicks, faculty_name):
        # Initial state with better messaging
        if not n_clicks or not faculty_name:
            return (_placeholder("🎯 Enter a faculty name and click Search to explore their research network!", "info"), 
                   "🚀 Ready to explore research networks...")
        
        faculty_name = faculty_name.strip()
        if not faculty_name:
            return (_placeholder("⚠️ Please enter a valid faculty name to continue.", "warning"),
                   "❓ Please enter a faculty name to search.")
        
        # Initialize database connection
        db = Neo4jUtils()
        status_message = f"🔍 Searching for {faculty_name}..."
        
        try:
            # Test connection first
            if not db.test_connection():
                return (_placeholder("❌ Database connection failed.\nPlease check if Neo4j server is running.", "error"),
                       "🔌 Database connection failed - Check Neo4j server")
            
            # Get publications
            publications = db.get_top_publications(faculty_name)
            
            if not publications:
                # Enhanced suggestion system
                sample_names = db.get_sample_faculty_names(10)
                if sample_names:
                    suggestions = [name for name in sample_names 
                                 if faculty_name.lower() in name.lower()][:3]
                    if suggestions:
                        suggestion_text = f"💡 Did you mean: {', '.join(suggestions)}?"
                    else:
                        suggestion_text = f"💭 Try searching for: {', '.join(sample_names[:5])}"
                else:
                    suggestion_text = "📊 No faculty data found in database."
                
                return (_placeholder(f"🔍 No publications found for '{faculty_name}'\n\n{suggestion_text}", "warning"),
                       f"❌ No results found for '{faculty_name}'")
            
            # Create the beautiful visualization
            fig = _create_research_graph(faculty_name, publications, db)
            status_message = f"✅ Successfully loaded {len(publications)} publications for {faculty_name} with their research keywords!"
            
            return fig, status_message
            
        except Exception as e:
            error_msg = f"⚠️ Error: {str(e)}"
            print(f"Widget3 error: {error_msg}")  # For debugging
            return (_placeholder(f"🚨 An unexpected error occurred:\n{error_msg}", "error"),
                   f"❌ System Error: {str(e)}")
        
        finally:
            db.close()