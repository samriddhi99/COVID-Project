"""
 Unemployment Multi-Page Dashboard
Requirements: dash, plotly, pandas, dash-bootstrap-components
Install: pip install dash plotly pandas dash-bootstrap-components
"""

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import os

# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

# Custom CSS for professional styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title> Unemployment Analytics Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
            }
            .navbar {
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .card {
                border: none;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .card:hover {
                transform: translateY(-5px);
            }
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .page-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px 0;
                margin-bottom: 30px;
                border-radius: 0 0 20px 20px;
            }
            .nav-pills .nav-link {
                border-radius: 50px;
                margin-right: 10px;
            }
            .nav-pills .nav-link.active {
                background-color: #667eea;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Load and prepare data
def load_data():
    """Load the  unemployment data from CSV"""
    # Try multiple possible filenames
    possible_files = ['/Users/yssf/Desktop/COVID PROJECT/unemployment_monthly.csv'
    ]
    
    for filename in possible_files:
        if os.path.exists(filename):
            print(f"Loading data from: {filename}")
            try:
                df = pd.read_csv(filename)
                print(f"Columns found: {df.columns.tolist()}")
                
                # Clean column names - remove leading/trailing whitespace
                df.columns = df.columns.str.strip()
                
                # Identify the correct columns based on what's available
                time_col = None
                value_col = None
                geo_col = None
                
                for col in df.columns:
                    col_lower = col.lower()
                    if 'time' in col_lower or 'period' in col_lower or 'date' in col_lower:
                        time_col = col
                    if 'obs_value' in col_lower or 'value' in col_lower or 'rate' in col_lower:
                        value_col = col
                    if 'geo' in col_lower or 'country' in col_lower or 'location' in col_lower:
                        geo_col = col
                
                # Use the identified columns or fall back to defaults
                if time_col is None:
                    time_col = 'TIME_PERIOD'
                if value_col is None:
                    value_col = 'OBS_VALUE'
                if geo_col is None:
                    geo_col = 'geo'
                
                print(f"Using columns - Time: {time_col}, Value: {value_col}, Geo: {geo_col}")
                
                # Rename to standardized names
                df = df.rename(columns={
                    time_col: 'TIME_PERIOD',
                    value_col: 'OBS_VALUE',
                    geo_col: 'geo'
                })
                
                # Parse date - handle various formats
                try:
                    df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'])
                except:
                    # Try parsing as period string (e.g., "2025-M10")
                    try:
                        df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'].str.replace('-M', '-'))
                    except:
                        print("Warning: Could not parse dates properly")
                        df['TIME_PERIOD'] = pd.to_datetime('2020-01-01')
                
                # Convert OBS_VALUE to numeric, handling any non-numeric values
                df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
                
                # Remove rows with missing values
                df = df.dropna(subset=['TIME_PERIOD', 'OBS_VALUE', 'geo'])
                
                print(f"Loaded {len(df)} records for {df['geo'].nunique()} countries")
                print(f"Date range: {df['TIME_PERIOD'].min()} to {df['TIME_PERIOD'].max()}")
                
                return df
                
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                continue
    
    # If no file found, create sample data
    print("Warning: CSV file not found. Creating sample data for demonstration.")
    dates = pd.date_range('2020-01', '2025-10', freq='MS')
    countries = ['USA', 'UK', 'Germany', 'France', 'Spain', 'Italy', 'Canada', 'Japan']
    data = []
    
    import random
    random.seed(42)
    
    for country in countries:
        base_rate = random.uniform(10, 25)
        for i, date in enumerate(dates):
            # Add some variation and trend
            variation = random.uniform(-2, 2)
            trend = (i - len(dates)/2) * 0.05
            rate = max(5, min(35, base_rate + variation + trend))
            data.append({
                'geo': country,
                'TIME_PERIOD': date,
                'OBS_VALUE': round(rate, 1)
            })
    
    df = pd.DataFrame(data)
    print(f"Created sample data: {len(df)} records for {df['geo'].nunique()} countries")
    return df

df = load_data()

# Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Overview", href="/", className="nav-link")),
        dbc.NavItem(dcc.Link("Comparative", href="/comparative", className="nav-link")),
        dbc.NavItem(dcc.Link("Geographic", href="/geographic", className="nav-link")),
    ],
    brand="Unemployment Analytics",
    brand_href="/",
    color="dark",
    dark=True,
    className="mb-4",
    sticky="top"
)

# Page layouts
def create_overview_page():
    """Overview page with key metrics and summary visualizations"""
    
    # Calculate key metrics
    latest_date = df['TIME_PERIOD'].max()
    latest_data = df[df['TIME_PERIOD'] == latest_date]
    avg_unemployment = latest_data['OBS_VALUE'].mean()
    max_unemployment = latest_data['OBS_VALUE'].max()
    min_unemployment = latest_data['OBS_VALUE'].min()
    
    # Year-over-year change
    year_ago = latest_date - pd.DateOffset(years=1)
    yoy_data = df[df['TIME_PERIOD'] == year_ago]
    if len(yoy_data) > 0:
        yoy_change = avg_unemployment - yoy_data['OBS_VALUE'].mean()
    else:
        yoy_change = 0
    
    return dbc.Container([
        # Page Header
        html.Div([
            html.H1(" Unemployment Dashboard", className="text-center mb-2"),
            html.P("Comprehensive analysis of  labour market dynamics",
                   className="text-center lead mb-0"),
            html.P(f"Last Updated: {latest_date.strftime('%B %Y')}", 
                   className="text-center", style={'opacity': '0.8'})
        ], className="page-header"),
        
        # Key Metrics
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H6("Average Rate", className="mb-2"),
                    html.H2(f"{avg_unemployment:.1f}%", className="mb-2"),
                    html.P(f"{'↑' if yoy_change > 0 else '↓'} {abs(yoy_change):.1f}% YoY",
                          className="mb-0")
                ], className="metric-card")
            ], md=4),
            dbc.Col([
                html.Div([
                    html.H6("Highest Rate", className="mb-2"),
                    html.H2(f"{max_unemployment:.1f}%", className="mb-2"),
                    html.P(f"{latest_data.loc[latest_data['OBS_VALUE'].idxmax(), 'geo']}", 
                          className="mb-0")
                ], className="metric-card")
            ], md=4),
            dbc.Col([
                html.Div([
                    html.H6("Lowest Rate", className="mb-2"),
                    html.H2(f"{min_unemployment:.1f}%", className="mb-2"),
                    html.P(f"{latest_data.loc[latest_data['OBS_VALUE'].idxmin(), 'geo']}", 
                          className="mb-0")
                ], className="metric-card")
            ], md=4),
        ], className="mb-4"),
        
        # Main visualizations
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Current Unemployment Rates by Country", 
                                          className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_bar_chart(latest_data),
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Distribution of Unemployment Rates", 
                                          className="mb-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_histogram(df),
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="mb-4")
            ], md=6),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Overall Trend (Average & Range)", className="mb-0")),
                    dbc.CardBody([
                        html.P("Track the average unemployment rate and its range across all countries over time.", 
                               className="text-muted mb-3"),
                        dcc.Graph(
                            figure=create_overview_trends(df),
                            config={'displayModeBar': True}
                        )
                    ])
                ])
            ])
        ])
    ], fluid=True)


      

def create_comparative_page():
    """Comparative analysis page"""
    years = sorted(df['TIME_PERIOD'].dt.year.unique(), reverse=True)
    
    return dbc.Container([
        html.Div([
            html.H1("Comparative Analysis", className="text-center mb-2"),
            html.P("Compare unemployment rates across countries and time periods", 
                   className="text-center lead mb-0")
        ], className="page-header"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Label("Select Years to Compare:", className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id='year-dropdown',
                            options=[{'label': str(y), 'value': y} for y in years],
                            value=[years[0], years[1]] if len(years) > 1 else [years[0]],
                            multi=True,
                            placeholder="Select years..."
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Average Unemployment by Country", className="mb-0")),
                    dbc.CardBody([
                        html.P("Compare average rates across selected years to identify improvements or deteriorations.", 
                               className="text-muted mb-3"),
                        dcc.Graph(id='comparison-bar', config={'displayModeBar': False})
                    ])
                ])
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Distribution Analysis (Box Plot)", className="mb-0")),
                    dbc.CardBody([
                        html.P("Visualize the spread, median, and outliers in unemployment data.", 
                               className="text-muted mb-3"),
                        dcc.Graph(id='comparison-box', config={'displayModeBar': False})
                    ])
                ])
            ], md=6)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Temporal Heatmap: Country vs Time", className="mb-0")),
                    dbc.CardBody([
                        html.P("Identify patterns and trends across all countries and time periods at a glance.", 
                               className="text-muted mb-3"),
                        dcc.Graph(id='heatmap-chart', config={'displayModeBar': True})
                    ])
                ])
            ])
        ])
    ], fluid=True)

def create_geographic_page():
    """Geographic analysis page"""
    dates = sorted(df['TIME_PERIOD'].unique())
    
    return dbc.Container([
        html.Div([
            html.H1("Geographic Analysis", className="text-center mb-2"),
            html.P("Spatial patterns in youth unemployment", 
                   className="text-center lead mb-0")
        ], className="page-header"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Label("Select Time Period:", className="fw-bold mb-2"),
                        dcc.Slider(
                            id='date-slider',
                            min=0,
                            max=len(dates) - 1,
                            value=len(dates) - 1,
                            marks={i: dates[i].strftime('%Y-%m') if i % (len(dates)//10 + 1) == 0 else '' 
                                   for i in range(len(dates))},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Div(id='slider-output', className="text-center mt-2")
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Unemployment Rates by Country", className="mb-0")),
                    dbc.CardBody([
                        html.P("Explore geographic distribution of youth unemployment at a specific point in time.", 
                               className="text-muted mb-3"),
                        dcc.Graph(id='geo-chart', config={'displayModeBar': True})
                    ])
                ])
            ], md=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Rankings", className="mb-0")),
                    dbc.CardBody([
                        html.Div(id='geo-stats')
                    ])
                ])
            ], md=4)
        ])
    ], fluid=True)

# Visualization functions
def create_bar_chart(data):
    """Create bar chart for current rates"""
    data_sorted = data.sort_values('OBS_VALUE', ascending=False)
    fig = px.bar(data_sorted, 
                 x='geo', y='OBS_VALUE',
                 color='OBS_VALUE',
                 color_continuous_scale='RdYlGn_r',
                 labels={'OBS_VALUE': 'Unemployment Rate (%)', 'geo': 'Country'})
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=30, b=50),
        xaxis_title="Country",
        yaxis_title="Unemployment Rate (%)"
    )
    return fig

def create_histogram(data):
    """Create histogram of unemployment distribution"""
    fig = px.histogram(data, x='OBS_VALUE', nbins=30,
                      labels={'OBS_VALUE': 'Unemployment Rate (%)', 'count': 'Frequency'})
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=30, b=50),
        xaxis_title="Unemployment Rate (%)",
        yaxis_title="Frequency"
    )
    fig.update_traces(marker_color='#667eea')
    return fig

def create_overview_trends(data):
    """Create aggregated trend line chart"""
    # Calculate regional/overall averages
    monthly_avg = data.groupby('TIME_PERIOD')['OBS_VALUE'].agg(['mean', 'min', 'max']).reset_index()
    
    fig = go.Figure()
    
    # Add average line
    fig.add_trace(go.Scatter(
        x=monthly_avg['TIME_PERIOD'],
        y=monthly_avg['mean'],
        mode='lines',
        name='Average',
        line=dict(color='#667eea', width=3),
        fill=None
    ))
    
    # Add range band
    fig.add_trace(go.Scatter(
        x=monthly_avg['TIME_PERIOD'],
        y=monthly_avg['max'],
        mode='lines',
        name='Max',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=monthly_avg['TIME_PERIOD'],
        y=monthly_avg['min'],
        mode='lines',
        name='Range',
        line=dict(width=0),
        fillcolor='rgba(102, 126, 234, 0.2)',
        fill='tonexty',
        showlegend=True
    ))
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=30, b=50),
        hovermode='x unified',
        xaxis_title="Date",
        yaxis_title="Unemployment Rate (%)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    return fig

def create_top_countries_trend(data):
    """Create trend chart for top 5 countries by recent unemployment"""
    latest_date = data['TIME_PERIOD'].max()
    latest_data = data[data['TIME_PERIOD'] == latest_date]
    top_countries = latest_data.nlargest(5, 'OBS_VALUE')['geo'].tolist()
    
    filtered = data[data['geo'].isin(top_countries)]
    
    fig = px.line(filtered, x='TIME_PERIOD', y='OBS_VALUE', color='geo',
                  labels={'OBS_VALUE': 'Unemployment Rate (%)', 'TIME_PERIOD': 'Date', 'geo': 'Country'})
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=30, b=50),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    return fig



@callback(
    [Output('comparison-bar', 'figure'),
     Output('comparison-box', 'figure'),
     Output('heatmap-chart', 'figure')],
    Input('year-dropdown', 'value')
)
def update_comparison(selected_years):
    if not selected_years:
        selected_years = [df['TIME_PERIOD'].dt.year.max()]
    
    filtered = df[df['TIME_PERIOD'].dt.year.isin(selected_years)].copy()
    
    # Grouped bar
    filtered['Year'] = filtered['TIME_PERIOD'].dt.year
    avg_by_year = filtered.groupby(['geo', 'Year'])['OBS_VALUE'].mean().reset_index()
    fig1 = px.bar(avg_by_year, x='geo', y='OBS_VALUE', color='Year',
                  barmode='group',
                  labels={'OBS_VALUE': 'Avg Unemployment (%)', 'geo': 'Country'},
                  color_continuous_scale='Viridis')
    fig1.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="Country",
        yaxis_title="Average Unemployment Rate (%)"
    )
    
    # Box plot
    filtered['Year_str'] = filtered['Year'].astype(str)
    fig2 = px.box(filtered, x='geo', y='OBS_VALUE', color='Year_str',
                  labels={'OBS_VALUE': 'Unemployment Rate (%)', 'geo': 'Country', 'Year_str': 'Year'})
    fig2.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="Country",
        yaxis_title="Unemployment Rate (%)"
    )
    
    # Heatmap
    pivot = df.pivot_table(
        values='OBS_VALUE', 
        index='geo',
        columns=df['TIME_PERIOD'].dt.to_period('M'),
        aggfunc='mean'
    )
    
    # Limit columns for better visualization
    if len(pivot.columns) > 60:
        pivot = pivot.iloc[:, -60:]
    
    fig3 = px.imshow(
        pivot,
        aspect='auto',
        color_continuous_scale='RdYlGn_r',
        labels={'color': 'Unemployment Rate (%)'},
        x=[str(col) for col in pivot.columns],
        y=pivot.index
    )
    fig3.update_layout(
        xaxis_title="Time Period",
        yaxis_title="Country",
        xaxis={'side': 'bottom'}
    )
    
    return fig1, fig2, fig3

@callback(
    [Output('geo-chart', 'figure'),
     Output('geo-stats', 'children'),
     Output('slider-output', 'children')],
    Input('date-slider', 'value')
)
def update_geographic(slider_value):
    dates = sorted(df['TIME_PERIOD'].unique())
    selected_date = dates[slider_value]
    filtered = df[df['TIME_PERIOD'] == selected_date].sort_values('OBS_VALUE', ascending=False)
    
    # Create horizontal bar chart (easier to read country names)
    fig = px.bar(filtered, 
                 y='geo', 
                 x='OBS_VALUE',
                 orientation='h',
                 color='OBS_VALUE',
                 color_continuous_scale='RdYlGn_r',
                 labels={'OBS_VALUE': 'Unemployment Rate (%)', 'geo': 'Country'})
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=max(400, len(filtered) * 25),
        yaxis_title="",
        xaxis_title="Unemployment Rate (%)",
        showlegend=False
    )
    
    # Stats
    top5 = filtered.head(5)
    bottom5 = filtered.tail(5)
    
    stats = html.Div([
        html.H6("Highest Rates:", className="fw-bold text-danger mt-3 mb-3"),
        html.Div([
            html.Div([
                html.Span(f"{i+1}. ", className="fw-bold"),
                html.Span(f"{row['geo']}: "),
                html.Span(f"{row['OBS_VALUE']:.1f}%", className="text-danger fw-bold")
            ], className="mb-2") for i, (_, row) in enumerate(top5.iterrows())
        ]),
        
        html.Hr(),
        
        html.H6("Lowest Rates:", className="fw-bold text-success mt-3 mb-3"),
        html.Div([
            html.Div([
                html.Span(f"{i+1}. ", className="fw-bold"),
                html.Span(f"{row['geo']}: "),
                html.Span(f"{row['OBS_VALUE']:.1f}%", className="text-success fw-bold")
            ], className="mb-2") for i, (_, row) in enumerate(bottom5.iterrows())
        ])
    ])
    
    date_text = html.H5(f"📅 {selected_date.strftime('%B %Y')}", 
                       className="fw-bold text-primary")
    
    return fig, stats, date_text

# Main layout with routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/timeseries':
        return create_timeseries_page()
    elif pathname == '/comparative':
        return create_comparative_page()
    elif pathname == '/geographic':
        return create_geographic_page()
    else:
        return create_overview_page()

if __name__ == '__main__':
    print("\n" + "="*60)
    print(" Unemployment Dashboard")
    print("="*60)
    print(f"Dashboard is running at: http://127.0.0.1:8020")
    print("Press Ctrl+C to quit")
    print("="*60 + "\n")
    app.run(debug=True, port=8020)