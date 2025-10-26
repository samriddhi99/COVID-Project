import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import os
from constants import region_mapping, colors
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Global Economic Indicators Dashboard"

df = pd.read_csv('datasets/data_2020_2023.csv', encoding='utf-8')
    
df.columns = df.columns.str.strip()


df['GDP_Billion'] = pd.to_numeric(df['GDP (Current USD)']) / 1e9
df['GDP_PerCapita'] = pd.to_numeric(df['GDP per Capita (Current USD)'], errors='coerce')
df['Growth_Rate'] = pd.to_numeric(df['GDP Growth (% Annual)'], errors='coerce')
df['Inflation_Rate'] = pd.to_numeric(df['Inflation (CPI %)'], errors='coerce')
df['Unemployment_Rate'] = pd.to_numeric(df['Unemployment Rate (%)'], errors='coerce')


# Get unique countries and years
countries = sorted(df['country_name'].unique())
years = sorted(df['year'].unique())
latest_year = df['year'].max()


# Add region to dataframe
df['Region'] = df['country_name'].map(region_mapping).fillna('Other')

# Get unique regions
regions = sorted(df[df['Region'] != 'Other']['Region'].unique())

# Color schemes


# Stat cards function
def create_stat_card(title, value, subtitle, color, icon):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.P(title, className="text-muted mb-1", style={'fontSize': '0.875rem'}),
                    html.H3(value, className="mb-0", style={'color': color, 'fontWeight': 'bold'}),
                    html.P(subtitle, className="text-success mb-0 mt-2", 
                          style={'fontSize': '0.875rem'})
                ], style={'flex': '1'}),
                html.Div([
                    html.Span(icon, style={'fontSize': '2rem'})
                ], style={'width': '60px', 'height': '60px', 
                         'backgroundColor': f"{color}20", 
                         'borderRadius': '12px',
                         'display': 'flex', 
                         'alignItems': 'center', 
                         'justifyContent': 'center'})
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
        ])
    ], className="shadow-sm h-100", style={'borderLeft': f'4px solid {color}'})

# Header
header = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("🌍 Global Economic Indicators Dashboard", 
                           className="text-white mb-0",
                           style={'fontWeight': 'bold'}),
                    html.P("Comprehensive analysis of worldwide economic data (2020-2023)", 
                          className="text-white-50 mb-0 mt-1")
                ])
            ], width=8),
            dbc.Col([
                dcc.Dropdown(
                    id='year-selector',
                    options=[{'label': str(year), 'value': year} for year in years],
                    value=latest_year,
                    clearable=False,
                    style={'width': '150px'}
                )
            ], width=4, className="d-flex justify-content-end align-items-center")
        ], className="w-100")
    ], fluid=True),
    color="primary",
    dark=True,
    className="mb-4"
)

# Tab styles
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '12px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '3px solid #3B82F6',
    'borderBottom': '1px solid #ffffff',
    'backgroundColor': '#ffffff',
    'color': '#3B82F6',
    'padding': '12px',
    'fontWeight': 'bold'
}

# Layout
app.layout = html.Div([
    header,
    
    dbc.Container([
        # Tabs for navigation
        dcc.Tabs(id='tabs', value='tab-overview', children=[
            dcc.Tab(label='📊 Overview', value='tab-overview', 
                   style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='📈 Comparative Analysis', value='tab-comparative',
                   style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='📉 Trends & Insights', value='tab-trends',
                   style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='🔄 Country Comparison', value='tab-comparison',
                   style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='📋 Data Explorer', value='tab-data',
                   style=tab_style, selected_style=tab_selected_style),
        ], className="mb-4"),
        
        # Content area
        html.Div(id='tab-content')
    ], fluid=True, className="px-4"),
    
    # Footer
    html.Footer([
        dbc.Container([
            html.Hr(),
            html.P("Data sources: World Bank, IMF, OECD | Dashboard created for economic analysis",
                  className="text-center text-muted")
        ], fluid=True)
    ], className="mt-5 mb-3")
], style={'backgroundColor': colors['background'], 'minHeight': '100vh'})

# Main callback for tab content
@app.callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'value'),
     Input('year-selector', 'value')]
)
def render_content(tab, selected_year):
    df_year = df[df['year'] == selected_year].copy()
    
    
    if tab == 'tab-overview':
        # Calculate metrics
        total_gdp = df_year['GDP_Billion'].sum()
        avg_growth = df_year['Growth_Rate'].mean()
        avg_unemployment = df_year['Unemployment_Rate'].mean()
        countries_count = df_year['country_name'].nunique()
        
        # Top 10 economies
        top_10 = df_year.nlargest(10, 'GDP_Billion').sort_values('GDP_Billion', ascending=True)
        print(top_10)
        fig_top_economies = go.Figure(data=[
            go.Bar(
                y=top_10['country_name'],
                x=top_10['GDP_Billion'],
                orientation='h',
                marker=dict(
                    color=top_10['GDP_Billion'],
                    colorscale='Blues',
                    showscale=False
                ),
                text=top_10['GDP_Billion'].round(0),
                texttemplate='$%{text}B',
                textposition='outside'
            )
        ])
        fig_top_economies.update_layout(
            title=f"Top 10 Economies by GDP ({selected_year})",
            xaxis_title="GDP (Billion USD)",
            yaxis_title="",
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Inflation trends
        inflation_data = df.groupby('year')['Inflation_Rate'].mean().reset_index()
        
        fig_inflation = go.Figure()
        fig_inflation.add_trace(go.Scatter(
            x=inflation_data['year'],
            y=inflation_data['Inflation_Rate'],
            mode='lines+markers',
            name='Global Average',
            line=dict(color=colors['danger'], width=3),
            marker=dict(size=8)
        ))
        
        # Add selected countries
        major_economies = ['United States', 'China', 'Germany', 'United Kingdom']
        for country in major_economies:
            if country in df['country_name'].values:
                country_data = df[df['country_name'] == country]
                fig_inflation.add_trace(go.Scatter(
                    x=country_data['year'],
                    y=country_data['Inflation_Rate'],
                    mode='lines+markers',
                    name=country,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
        
        fig_inflation.update_layout(
            title="Inflation Trends (2020-2023)",
            xaxis_title="Year",
            yaxis_title="Inflation Rate (%)",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return html.Div([
            # Stat cards
            dbc.Row([
                dbc.Col([
                    create_stat_card(
                        "Global GDP",
                        f"${total_gdp/1000:.1f}T",
                        f"Year {selected_year}",
                        colors['primary'],
                        "💰"
                    )
                ], width=12, md=3),
                dbc.Col([
                    create_stat_card(
                        "Avg. Growth Rate",
                        f"{avg_growth:.1f}%",
                        "Across all countries",
                        colors['success'],
                        "📈"
                    )
                ], width=12, md=3),
                dbc.Col([
                    create_stat_card(
                        "Avg. Unemployment",
                        f"{avg_unemployment:.1f}%",
                        "Global average",
                        colors['warning'],
                        "👥"
                    )
                ], width=12, md=3),
                dbc.Col([
                    create_stat_card(
                        "Countries Analyzed",
                        str(countries_count),
                        "Global coverage",
                        colors['purple'],
                        "🌍"
                    )
                ], width=12, md=3),
            ], className="mb-4"),
            
            # Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fig_top_economies)
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fig_inflation)
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6),
            ], className="mb-4"),
            
            # Insights
            dbc.Card([
                dbc.CardBody([
                    html.H4("💡 Key Insights", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H6("Post-Pandemic Recovery", className="text-primary"),
                                html.P("Most economies showed strong GDP growth in 2021-2022, with average rates of 5-7% as restrictions eased.",
                                      className="text-muted small")
                            ], className="p-3 bg-light rounded")
                        ], width=12, md=4),
                        dbc.Col([
                            html.Div([
                                html.H6("Inflation Spike", className="text-danger"),
                                html.P("2022 saw peak inflation rates globally due to supply chain disruptions and energy costs, moderating in 2023.",
                                      className="text-muted small")
                            ], className="p-3 bg-light rounded")
                        ], width=12, md=4),
                        dbc.Col([
                            html.Div([
                                html.H6("Emerging Markets", className="text-success"),
                                html.P("Asian economies like India and China continue to lead in growth rates, driving global economic expansion.",
                                      className="text-muted small")
                            ], className="p-3 bg-light rounded")
                        ], width=12, md=4),
                    ])
                ])
            ], className="shadow-sm mb-4", style={'background': 'linear-gradient(135deg, #E0E7FF 0%, #E0F2FE 100%)'}),
            
            # Top/Bottom Performers
            dbc.Card([
                dbc.CardBody([
                    html.H4("🏆 Top & Bottom Performers", className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.H6("🚀 Highest GDP Growth", className="text-success mb-3"),
                            html.Div(id='top-growth-performers')
                        ], width=12, md=6),
                        dbc.Col([
                            html.H6("📉 Lowest GDP Growth", className="text-danger mb-3"),
                            html.Div(id='bottom-growth-performers')
                        ], width=12, md=6),
                    ]),
                    html.Hr(className="my-4"),
                    dbc.Row([
                        dbc.Col([
                            html.H6("💰 Highest GDP per Capita", className="text-primary mb-3"),
                            html.Div(id='top-gdp-per-capita')
                        ], width=12, md=6),
                        dbc.Col([
                            html.H6("📊 Lowest Unemployment", className="text-success mb-3"),
                            html.Div(id='lowest-unemployment')
                        ], width=12, md=6),
                    ])
                ])
            ], className="shadow-sm")
        ])
    
    elif tab == 'tab-comparative':
        # GDP per Capita vs Growth
        df_year_clean = df_year.dropna(subset=['GDP_PerCapita', 'Growth_Rate', 'GDP_Billion'])
        df_year_clean = df_year_clean[
            (df_year_clean['GDP_PerCapita'] > 0) & 
            (df_year_clean['Growth_Rate'].abs() < 100)
        ]
        
        fig_scatter = px.scatter(
            df_year_clean,
            x='GDP_PerCapita',
            y='Growth_Rate',
            size='GDP_Billion',
            color='Growth_Rate',
            hover_name='country_name',
            hover_data={
                'GDP_PerCapita': ':,.0f',
                'Growth_Rate': ':.2f',
                'GDP_Billion': ':,.0f'
            },
            color_continuous_scale='RdYlGn',
            title=f"GDP per Capita vs Growth Rate ({selected_year})"
        )
        fig_scatter.update_layout(
            xaxis_title="GDP per Capita (USD)",
            yaxis_title="GDP Growth Rate (%)",
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Unemployment comparison
        unemployment_top = df_year.nlargest(15, 'GDP_Billion').dropna(subset=['Unemployment_Rate'])
        unemployment_top = unemployment_top.sort_values('Unemployment_Rate', ascending=True)
        
        fig_unemployment = go.Figure(data=[
            go.Bar(
                y=unemployment_top['country_name'],
                x=unemployment_top['Unemployment_Rate'],
                orientation='h',
                marker=dict(
                    color=['#10B981' if x < 4 else '#F59E0B' if x < 7 else '#EF4444' 
                           for x in unemployment_top['Unemployment_Rate']],
                ),
                text=unemployment_top['Unemployment_Rate'].round(1),
                texttemplate='%{text}%',
                textposition='outside'
            )
        ])
        fig_unemployment.update_layout(
            title=f"Unemployment Rates - Major Economies ({selected_year})",
            xaxis_title="Unemployment Rate (%)",
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Top 20 economies growth
        top_20 = df_year.nlargest(20, 'GDP_Billion')
        
        fig_regional = go.Figure(data=[
            go.Bar(
                x=top_20['country_name'],
                y=top_20['Growth_Rate'],
                marker=dict(color=colors['purple']),
                text=top_20['Growth_Rate'].round(1),
                texttemplate='%{text}%',
                textposition='outside'
            )
        ])
        fig_regional.update_layout(
            title=f"GDP Growth Rates - Top 20 Economies ({selected_year})",
            xaxis_title="Country",
            yaxis_title="GDP Growth Rate (%)",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis={'tickangle': -45}
        )
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.P("Bubble size represents total GDP. This visualization shows the relationship between wealth (GDP per capita) and economic growth rates.",
                                  className="text-muted small mb-3"),
                            dcc.Graph(figure=fig_scatter)
                        ])
                    ], className="shadow-sm mb-4")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fig_unemployment)
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fig_regional)
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6),
            ])
        ])
    
    elif tab == 'tab-trends':
        # Time series data
        time_series = df.groupby('year').agg({
            'GDP_Billion': 'sum',
            'Growth_Rate': 'mean',
            'Inflation_Rate': 'mean'
        }).reset_index()
        
        fig_trends = go.Figure()
        
        # GDP on primary axis
        fig_trends.add_trace(go.Scatter(
            x=time_series['year'],
            y=time_series['GDP_Billion']/1000,
            name='Global GDP (Trillion USD)',
            yaxis='y',
            line=dict(color=colors['primary'], width=3),
            fill='tonexty',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        
        # Growth and Inflation on secondary axis
        fig_trends.add_trace(go.Scatter(
            x=time_series['year'],
            y=time_series['Growth_Rate'],
            name='GDP Growth (%)',
            yaxis='y2',
            line=dict(color=colors['success'], width=3, dash='dash')
        ))
        
        fig_trends.add_trace(go.Scatter(
            x=time_series['year'],
            y=time_series['Inflation_Rate'],
            name='Inflation (%)',
            yaxis='y2',
            line=dict(color=colors['danger'], width=3, dash='dot')
        ))
        
        fig_trends.update_layout(
            title="Global Economic Trends (2020-2023)",
            xaxis=dict(title='Year'),
            yaxis=dict(title='Global GDP (Trillion USD)', side='left'),
            yaxis2=dict(title='Rate (%)', overlaying='y', side='right'),
            height=500,
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified'
        )
        
        # Country selector
        country_options = [{'label': c, 'value': c} for c in sorted(countries)]
        
        return html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.P("Track the evolution of key economic indicators through the post-pandemic period.",
                                  className="text-muted small mb-3"),
                            dcc.Graph(figure=fig_trends)
                        ])
                    ], className="shadow-sm mb-4")
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Span("✅", style={'fontSize': '2rem'}),
                                html.H5("Economic Recovery Pattern", className="mt-2"),
                                html.P("The global economy showed remarkable resilience with a V-shaped recovery in 2021, bouncing back strongly after the 2020 contraction.",
                                      className="text-muted small"),
                                html.Ul([
                                    html.Li("Strong fiscal and monetary stimulus drove recovery"),
                                    html.Li("Vaccine rollout accelerated economic reopening"),
                                    html.Li("Supply chains gradually normalized")
                                ], className="small text-muted")
                            ])
                        ])
                    ], className="shadow-sm", style={'background': 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)', 'border': 'none'})
                ], width=12, md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Span("📊", style={'fontSize': '2rem'}),
                                html.H5("Inflation Dynamics", className="mt-2"),
                                html.P("2022 marked peak inflation due to energy crisis and supply disruptions, with central banks responding through aggressive rate hikes.",
                                      className="text-muted small"),
                                html.Ul([
                                    html.Li("Energy prices spiked due to geopolitical tensions"),
                                    html.Li("Central banks raised interest rates significantly"),
                                    html.Li("Inflation moderated in 2023 but remained elevated")
                                ], className="small text-muted")
                            ])
                        ])
                    ], className="shadow-sm", style={'background': 'linear-gradient(135deg, #FED7AA 0%, #FCA5A5 100%)', 'border': 'none'})
                ], width=12, md=6),
            ], className="mb-4"),
            
            dbc.Card([
                dbc.CardBody([
                    html.H5("🔍 Country Deep Dive", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select a country to explore:", className="mb-2 font-weight-bold"),
                            dcc.Dropdown(
                                id='country-selector',
                                options=country_options,
                                value='United States',
                                clearable=False,
                                searchable=True,
                                placeholder="Type to search countries..."
                            )
                        ], width=12, md=6)
                    ], className="mb-3"),
                    html.Div(id='country-profile')
                ])
            ], className="shadow-sm")
        ])
    
    elif tab == 'tab-comparison':
        # Country Comparison Tab
        return html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🔄 Compare Two Countries Side-by-Side", className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select First Country:", className="font-weight-bold mb-2"),
                            dcc.Dropdown(
                                id='compare-country-1',
                                options=[{'label': c, 'value': c} for c in sorted(countries)],
                                value='United States',
                                clearable=False,
                                searchable=True
                            )
                        ], width=12, md=5),
                        dbc.Col([
                            html.Div("VS", className="text-center font-weight-bold text-primary", 
                                    style={'fontSize': '2rem', 'marginTop': '30px'})
                        ], width=12, md=2),
                        dbc.Col([
                            html.Label("Select Second Country:", className="font-weight-bold mb-2"),
                            dcc.Dropdown(
                                id='compare-country-2',
                                options=[{'label': c, 'value': c} for c in sorted(countries)],
                                value='China',
                                clearable=False,
                                searchable=True
                            )
                        ], width=12, md=5),
                    ], className="mb-4")
                ])
            ], className="shadow-sm mb-4"),
            
            html.Div(id='comparison-content')
        ])
    
    elif tab == 'tab-data':
        # Data Explorer Tab with Regional Filter
        return html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H4("📋 Data Explorer", className="mb-4"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Filter by Region:", className="font-weight-bold mb-2"),
                            dcc.Dropdown(
                                id='region-filter',
                                options=[{'label': 'All Regions', 'value': 'All'}] + 
                                        [{'label': r, 'value': r} for r in regions],
                                value='All',
                                clearable=False
                            )
                        ], width=12, md=4),
                        dbc.Col([
                            html.Label("Filter by Year:", className="font-weight-bold mb-2"),
                            dcc.Dropdown(
                                id='data-year-filter',
                                options=[{'label': 'All Years', 'value': 'All'}] + 
                                        [{'label': str(y), 'value': y} for y in years],
                                value=latest_year,
                                clearable=False
                            )
                        ], width=12, md=4),
                        dbc.Col([
                            html.Label("Search Country:", className="font-weight-bold mb-2"),
                            dcc.Input(
                                id='country-search',
                                type='text',
                                placeholder='Type to search...',
                                className='form-control'
                            )
                        ], width=12, md=4),
                    ], className="mb-3")
                ])
            ], className="shadow-sm mb-4"),
            
            html.Div(id='data-table-container')
        ])

# Callback for Country Profile
@app.callback(
    Output('country-profile', 'children'),
    [Input('country-selector', 'value'),
     Input('year-selector', 'value')]
)
def update_country_profile(country, year):
    country_data_year = df[(df['country_name'] == country) & (df['year'] == year)]
    
    if country_data_year.empty:
        return html.Div("No data available for selected country and year", className="text-muted")
    
    country_data = country_data_year.iloc[0]
    
    # Time series for selected country
    country_timeseries = df[df['country_name'] == country].sort_values('year')
    
    fig_country = go.Figure()
    fig_country.add_trace(go.Scatter(
        x=country_timeseries['year'],
        y=country_timeseries['GDP_Billion'],
        name='GDP',
        line=dict(color=colors['primary'], width=3),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    fig_country.update_layout(
        title=f"{country} - GDP Trend",
        xaxis_title="Year",
        yaxis_title="GDP (Billion USD)",
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return html.Div([
        dbc.Alert([
            html.H5(f"{country} - Economic Profile ({year})", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.P("GDP", className="text-muted small mb-1"),
                        html.H4(f"${country_data['GDP_Billion']:.0f}B", className="text-primary mb-0")
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.P("Growth Rate", className="text-muted small mb-1"),
                        html.H4(f"{country_data['Growth_Rate']:.2f}%", className="text-success mb-0")
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.P("Inflation", className="text-muted small mb-1"),
                        html.H4(f"{country_data['Inflation_Rate']:.2f}%", className="text-warning mb-0")
                    ], className="text-center")
                ], width=3),
                dbc.Col([
                    html.Div([
                        html.P("Unemployment", className="text-muted small mb-1"),
                        html.H4(f"{country_data['Unemployment_Rate']:.2f}%", className="text-danger mb-0")
                    ], className="text-center")
                ], width=3),
            ])
        ], color="light"),
        dcc.Graph(figure=fig_country)
    ])

# Callbacks for Top/Bottom Performers
@app.callback(
    [Output('top-growth-performers', 'children'),
     Output('bottom-growth-performers', 'children'),
     Output('top-gdp-per-capita', 'children'),
     Output('lowest-unemployment', 'children')],
    [Input('year-selector', 'value')]
)
def update_performers(selected_year):
    df_year = df[df['year'] == selected_year].copy()
    
    # Top 5 GDP Growth
    top_growth = df_year.nlargest(5, 'Growth_Rate')[['country_name', 'Growth_Rate']].dropna()
    top_growth_list = html.Ol([
        html.Li(f"{row['country_name']}: {row['Growth_Rate']:.2f}%", className="mb-2")
        for _, row in top_growth.iterrows()
    ], className="text-success")
    
    # Bottom 5 GDP Growth
    bottom_growth = df_year.nsmallest(5, 'Growth_Rate')[['country_name', 'Growth_Rate']].dropna()
    bottom_growth_list = html.Ol([
        html.Li(f"{row['country_name']}: {row['Growth_Rate']:.2f}%", className="mb-2")
        for _, row in bottom_growth.iterrows()
    ], className="text-danger")
    
    # Top 5 GDP per Capita
    top_gdp_pc = df_year.nlargest(5, 'GDP_PerCapita')[['country_name', 'GDP_PerCapita']].dropna()
    top_gdp_pc_list = html.Ol([
        html.Li(f"{row['country_name']}: ${row['GDP_PerCapita']:,.0f}", className="mb-2")
        for _, row in top_gdp_pc.iterrows()
    ], className="text-primary")
    
    # Lowest 5 Unemployment
    lowest_unemp = df_year.nsmallest(5, 'Unemployment_Rate')[['country_name', 'Unemployment_Rate']].dropna()
    lowest_unemp_list = html.Ol([
        html.Li(f"{row['country_name']}: {row['Unemployment_Rate']:.2f}%", className="mb-2")
        for _, row in lowest_unemp.iterrows()
    ], className="text-success")
    
    return top_growth_list, bottom_growth_list, top_gdp_pc_list, lowest_unemp_list

# Callback for Country Comparison
@app.callback(
    Output('comparison-content', 'children'),
    [Input('compare-country-1', 'value'),
     Input('compare-country-2', 'value'),
     Input('year-selector', 'value')]
)
def update_comparison(country1, country2, year):
    df_c1 = df[(df['country_name'] == country1) & (df['year'] == year)]
    df_c2 = df[(df['country_name'] == country2) & (df['year'] == year)]
    
    if df_c1.empty or df_c2.empty:
        return html.Div("No data available for comparison", className="text-muted")
    
    c1_data = df_c1.iloc[0]
    c2_data = df_c2.iloc[0]
    
    # Comparison metrics
    metrics = [
        ('GDP (Billion USD)', c1_data['GDP_Billion'], c2_data['GDP_Billion'], 'B'),
        ('GDP per Capita (USD)', c1_data['GDP_PerCapita'], c2_data['GDP_PerCapita'], ''),
        ('Growth Rate (%)', c1_data['Growth_Rate'], c2_data['Growth_Rate'], '%'),
        ('Inflation Rate (%)', c1_data['Inflation_Rate'], c2_data['Inflation_Rate'], '%'),
        ('Unemployment Rate (%)', c1_data['Unemployment_Rate'], c2_data['Unemployment_Rate'], '%'),
    ]
    
    comparison_cards = []
    for metric_name, val1, val2, suffix in metrics:
        winner = country1 if val1 > val2 else country2
        if 'Unemployment' in metric_name:
            winner = country1 if val1 < val2 else country2
        
        comparison_cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(metric_name, className="text-muted mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.P(country1, className="small mb-1"),
                                html.H5(f"{val1:,.2f}{suffix}", 
                                       className="text-primary" if winner == country1 else "text-muted")
                            ], width=6),
                            dbc.Col([
                                html.P(country2, className="small mb-1"),
                                html.H5(f"{val2:,.2f}{suffix}", 
                                       className="text-primary" if winner == country2 else "text-muted")
                            ], width=6),
                        ])
                    ])
                ], className="shadow-sm h-100")
            ], width=12, md=6, lg=4, className="mb-3")
        )
    
    # Time series comparison
    c1_timeseries = df[df['country_name'] == country1].sort_values('year')
    c2_timeseries = df[df['country_name'] == country2].sort_values('year')
    
    fig_comparison = go.Figure()
    fig_comparison.add_trace(go.Scatter(
        x=c1_timeseries['year'],
        y=c1_timeseries['GDP_Billion'],
        name=country1,
        line=dict(color=colors['primary'], width=3)
    ))
    fig_comparison.add_trace(go.Scatter(
        x=c2_timeseries['year'],
        y=c2_timeseries['GDP_Billion'],
        name=country2,
        line=dict(color=colors['danger'], width=3)
    ))
    fig_comparison.update_layout(
        title=f"GDP Comparison: {country1} vs {country2}",
        xaxis_title="Year",
        yaxis_title="GDP (Billion USD)",
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Growth rate comparison
    fig_growth = go.Figure()
    fig_growth.add_trace(go.Bar(
        x=c1_timeseries['year'],
        y=c1_timeseries['Growth_Rate'],
        name=country1,
        marker_color=colors['success']
    ))
    fig_growth.add_trace(go.Bar(
        x=c2_timeseries['year'],
        y=c2_timeseries['Growth_Rate'],
        name=country2,
        marker_color=colors['warning']
    ))
    fig_growth.update_layout(
        title=f"Growth Rate Comparison: {country1} vs {country2}",
        xaxis_title="Year",
        yaxis_title="GDP Growth Rate (%)",
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        barmode='group'
    )
    
    return html.Div([
        dbc.Row(comparison_cards),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_comparison)
                    ])
                ], className="shadow-sm")
            ], width=12, lg=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig_growth)
                    ])
                ], className="shadow-sm")
            ], width=12, lg=6),
        ])
    ])

# Callback for Data Table
@app.callback(
    Output('data-table-container', 'children'),
    [Input('region-filter', 'value'),
     Input('data-year-filter', 'value'),
     Input('country-search', 'value')]
)
def update_data_table(region, year_filter, search_text):
    # Filter data
    filtered_df = df.copy()
    
    if region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == region]
    
    if year_filter != 'All':
        filtered_df = filtered_df[filtered_df['year'] == year_filter]
    
    if search_text:
        filtered_df = filtered_df[filtered_df['country_name'].str.contains(search_text, case=False, na=False)]
    
    # Select columns to display
    display_columns = [
        'country_name', 'Region', 'year', 'GDP_Billion', 'GDP_PerCapita', 
        'Growth_Rate', 'Inflation_Rate', 'Unemployment_Rate'
    ]
    
    table_df = filtered_df[display_columns].copy()
    table_df.columns = ['Country', 'Region', 'Year', 'GDP (B USD)', 'GDP per Capita', 
                        'Growth Rate (%)', 'Inflation (%)', 'Unemployment (%)']
    
    # Regional summary
    if region != 'All' and not filtered_df.empty:
        regional_summary = filtered_df.groupby('year').agg({
            'GDP_Billion': 'sum',
            'Growth_Rate': 'mean',
            'Inflation_Rate': 'mean',
            'Unemployment_Rate': 'mean'
        }).reset_index()
        
        fig_regional = go.Figure()
        fig_regional.add_trace(go.Bar(
            x=regional_summary['year'],
            y=regional_summary['GDP_Billion'],
            name='Total GDP',
            marker_color=colors['primary']
        ))
        fig_regional.update_layout(
            title=f"{region} - Total GDP by Year",
            xaxis_title="Year",
            yaxis_title="Total GDP (Billion USD)",
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        regional_chart = dbc.Card([
            dbc.CardBody([
                html.H5(f"📊 {region} Regional Summary", className="mb-3"),
                dcc.Graph(figure=fig_regional),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.P("Avg Growth Rate", className="text-muted small mb-1"),
                            html.H5(f"{regional_summary['Growth_Rate'].mean():.2f}%", className="text-success")
                        ], className="text-center p-3 bg-light rounded")
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.P("Avg Inflation", className="text-muted small mb-1"),
                            html.H5(f"{regional_summary['Inflation_Rate'].mean():.2f}%", className="text-warning")
                        ], className="text-center p-3 bg-light rounded")
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.P("Avg Unemployment", className="text-muted small mb-1"),
                            html.H5(f"{regional_summary['Unemployment_Rate'].mean():.2f}%", className="text-danger")
                        ], className="text-center p-3 bg-light rounded")
                    ], width=4),
                ])
            ])
        ], className="shadow-sm mb-4")
    else:
        regional_chart = html.Div()
    
    return html.Div([
        regional_chart,
        dbc.Card([
            dbc.CardBody([
                html.H5(f"📋 Data Table ({len(table_df)} records)", className="mb-3"),
                dash_table.DataTable(
                    data=table_df.round(2).to_dict('records'),
                    columns=[{'name': col, 'id': col} for col in table_df.columns],
                    page_size=20,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'fontFamily': 'Arial, sans-serif',
                        'fontSize': '14px'
                    },
                    style_header={
                        'backgroundColor': colors['primary'],
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f8f9fa'
                        },
                        {
                            'if': {'column_id': 'Growth Rate (%)'},
                            'color': colors['success'],
                            'fontWeight': 'bold'
                        },
                        {
                            'if': {'column_id': 'Inflation (%)'},
                            'color': colors['warning'],
                            'fontWeight': 'bold'
                        },
                        {
                            'if': {'column_id': 'Unemployment (%)'},
                            'color': colors['danger'],
                            'fontWeight': 'bold'
                        }
                    ],
                    sort_action='native',
                    filter_action='native',
                    export_format='csv',
                    export_headers='display'
                )
            ])
        ], className="shadow-sm")
    ])

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Dashboard is starting...")
    print("="*60)
    print("\n📊 Open your browser and go to: http://localhost:8050")
    print("\n⏹️  Press CTRL+C to stop the server\n")
    app.run(debug=True, port=8050)