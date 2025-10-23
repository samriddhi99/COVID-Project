import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc

# --- 1. Load Data ---
# (Run create_data.py first to generate this file)
try:
    df = pd.read_csv('/Users/yssf/Desktop/COVID PROJECT/unemployment_monthly.csv')
except FileNotFoundError:
    print("Data file not found. Please run 'create_data.py' first.")
    print("If 'create_data.py' is not available, you can create a placeholder CSV.")
    # Create a minimal placeholder if the file is missing, so the app can start
    placeholder_data = {
        'geo': ['EU27'], 's_adj': ['Seasonally Adjusted'],
        'TIME_PERIOD': [pd.to_datetime('2020-01-01')],
        'OBS_VALUE': [15.0], 'unit': ['Percentage'], 'freq': ['Monthly']
    }
    df = pd.DataFrame(placeholder_data)
    print("Using minimal placeholder data for app initialization.")


# Convert time column to datetime objects
df['TIME_PERIOD'] = pd.to_datetime(df['TIME_PERIOD'])
df = df.sort_values(by='TIME_PERIOD')

# Get available options for controls
available_geos = sorted(df['geo'].unique())
available_s_adj = sorted(df['s_adj'].unique())


# --- 2. Initialize App ---
# Use a clean Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)
server = app.server


# --- 3. Define Reusable Styles ---
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "20rem", # Increased to give sidebar space
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


# --- 4. Define App Components ---

# The sidebar with navigation links
sidebar = html.Div(
    [
        html.H2(" Unemployment Analytics ", className="display-6"),
        html.Hr(),
        html.P(
            "A multi-page dashboard analyzing  unemployment trends.",
            className="lead",
            style={"fontSize": "0.9rem"}
        ),
        dbc.Nav(
            [
                dbc.NavLink("Time Series Overview", href="/", active="exact"),
                dbc.NavLink("Country Deep Dive", href="/deep-dive", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# --- 5. Define Page Layouts ---

# --- Layout for Page 1: Overview ---
layout_overview = dbc.Container(
    [
        dbc.Row([
            dbc.Col(html.H1("Time Series Overview"), width=12)
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Alert(
                    "Compare unemployment trends over time for multiple geographies.",
                    color="primary"
                ),
                width=12
            )
        ]),
        dbc.Row([
            # Controls Column
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Controls", className="card-title"),
                        html.Div([
                            dbc.Label("Select Geographies:", html_for="overview-geo-dropdown"),
                            dcc.Dropdown(
                                id='overview-geo-dropdown',
                                options=[{'label': geo, 'value': geo} for geo in available_geos],
                                value=['EU27', 'DE', 'FR', 'ES'] if 'EU27' in available_geos else [available_geos[0]], # Default selection
                                multi=True
                            ),
                        ]),
                        html.Hr(),
                        html.Div([
                            dbc.Label("Select Adjustment Type:", html_for="overview-s-adj-radio"),
                            dbc.RadioItems(
                                id='overview-s-adj-radio',
                                options=[{'label': s, 'value': s} for s in available_s_adj],
                                value=available_s_adj[0], # Default selection
                                inline=True
                            ),
                        ])
                    ])
                ),
                width=12 # Controls take full width on this page
            )
        ], className="mb-4"),
        dbc.Row([
            # Graph Column
            dbc.Col(
                dcc.Loading(
                    id="loading-overview-chart",
                    children=[dcc.Graph(id='overview-line-chart')],
                    type="circle"
                ),
                width=12
            )
        ])
    ],
    fluid=True
)

# --- Layout for Page 2: Deep Dive ---
layout_deepdive = dbc.Container(
    [
        dbc.Row([
            dbc.Col(html.H1("Country Deep Dive"), width=12)
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Alert(
                    "Analyze the distribution and latest data for a single country.",
                    color="info"
                ),
                width=12
            )
        ]),
        dbc.Row([
            # Controls
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Controls", className="card-title"),
                        html.Div([
                            dbc.Label("Select Geography:", html_for="deepdive-geo-dropdown"),
                            dcc.Dropdown(
                                id='deepdive-geo-dropdown',
                                options=[{'label': geo, 'value': geo} for geo in available_geos],
                                value='ES' if 'ES' in available_geos else available_geos[0], # Default single country
                                multi=False,
                                clearable=False
                            ),
                        ]),
                        html.Hr(),
                        html.Div([
                            dbc.Label("Select Adjustment Type:", html_for="deepdive-s-adj-radio"),
                            dbc.RadioItems(
                                id='deepdive-s-adj-radio',
                                options=[{'label': s, 'value': s} for s in available_s_adj],
                                value=available_s_adj[0], # Default selection
                                inline=True
                            ),
                        ])
                    ])
                ),
                width=12
            )
        ], className="mb-4"),

        # KPI Row
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(id='kpi-latest-value'), color="light"), width=4),
            dbc.Col(dbc.Card(dbc.CardBody(id='kpi-avg-value'), color="light"), width=4),
            dbc.Col(dbc.Card(dbc.CardBody(id='kpi-yoy-change'), color="light"), width=4),
        ], className="mb-4"),

        # Graphs Row
        dbc.Row([
            dbc.Col(
                dcc.Loading(dcc.Graph(id='deepdive-box-plot')),
                width=6
            ),
            dbc.Col(
                dcc.Loading(dcc.Graph(id='deepdive-bar-comparison')),
                width=6
            ),
        ])
    ],
    fluid=True
)


# --- 6. Main App Layout ---
# This layout contains the URL, sidebar, and a container for page content
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    html.Div(id='page-content', style=CONTENT_STYLE)
])


# --- 7. Callbacks ---

# --- Router Callback ---
# This callback swaps the page content based on the URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/deep-dive':
        return layout_deepdive
    else:
        # Default to overview page
        return layout_overview

# --- Page 1: Overview Callback ---
@app.callback(
    Output('overview-line-chart', 'figure'),
    [Input('overview-geo-dropdown', 'value'),
     Input('overview-s-adj-radio', 'value')]
)
def update_overview_chart(selected_geos, selected_s_adj):
    if not selected_geos:
        return go.Figure().update_layout(
            title="Please select at least one geography.",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "No data selected.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 20}
            }]
        )

    # Filter data based on selections
    dff = df[
        (df['geo'].isin(selected_geos)) &
        (df['s_adj'] == selected_s_adj)
    ]

    if dff.empty:
        return go.Figure().update_layout(
            title="No data found for the selected criteria.",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "No data available.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 20}
            }]
        )

    # Create the line chart
    fig = px.line(
        dff,
        x='TIME_PERIOD',
        y='OBS_VALUE',
        color='geo',
        title=f' Unemployment ({selected_s_adj})',
        labels={
            'TIME_PERIOD': 'Date',
            'OBS_VALUE': 'Unemployment Rate (%)',
            'geo': 'Geography'
        }
    )

    fig.update_layout(
        transition_duration=500,
        hovermode="x unified",
        legend_title_text='Geography'
    )
    fig.update_traces(
        hovertemplate='<b>%{customdata[0]}</b><br>%{x|%B %Y}<br>Rate: %{y:.1f}%<extra></extra>',
        customdata=dff[['geo']]
    )

    return fig

# --- Page 2: Deep Dive Callback ---
@app.callback(
    [Output('kpi-latest-value', 'children'),
     Output('kpi-avg-value', 'children'),
     Output('kpi-yoy-change', 'children'),
     Output('deepdive-box-plot', 'figure'),
     Output('deepdive-bar-comparison', 'figure')],
    [Input('deepdive-geo-dropdown', 'value'),
     Input('deepdive-s-adj-radio', 'value')]
)
def update_deep_dive(selected_geo, selected_s_adj):
    # Filter data
    dff_country = df[
        (df['geo'] == selected_geo) &
        (df['s_adj'] == selected_s_adj)
    ].sort_values(by='TIME_PERIOD')

    # Handle empty data frame
    if dff_country.empty:
        empty_fig = go.Figure().update_layout(
            title="No data available for this selection.",
            xaxis={"visible": False}, yaxis={"visible": False}
        )
        kpi_nodata = [html.H4("N/A", className="card-title"), html.P("No data", className="card-text")]
        return kpi_nodata, kpi_nodata, kpi_nodata, empty_fig, empty_fig

    # --- 1. Calculate KPIs ---
    
    # Latest Value
    latest_data = dff_country.iloc[-1]
    latest_val = latest_data['OBS_VALUE']
    latest_date = latest_data['TIME_PERIOD'].strftime('%B %Y')
    kpi_latest_content = [
        html.H4(f"{latest_val:.1f}%", className="card-title"),
        html.P(f"Latest Value ({latest_date})", className="card-text")
    ]

    # Average Value
    avg_val = dff_country['OBS_VALUE'].mean()
    kpi_avg_content = [
        html.H4(f"{avg_val:.1f}%", className="card-title"),
        html.P(f"Overall Average (2018-2024)", className="card-text")
    ]

    # Year-over-Year Change
    try:
        last_year_data = dff_country[
            dff_country['TIME_PERIOD'] == (latest_data['TIME_PERIOD'] - pd.DateOffset(years=1))
        ].iloc[0]
        yoy_change = latest_val - last_year_data['OBS_VALUE']
        yoy_color = "danger" if yoy_change > 0 else "success"
        yoy_icon = "bi:arrow-up" if yoy_change > 0 else "bi:arrow-down"
        kpi_yoy_content = [
            html.H4(
                f"{yoy_change:+.1f} pts",
                className=f"card-title text-{yoy_color}"
            ),
            html.P("Year-over-Year Change", className="card-text")
        ]
    except (IndexError, TypeError):
        # Not enough data for YoY
        kpi_yoy_content = [
            html.H4("N/A", className="card-title"),
            html.P("Year-over-Year Change", className="card-text")
        ]

    # --- 2. Create Box Plot ---
    # Add a year column for analysis
    dff_country['Year'] = dff_country['TIME_PERIOD'].dt.year.astype(str)
    
    fig_box = px.box(
        dff_country,
        x='Year',
        y='OBS_VALUE',
        color='Year',
        title=f'Distribution of Unemployment Rate in {selected_geo}',
        labels={'OBS_VALUE': 'Unemployment Rate (%)', 'Year': 'Year'}
    )
    fig_box.update_layout(showlegend=False)

    # --- 3. Create Bar Comparison Chart ---
    # Compare latest month to 12-month average
    avg_12m = dff_country.iloc[-12:]['OBS_VALUE'].mean()
    bar_data = pd.DataFrame({
        'Metric': ['Latest Month', '12-Month Average'],
        'Value': [latest_val, avg_12m]
    })
    
    fig_bar = px.bar(
        bar_data,
        x='Metric',
        y='Value',
        color='Metric',
        text='Value',
        title=f'Latest Rate vs. 12-Month Average ({selected_geo})',
        labels={'Value': 'Unemployment Rate (%)', 'Metric': ''}
    )
    fig_bar.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    fig_bar.update_layout(showlegend=False, yaxis_range=[0, max(latest_val, avg_12m) * 1.2])


    return kpi_latest_content, kpi_avg_content, kpi_yoy_content, fig_box, fig_bar


# --- 8. Run the App ---
if __name__ == '__main__':
    app.run(debug=True)

