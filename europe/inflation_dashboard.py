import dash
from dash import dcc, html, callback, Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# Read the CSV file with proper settings
df = pd.read_csv('dataset europe/prc_hicp_manr_linear.csv', low_memory=False)


df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')


df = df.dropna(subset=['OBS_VALUE', 'TIME_PERIOD'])


df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'])
df['Year'] = df['TIME_PERIOD'].dt.year
df['Month'] = df['TIME_PERIOD'].dt.month
df['Month_Name'] = df['TIME_PERIOD'].dt.strftime('%B')


countries = sorted(df['geo'].unique())

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)


colors = {
    'background': '#f8f9fa',
    'card': '#ffffff',
    'primary': '#2c3e50',
    'secondary': '#3498db',
    'accent': '#e74c3c',
    'success': '#27ae60',
    'text': '#2c3e50',
    'border': '#dee2e6'
}

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
                margin: 0;
                padding: 0;
            }
            .navbar {
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                padding: 1.5rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .nav-link {
                color: white !important;
                font-weight: 500;
                margin: 0 1rem;
                transition: all 0.3s;
                border-bottom: 2px solid transparent;
            }
            .nav-link:hover, .nav-link.active {
                border-bottom: 2px solid white;
            }
            .card {
                border: none;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                margin-bottom: 2rem;
                transition: transform 0.3s;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            }
            .metric-card {
                background: white;
                padding: 2rem;
                border-radius: 12px;
                text-align: center;
                height: 100%;
            }
            .metric-value {
                font-size: 2.5rem;
                font-weight: bold;
                color: #2c3e50;
                margin: 0.5rem 0;
            }
            .metric-label {
                color: #7f8c8d;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .page-header {
                background: white;
                padding: 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            .page-title {
                color: #2c3e50;
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }
            .page-subtitle {
                color: #7f8c8d;
                font-size: 1.1rem;
            }
            .insight-box {
                background: #e8f4f8;
                border-left: 4px solid #3498db;
                padding: 1.5rem;
                border-radius: 8px;
                margin: 1.5rem 0;
            }
            .insight-title {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 0.5rem;
            }
            .control-panel {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            .Select-control {
                border-radius: 8px;
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

# Navigation bar
navbar = html.Nav([
    html.Div([
        html.A([
            html.I(className="fas fa-chart-line me-2"),
            "European Inflation Dashboard"
        ], className="navbar-brand text-white fw-bold", style={'fontSize': '1.5rem'}),
        html.Div([
            dcc.Link('Overview', href='/', className='nav-link'),
            dcc.Link('Time Series', href='/timeseries', className='nav-link'),
            dcc.Link('Country Comparison', href='/comparison', className='nav-link'),
            dcc.Link('Geographic View', href='/geographic', className='nav-link'),
        ], className='d-flex')
    ], className='container d-flex justify-content-between align-items-center')
], className='navbar')


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', className='container mt-4 mb-5')
])

# Overview Page
def overview_layout():
    return html.Div([
        html.Div([
            html.H1("European Inflation Rate Overview", className='page-title'),
            html.P("Monthly Consumer Price Index (HICP) - Annual Rate of Change", className='page-subtitle'),
            html.P(f"Data Period: {df['TIME_PERIOD'].min().strftime('%B %Y')} to {df['TIME_PERIOD'].max().strftime('%B %Y')}", 
                   className='text-muted')
        ], className='page-header'),
        
        # Country Selector
        html.Div([
            html.Label("Select Country:", className='fw-bold mb-2'),
            dcc.Dropdown(
                id='country-selector',
                options=[{'label': country, 'value': country} for country in countries],
                value=countries[0] if countries else None,
                clearable=False,
                style={'borderRadius': '8px'}
            )
        ], className='control-panel'),
        
        # Key Metrics
        html.Div(id='key-metrics', className='row mb-4'),
        
        # Main Overview Chart
        html.Div([
            dcc.Graph(id='overview-chart', config={'displayModeBar': False})
        ], className='card p-4'),
        
        # Key Insights
        html.Div(id='key-insights', className='insight-box')
    ])

# Time Series Analysis Page
def timeseries_layout():
    return html.Div([
        html.Div([
            html.H1("Time Series Analysis", className='page-title'),
            html.P("Detailed temporal patterns and trends in inflation rates", className='page-subtitle')
        ], className='page-header'),
        
        html.Div([
            html.Label("Select Country:", className='fw-bold mb-2'),
            dcc.Dropdown(
                id='ts-country-selector',
                options=[{'label': country, 'value': country} for country in countries],
                value=countries[0] if countries else None,
                clearable=False
            )
        ], className='control-panel'),
        
        html.Div([
            html.Div([
                dcc.Graph(id='ts-detailed-chart', config={'displayModeBar': False})
            ], className='card p-4 col-md-12 mb-4'),
        ], className='row'),
        
        html.Div([
            html.Div([
                dcc.Graph(id='yearly-comparison', config={'displayModeBar': False})
            ], className='card p-4 col-md-6'),
            html.Div([
                dcc.Graph(id='monthly-pattern', config={'displayModeBar': False})
            ], className='card p-4 col-md-6'),
        ], className='row')
    ])

# Country Comparison Page
def comparison_layout():
    return html.Div([
        html.Div([
            html.H1("Country Comparison", className='page-title'),
            html.P("Compare inflation rates across European countries", className='page-subtitle')
        ], className='page-header'),
        
        html.Div([
            html.Label("Select Countries to Compare (up to 5):", className='fw-bold mb-2'),
            dcc.Dropdown(
                id='multi-country-selector',
                options=[{'label': country, 'value': country} for country in countries],
                value=countries[:3] if len(countries) >= 3 else countries,
                multi=True
            )
        ], className='control-panel'),
        
        html.Div([
            html.Div([
                dcc.Graph(id='multi-country-chart', config={'displayModeBar': False})
            ], className='card p-4 col-md-12 mb-4'),
        ], className='row'),
        
        html.Div([
            html.Div([
                dcc.Graph(id='latest-comparison', config={'displayModeBar': False})
            ], className='card p-4 col-md-6'),
            html.Div([
                dcc.Graph(id='avg-comparison', config={'displayModeBar': False})
            ], className='card p-4 col-md-6'),
        ], className='row')
    ])

# Geographic View Page
def geographic_layout():
    return html.Div([
        html.Div([
            html.H1("Geographic Analysis", className='page-title'),
            html.P("Spatial distribution of inflation across Europe", className='page-subtitle')
        ], className='page-header'),
        
        html.Div([
            html.Label("Select Time Period:", className='fw-bold mb-2'),
            dcc.Dropdown(
                id='period-selector',
                options=[],
                value=None,
                clearable=False
            )
        ], className='control-panel'),
        
        html.Div([
            html.Div([
                dcc.Graph(id='europe-heatmap', config={'displayModeBar': False})
            ], className='card p-4 col-md-12 mb-4'),
        ], className='row'),
        
        html.Div([
            html.Div([
                dcc.Graph(id='top-bottom-countries', config={'displayModeBar': False})
            ], className='card p-4 col-md-12'),
        ], className='row')
    ])

# Callbacks
@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/timeseries':
        return timeseries_layout()
    elif pathname == '/comparison':
        return comparison_layout()
    elif pathname == '/geographic':
        return geographic_layout()
    else:
        return overview_layout()

@callback(
    [Output('key-metrics', 'children'),
     Output('key-insights', 'children')],
    Input('country-selector', 'value')
)
def update_metrics(country):
    if not country:
        return html.Div(), html.Div()
    
    country_df = df[df['geo'] == country].copy()
    
    if len(country_df) == 0:
        return html.Div("No data available"), html.Div()
    
    latest_rate = country_df['OBS_VALUE'].iloc[-1]
    avg_rate = country_df['OBS_VALUE'].mean()
    max_rate = country_df['OBS_VALUE'].max()
    min_rate = country_df['OBS_VALUE'].min()
    
    metrics = html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-percentage fa-2x mb-3", style={'color': '#3498db'}),
                html.Div(f"{latest_rate:.1f}%", className='metric-value'),
                html.Div("Current Rate", className='metric-label'),
                html.Small(f"{country_df['TIME_PERIOD'].max().strftime('%B %Y')}", className='text-muted')
            ], className='metric-card')
        ], className='col-md-3'),
        html.Div([
            html.Div([
                html.I(className="fas fa-chart-line fa-2x mb-3", style={'color': '#27ae60'}),
                html.Div(f"{avg_rate:.1f}%", className='metric-value'),
                html.Div("Average Rate", className='metric-label'),
                html.Small("Overall Period", className='text-muted')
            ], className='metric-card')
        ], className='col-md-3'),
        html.Div([
            html.Div([
                html.I(className="fas fa-arrow-up fa-2x mb-3", style={'color': '#e74c3c'}),
                html.Div(f"{max_rate:.1f}%", className='metric-value'),
                html.Div("Peak Rate", className='metric-label'),
                html.Small(f"{country_df.loc[country_df['OBS_VALUE'].idxmax(), 'TIME_PERIOD'].strftime('%B %Y')}", className='text-muted')
            ], className='metric-card')
        ], className='col-md-3'),
        html.Div([
            html.Div([
                html.I(className="fas fa-arrow-down fa-2x mb-3", style={'color': '#f39c12'}),
                html.Div(f"{min_rate:.1f}%", className='metric-value'),
                html.Div("Lowest Rate", className='metric-label'),
                html.Small(f"{country_df.loc[country_df['OBS_VALUE'].idxmin(), 'TIME_PERIOD'].strftime('%B %Y')}", className='text-muted')
            ], className='metric-card')
        ], className='col-md-3'),
    ], className='row')
    
    insights = html.Div([
        html.Div([
            html.I(className="fas fa-lightbulb me-2"),
            f"Key Insights for {country}"
        ], className='insight-title'),
        html.Ul([
            html.Li(f"The current inflation rate is {latest_rate:.1f}%."),
            html.Li(f"Inflation peaked at {max_rate:.1f}% in {country_df.loc[country_df['OBS_VALUE'].idxmax(), 'TIME_PERIOD'].strftime('%B %Y')}."),
            html.Li(f"The average inflation rate over the entire period is {avg_rate:.1f}%."),
            html.Li(f"Standard deviation: {country_df['OBS_VALUE'].std():.2f}% indicates {'moderate' if country_df['OBS_VALUE'].std() < 2 else 'high'} volatility.")
        ])
    ])
    
    return metrics, insights

@callback(
    Output('overview-chart', 'figure'),
    Input('country-selector', 'value')
)
def update_overview_chart(country):
    if not country:
        return {}
    
    country_df = df[df['geo'] == country].sort_values('TIME_PERIOD')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=country_df['TIME_PERIOD'],
        y=country_df['OBS_VALUE'],
        mode='lines+markers',
        name='Inflation Rate',
        line=dict(color='#3498db', width=3),
        marker=dict(size=6, color='#2c3e50'),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.1)'
    ))
    
    fig.add_hline(y=country_df['OBS_VALUE'].mean(), line_dash="dash", 
                  line_color="#e74c3c", 
                  annotation_text=f"Average: {country_df['OBS_VALUE'].mean():.1f}%",
                  annotation_position="right")
    
    fig.update_layout(
        title=f'Monthly Inflation Rate - {country}',
        xaxis_title='Time Period',
        yaxis_title='Annual Rate of Change (%)',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=450,
        margin=dict(l=60, r=40, t=80, b=60),
        xaxis=dict(showgrid=True, gridcolor='#ecf0f1'),
        yaxis=dict(showgrid=True, gridcolor='#ecf0f1')
    )
    
    return fig

@callback(
    Output('ts-detailed-chart', 'figure'),
    Input('ts-country-selector', 'value')
)
def update_ts_detailed(country):
    if not country:
        return {}
    
    country_df = df[df['geo'] == country].sort_values('TIME_PERIOD').copy()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=country_df['TIME_PERIOD'],
        y=country_df['OBS_VALUE'],
        mode='lines+markers',
        name='Inflation Rate',
        line=dict(color='#3498db', width=2),
        marker=dict(size=8, color='#2c3e50', line=dict(color='white', width=1))
    ))
    
    country_df['MA3'] = country_df['OBS_VALUE'].rolling(window=3).mean()
    fig.add_trace(go.Scatter(
        x=country_df['TIME_PERIOD'],
        y=country_df['MA3'],
        mode='lines',
        name='3-Month Moving Avg',
        line=dict(color='#e74c3c', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=f'Inflation Rate with Moving Average - {country}',
        xaxis_title='Month',
        yaxis_title='Rate (%)',
        height=400,
        plot_bgcolor='white',
        hovermode='x unified'
    )
    
    return fig

@callback(
    Output('yearly-comparison', 'figure'),
    Input('ts-country-selector', 'value')
)
def update_yearly_comparison(country):
    if not country:
        return {}
    
    country_df = df[df['geo'] == country]
    yearly_avg = country_df.groupby('Year')['OBS_VALUE'].mean().reset_index()
    
    fig = go.Figure(data=[
        go.Bar(
            x=yearly_avg['Year'],
            y=yearly_avg['OBS_VALUE'],
            marker=dict(
                color=yearly_avg['OBS_VALUE'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Rate (%)")
            ),
            text=[f"{val:.1f}%" for val in yearly_avg['OBS_VALUE']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f'Average Inflation Rate by Year - {country}',
        xaxis_title='Year',
        yaxis_title='Average Rate (%)',
        height=400,
        plot_bgcolor='white'
    )
    
    return fig

@callback(
    Output('monthly-pattern', 'figure'),
    Input('ts-country-selector', 'value')
)
def update_monthly_pattern(country):
    if not country:
        return {}
    
    country_df = df[df['geo'] == country]
    monthly_avg = country_df.groupby('Month')['OBS_VALUE'].mean().reset_index()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_avg['Month_Name'] = monthly_avg['Month'].apply(lambda x: month_names[x-1])
    
    fig = go.Figure(data=[
        go.Scatterpolar(
            r=monthly_avg['OBS_VALUE'],
            theta=monthly_avg['Month_Name'],
            fill='toself',
            fillcolor='rgba(52, 152, 219, 0.3)',
            line=dict(color='#3498db', width=2),
            marker=dict(size=8, color='#2c3e50')
        )
    ])
    
    fig.update_layout(
        title=f'Seasonal Pattern - {country}',
        polar=dict(
            radialaxis=dict(visible=True, range=[0, monthly_avg['OBS_VALUE'].max() * 1.1])
        ),
        height=400
    )
    
    return fig

@callback(
    Output('multi-country-chart', 'figure'),
    Input('multi-country-selector', 'value')
)
def update_multi_country(countries_list):
    if not countries_list or len(countries_list) == 0:
        return {}
    
    # Limit to 5 countries for readability
    countries_list = countries_list[:5]
    
    fig = go.Figure()
    
    colors_list = ['#3498db', '#e74c3c', '#27ae60', '#f39c12', '#9b59b6']
    
    for idx, country in enumerate(countries_list):
        country_df = df[df['geo'] == country].sort_values('TIME_PERIOD')
        fig.add_trace(go.Scatter(
            x=country_df['TIME_PERIOD'],
            y=country_df['OBS_VALUE'],
            mode='lines+markers',
            name=country,
            line=dict(color=colors_list[idx % len(colors_list)], width=2),
            marker=dict(size=5)
        ))
    
    fig.update_layout(
        title='Multi-Country Inflation Rate Comparison',
        xaxis_title='Time Period',
        yaxis_title='Annual Rate of Change (%)',
        hovermode='x unified',
        plot_bgcolor='white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

@callback(
    Output('latest-comparison', 'figure'),
    Input('multi-country-selector', 'value')
)
def update_latest_comparison(countries_list):
    if not countries_list or len(countries_list) == 0:
        return {}
    
    latest_data = []
    for country in countries_list[:5]:
        country_df = df[df['geo'] == country].sort_values('TIME_PERIOD')
        if len(country_df) > 0:
            latest_data.append({
                'Country': country,
                'Rate': country_df['OBS_VALUE'].iloc[-1]
            })
    
    latest_df = pd.DataFrame(latest_data).sort_values('Rate', ascending=True)
    
    fig = go.Figure(data=[
        go.Bar(
            y=latest_df['Country'],
            x=latest_df['Rate'],
            orientation='h',
            marker=dict(
                color=latest_df['Rate'],
                colorscale='RdYlGn_r',
                showscale=False
            ),
            text=[f"{val:.1f}%" for val in latest_df['Rate']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title='Latest Inflation Rate by Country',
        xaxis_title='Rate (%)',
        yaxis_title='',
        height=400,
        plot_bgcolor='white'
    )
    
    return fig

@callback(
    Output('avg-comparison', 'figure'),
    Input('multi-country-selector', 'value')
)
def update_avg_comparison(countries_list):
    if not countries_list or len(countries_list) == 0:
        return {}
    
    avg_data = []
    for country in countries_list[:5]:
        country_df = df[df['geo'] == country]
        if len(country_df) > 0:
            avg_data.append({
                'Country': country,
                'Average': country_df['OBS_VALUE'].mean(),
                'StdDev': country_df['OBS_VALUE'].std()
            })
    
    avg_df = pd.DataFrame(avg_data).sort_values('Average', ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=avg_df['Country'],
        y=avg_df['Average'],
        name='Average Rate',
        marker_color='#3498db',
        text=[f"{val:.1f}%" for val in avg_df['Average']],
        textposition='outside',
        error_y=dict(
            type='data',
            array=avg_df['StdDev'],
            visible=True,
            color='#7f8c8d'
        )
    ))
    
    fig.update_layout(
        title='Average Inflation Rate with Standard Deviation',
        xaxis_title='Country',
        yaxis_title='Rate (%)',
        height=400,
        plot_bgcolor='white',
        showlegend=False
    )
    
    return fig

@callback(
    Output('period-selector', 'options'),
    Output('period-selector', 'value'),
    Input('url', 'pathname')
)
def update_period_options(pathname):
    periods = sorted(df['TIME_PERIOD'].unique(), reverse=True)
    options = [{'label': pd.to_datetime(p).strftime('%B %Y'), 'value': str(p)} for p in periods]
    return options, str(periods[0]) if len(periods) > 0 else None

@callback(
    Output('europe-heatmap', 'figure'),
    Input('period-selector', 'value')
)
def update_europe_heatmap(period):
    if not period:
        return {}
    
    period_df = df[df['TIME_PERIOD'] == pd.to_datetime(period)]
    
    fig = px.choropleth(
        period_df,
        locations='geo',
        locationmode='country names',
        color='OBS_VALUE',
        hover_name='geo',
        hover_data={'OBS_VALUE': ':.1f', 'geo': False},
        color_continuous_scale='RdYlGn_r',
        labels={'OBS_VALUE': 'Inflation Rate (%)'},
        scope='europe'
    )
    
    fig.update_layout(
        title=f'Inflation Rate Across Europe - {pd.to_datetime(period).strftime("%B %Y")}',
        height=600,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='mercator'
        )
    )
    
    return fig

@callback(
    Output('top-bottom-countries', 'figure'),
    Input('period-selector', 'value')
)
def update_top_bottom(period):
    if not period:
        return {}
    
    period_df = df[df['TIME_PERIOD'] == pd.to_datetime(period)].sort_values('OBS_VALUE')
    
    top_5 = period_df.tail(5)
    bottom_5 = period_df.head(5)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=bottom_5['geo'],
        x=bottom_5['OBS_VALUE'],
        orientation='h',
        name='Lowest 5',
        marker_color='#27ae60',
        text=[f"{val:.1f}%" for val in bottom_5['OBS_VALUE']],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        y=top_5['geo'],
        x=top_5['OBS_VALUE'],
        orientation='h',
        name='Highest 5',
        marker_color='#e74c3c',
        text=[f"{val:.1f}%" for val in top_5['OBS_VALUE']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=f'Top and Bottom 5 Countries - {pd.to_datetime(period).strftime("%B %Y")}',
        xaxis_title='Inflation Rate (%)',
        yaxis_title='',
        height=500,
        plot_bgcolor='white',
        barmode='group'
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8050)
