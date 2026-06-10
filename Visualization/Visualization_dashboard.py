# --- Imports ---
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib
matplotlib.use('Agg')   # ✅ Use non-GUI backend (no Tkinter, no warnings)
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State

# --- !!! IMPORTANT !!! ---
# You MUST load your dataframes 'movies_df' and 'df' in a cell 
# BEFORE running this code, or load them right here.
#
# Example (uncomment and modify to load your data):
# movies_df = pd.read_csv('your_movies_data.csv')
# df = pd.read_csv('your_ratings_data.csv') 
#
# --- End of Data Loading ---

movies_df = pd.read_csv(r"C:\Users\Sreekar\Sem-3\DCV\DA2402-Project\DataPreProcessing\PreProcessedData\movie_level_data.csv")
df = pd.read_csv(r"C:\Users\Sreekar\Sem-3\DCV\DA2402-Project\DataPreProcessing\PreProcessedData\cleaned_data.csv")

# Define genre columns
genre_cols = [
    'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary',
    'Drama', 'Fantasy', 'Film Noir', 'Horror', 'Imax', 'Musical', 'Mystery',
    'Romance', 'Science Fiction', 'Thriller', 'War', 'Western'
]

# --- Create the main app ---
# Using 'Dash' is fine, but for advanced Jupyter integration (like inline plots),
# you might explore 'from jupyter_dash import JupyterDash' and use 'JupyterDash' here.
# For your request (external link), 'dash.Dash' is perfectly fine.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)

app.index_string = app.index_string.replace(
    '</head>',
    """
    <style>
        /* Fix dropdown text color */
        .Select-control, .Select-menu-outer, .Select-value-label, .Select-placeholder {
            color: black !important;
        }
        .Select-menu-outer {
            background-color: white !important;
        }
        .Select--multi .Select-value {
            color: black !important;
        }
    </style>
    </head>
    """
)

# --- App Layout with Navigation ---
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Movie Analytics Dashboard", className="text-center mt-4 mb-4"),
            html.P("Interactive analysis of movie ratings, genres, and trends", 
                   className="text-center text-muted mb-4")
        ])
    ]),
    
    # Navigation
    dbc.Row([
        dbc.Col([
            dbc.Nav([
                dbc.NavLink("Movies by Genre", href="/", active="exact", id="page-1-link"),
                dbc.NavLink("Movie Ratings", href="/page-2", active="exact", id="page-2-link"),
                dbc.NavLink("Rating Distribution", href="/page-3", active="exact", id="page-3-link"),
                dbc.NavLink("Tag Frequency", href="/page-4", active="exact", id="page-4-link"),
                dbc.NavLink("Genre Correlation", href="/page-5", active="exact", id="page-5-link"),
            ], pills=True, vertical=False, className="mb-4 justify-content-center")
        ])
    ]),
    
    # Page Content
    dbc.Row([
        dbc.Col([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ])
    ])
], fluid=True)

# --- Page 1: Movies by Decade ---
yearly_overall = movies_df.groupby('year')['average_rating'].mean().reset_index()
yearly_overall['Genre'] = 'Overall'

page_1_layout = dbc.Container([
    html.H2("Number of Movies by Genre", className="mt-4 mb-4 text-center"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Year Range:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='year-slider-1',
                min=int(movies_df['year'].min()),
                max=int(movies_df['year'].max()),
                step=1,
                value=[int(movies_df['year'].min()), int(movies_df['year'].max())],
                marks={int(y): str(int(y)) for y in range(int(movies_df['year'].min()), int(movies_df['year'].max())+1, 10)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], md=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(html.H5(id='decade-info-1', className="mb-3 text-center"))
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='genre-count-graph-1'), width=12)
    ]),
    
    # Interpretation text
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Interpretation:", className="mt-4 mb-2"),
                html.P("This bar chart shows the distribution of movies across different genres. Drama and Comedy typically dominate in terms of volume, while niche genres like Film Noir and Western have fewer productions. The trend reflects audience preferences and production costs across different categories."),
            ], className="bg-dark p-3 rounded")
        ], width=12)
    ])
], fluid=True)


# --- Page 2: Genre Ratings Analysis ---
page_2_layout = dbc.Container([
    html.H2("Movie Ratings Analysis", className="mt-4 mb-4 text-center"),

    dbc.Row([
        html.H4("Ratings with Genre", className="text-center mb-3"),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Select Year Range:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='year-slider-2',
                min=int(movies_df['year'].min()),
                max=int(movies_df['year'].max()),
                step=1,
                value=[int(movies_df['year'].min()), int(movies_df['year'].max())],
                marks={int(y): str(int(y)) for y in range(int(movies_df['year'].min()), int(movies_df['year'].max())+1, 10)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], md=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Genres:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='genre-dropdown-2',
                options=[{'label': g, 'value': g} for g in genre_cols],
                value=genre_cols,
                multi=True,
                placeholder="Select genres..."
            )
        ], md=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Metric:", style={'fontWeight': 'bold'}),
            dcc.RadioItems(
                id='metric-toggle-2',
                options=[
                    {'label': 'Total Ratings', 'value': 'count'},
                    {'label': 'Weighted Average Rating', 'value': 'average'}
                ],
                value='count',
                inline=True,
                inputStyle={"margin-right": "6px", "margin-left": "12px"}
            )
        ], md=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(html.H5(id='info-text-2', className="text-center mb-3"), width=12)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='ratings-genre-bar-2', style={'height': '600px'}), width=12)
    ]),
    
    # Interpretation for first chart
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Interpretation:", className="mt-4 mb-2"),
                html.P("This chart compares genres by either total rating counts or weighted average ratings. Popular genres like Drama and Comedy typically receive more ratings, while Documentary and Film Noir often achieve higher average ratings, suggesting niche appeal with dedicated audiences."),
            ], className="bg-dark p-3 rounded")
        ], width=12)
    ]),

    dbc.Row(className="mb-5"),
    dbc.Row(className="mb-5"),

    dbc.Row([
        dbc.Col([
            html.H4("Ratings with Time Series", className="text-center mb-3"),
            html.Label("Select Genres:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='genre-dropdown-3',
                options=[{'label': g, 'value': g} for g in ['Overall'] + genre_cols],
                value=['Action', 'Comedy'],
                multi=True,
                placeholder="Select genres..."
            ),
            html.Div([
                dbc.Button("Play", id='play-pause-button-3', color="success", className="me-2"),
                dbc.Button("Reset", id='reset-button-3', color="danger"),
            ], className="mt-3 mb-3"),
            
            dcc.Interval(
                id='animation-interval-3',
                interval=200,
                n_intervals=0,
                disabled=False
            )
        ], md=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(html.H5(id='info-text-3', className="text-center mb-3"), width=12)
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='genre-lineplot-3', style={'height': '600px'}), width=12)
    ]),
    
    # Interpretation for second chart
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Interpretation:", className="mt-4 mb-2"),
                html.P("The time series reveals rating trends across decades. Some genres maintain consistent high ratings, while others like Action and Comedy fluctuFate with cultural trends and technological advancements in filmmaking."),
            ], className="bg-dark p-3 rounded")
        ], width=12)
    ])
], fluid=True)


# --- Page 3: Combined Ratings Analysis ---
page_3_layout = dbc.Container([
    html.H2("Ratings Analysis", className="mt-4 mb-4 text-center"),

    # Row 1: Scatter Plot
    dbc.Row([
        dbc.Col([
            html.H4("Average Rating vs Number of Ratings", className="text-center mb-3"),
            html.Label("Filter by Genre:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='scatter-genre-dropdown-4',
                options = [{'label': g, 'value': g} for g in ['Overall'] + sorted(genre_cols)],
                value = 'Overall',
                multi = False,
                clearable = False,
                className = "mb-3"
            ),
            dcc.Graph(id='rating-scatter-4', style={'height': '600px'})
        ], width=12, className="mb-5")
    ], className="mb-5"),
    
    # Interpretation for scatter plot
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Interpretation:", className="mt-2 mb-2"),
                html.P("This scatter plot shows the relationship between popularity (number of ratings) and quality (average rating). Most movies cluster in the middle, while highly-rated popular movies appear in the top-right quadrant."),
            ], className="bg-dark p-3 rounded")
        ], width=12)
    ], className="mb-5"),

    # Row 2: Pareto Chart
    dbc.Row([
        dbc.Col([
           html.H4("User Rating Analysis - Pareto Chart", className="text-center mb-3"),
           dcc.Graph(id='pareto-chart-4', style={'height': '600px'})
        ], width=12)
    ], className="mb-5"),
    
    # Interpretation for Pareto chart
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Interpretation:", className="mt-2 mb-2"),
                html.P("The Pareto principle is evident here - a small percentage of active users contribute most ratings. This highlights the importance of power users in rating systems and suggests rating platforms are dominated by enthusiastic movie enthusiasts."),
            ], className="bg-dark p-3 rounded")
        ], width=12)
    ], className="mb-5"),

    # Row 3: Violin Plot
    dbc.Row([
       dbc.Col([
           html.H4("Rating Distribution by User Activity Level and Genre", className="text-center mb-3"),
           html.Label("Select Genres:", style={'fontWeight': 'bold'}),
           dcc.Dropdown(
               id='genre-dropdown-4',
               options=[{'label': g, 'value': g} for g in ['Overall'] + sorted(genre_cols)],
               value=['Overall'],
               multi=True,
               placeholder="Select one or more genres..."
           ),
           html.H5(id='info-text-4', className="text-center mt-3 mb-3"),
           dcc.Graph(id='violin-plot-4', style={'height': '600px'})
       ], width=12)
    ]),
    
    # Interpretation for violin plot
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Interpretation:", className="mt-4 mb-2"),
                html.P("Violin plots show rating distributions across user activity levels. Active users often rate more critically (wider spread), while casual viewers tend toward extreme ratings. Some genres maintain consistent ratings across all user types, indicating universal appeal."),
            ], className="bg-dark p-3 rounded")
        ], width=12)
    ]),

    dcc.Store(id='page-4-visited', data=False)
], fluid=True)

# --- Page 4: Tag Analysis ---
def generate_wordcloud_figure():
    tags = df['tag'].dropna()
    tags = tags.astype(str).str.lower()
    all_tags = ' '.join(tags)
    
    stopwords = set(STOPWORDS)
    custom_stopwords = {"movie", "film", "good", "bad", "watch", "seen"}
    stopwords.update(custom_stopwords)
    
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='black',
        stopwords=stopwords,
        colormap='plasma',
        max_words=200
    ).generate(all_tags)
    
    # Convert matplotlib figure to base64 for displaying in Dash
    plt.figure(figsize=(14, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("Most Common User Tags", fontsize=20, weight='bold', pad=20)
    
    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', dpi=100)
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return f"data:image/png;base64,{image_base64}"

page_4_layout = dbc.Container([
    html.H2("User Tag Analysis", className="mt-4 mb-4 text-center"),
    
    dbc.Row([
        dbc.Col([
            html.Img(id='wordcloud-image-5', style={'width': '100%', 'height': 'auto'})
        ], width=12)
    ]),
    
    # Interpretation for wordcloud
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Interpretation:", className="mt-4 mb-2"),
                html.P("The word cloud visualizes most frequent user-generated tags. Larger words indicate higher frequency. This reveals common viewing contexts (comedy, romance), emotional responses (funny, boring), and thematic elements that resonate with audiences beyond official genre classifications."),
            ], className="bg-dark p-3 rounded")
        ], width=12)
    ])
], fluid=True)

# --- Page 5: Genre Correlation ---
default_genres = sorted(['Action', 'Adventure', 'Animation', 'Children', 'Comedy',
                         'Crime', 'Fantasy', 'Horror', 'Science Fiction', 'Thriller'])

page_5_layout = dbc.Container([
    html.H2("Genre Correlation Heatmap", className="mt-4 mb-4 text-center"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Genres to Compare:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='genre-dropdown-6',
                options=[{'label': g, 'value': g} for g in sorted(genre_cols)],
                value=default_genres,
                multi=True,
                placeholder="Select one or more genres..."
            )
        ], md=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='genre-heatmap-6', style={'height': '800px', 'margin': '0 auto'}), width=12, className="text-center mx-auto")
    ]),
    
    # Interpretation for heatmap
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Interpretation:", className="mt-4 mb-2"),
                html.P("The correlation matrix shows how often genres co-occur in movies. Strong positive correlations (blue) indicate frequent genre combinations (Action-Adventure), while negative correlations (red) suggest mutually exclusive pairings. Diagonal elements are always 1 (perfect self-correlation)."),
            ], className="bg-dark p-3 rounded")
        ], width=12)
    ])
], fluid=True)

# --- Callback for page navigation ---
@callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    elif pathname == '/page-3':
        return page_3_layout
    elif pathname == '/page-4':
        return page_4_layout
    elif pathname == '/page-5':
        return page_5_layout
    else:
        return page_1_layout

# --- Callbacks for Page 1 ---
@callback(
    [Output('genre-count-graph-1', 'figure'),
     Output('decade-info-1', 'children')],
    Input('year-slider-1', 'value')
)
def update_genre_count_1(selected_year_range):
    start_year, end_year = selected_year_range
    # Filter by the specific start and end years from the slider
    filtered = movies_df[(movies_df['year'] >= start_year) & (movies_df['year'] <= end_year)]

    genre_counts = []
    for g in genre_cols:
        genre_counts.append({'Genre': g, 'Movie Count': int(filtered[g].sum())})

    count_df = pd.DataFrame(genre_counts).sort_values('Movie Count', ascending=False)

    fig = px.bar(
        count_df,
        x='Genre',
        y='Movie Count',
        title=f"Number of Movies by Genre ({start_year}–{end_year})",
        color='Movie Count',
        color_continuous_scale='Greens',
        text='Movie Count'
    )

    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        title_x=0.5,
        height=550,
        template='plotly_dark',
        margin=dict(l=40, r=40, t=60, b=100),
        xaxis_title="Genre",
        yaxis_title="Number of Movies"
    )

    info_text = f"{len(filtered)} movies released between {start_year} and {end_year}."
    return fig, info_text

# --- Callbacks for Page 2 ---
@callback(
    Output('ratings-genre-bar-2', 'figure'),
    [Input('year-slider-2', 'value'),
     Input('genre-dropdown-2', 'value'),
     Input('metric-toggle-2', 'value')]
)
def update_genre_plot_2(selected_years, selected_genres, selected_metric):
    start_year, end_year = selected_years

    if not selected_genres:
        selected_genres = genre_cols

    filtered = movies_df[(movies_df['year'] >= start_year) & (movies_df['year'] <= end_year)].copy()

    if selected_metric == 'count':
        genre_values = {
            genre: (filtered[genre] * filtered['rating_count']).sum()
            for genre in selected_genres
        }
        avg_value = pd.Series(list(genre_values.values())).mean()
        metric_label = 'Total Ratings'
        title = f"Total Ratings by Genre ({start_year}–{end_year})"
        color_scale = 'Viridis'
    else:
        genre_values = {}
        for genre in selected_genres:
            genre_movies = filtered[filtered[genre] == 1]
            if not genre_movies.empty:
                weighted_avg = (
                    (genre_movies['average_rating'] * genre_movies['rating_count']).sum()
                    / genre_movies['rating_count'].sum()
                )
                genre_values[genre] = weighted_avg
            else:
                genre_values[genre] = 0

        avg_value = (
            (filtered['average_rating'] * filtered['rating_count']).sum()
            / filtered['rating_count'].sum()
        )
        metric_label = 'Weighted Average Rating'
        title = f"Weighted Average Ratings by Genre ({start_year}–{end_year})"
        color_scale = 'Viridis'

    df_plot = pd.DataFrame(list(genre_values.items()), columns=['Genre', metric_label])
    df_plot = df_plot.sort_values(by=metric_label, ascending=False)

    fig = px.bar(
        df_plot,
        x='Genre',
        y=metric_label,
        text_auto=',.0f', # Changed to remove decimals and add thousands separator
        title=title,
        color=metric_label,
        color_continuous_scale=color_scale
    )

    fig.add_hline(
        y=avg_value,
        line_dash="dot",
        line_color="white",
        annotation_text=f"Avg {metric_label}: {avg_value:.2f}",
        annotation_position="top right"
    )

    fig.update_traces(textposition='outside', marker_line_color='black', marker_line_width=0.8)
    fig.update_yaxes(tickformat=',') # Added to force full numbers with commas on Y-axis
    
    if selected_metric == 'average':
        fig.update_yaxes(range=[2.5, 4.5])
        
    fig.update_layout(
        template='plotly_dark',
        title_x=0.5,
        margin=dict(l=50, r=50, t=80, b=50),
        coloraxis_showscale=False,
        xaxis={'categoryorder': 'total descending'}
    )

    return fig

# --- Callbacks for Page 3 ---

@app.callback(
    [Output('animation-interval-3', 'disabled'),
     Output('play-pause-button-3', 'children'),
     Output('play-pause-button-3', 'color')],
    [Input('play-pause-button-3', 'n_clicks'),
     Input('reset-button-3', 'n_clicks')],
    [State('animation-interval-3', 'disabled')]
)
def toggle_animation(play_pause_clicks, reset_clicks, is_disabled):
    ctx = dash.callback_context
    if not ctx.triggered:
        return True, "Play", "success"  # Default state
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'play-pause-button-3':
        if is_disabled:
            return False, "Pause", "warning"  # Start animation
        else:
            return True, "Play", "success"     # Pause animation
    elif button_id == 'reset-button-3':
        return True, "Play", "success"         # Reset to initial state
    
    return True, "Play", "success"

# Keep this reset callback (add if you don't have it):
@app.callback(
    Output('animation-interval-3', 'n_intervals'),
    [Input('reset-button-3', 'n_clicks')]
)
def reset_animation(reset_clicks):
    if reset_clicks:
        return 0
    return dash.no_update

@app.callback(
    Output('genre-lineplot-3', 'figure'),
    [Input('genre-dropdown-3', 'value'),
     Input('animation-interval-3', 'n_intervals')]
    # REMOVE: [State('animation-speed-3', 'value')]
)
def update_lineplot_3(selected_genres, n_intervals):  # Remove animation_speed parameter
    if not selected_genres:
        selected_genres = ['Overall']
    
    # Get your FULL data first to calculate fixed axis ranges
    genre_dfs = []
    if 'Overall' in selected_genres:
        genre_dfs.append(yearly_overall.assign(Genre='Overall'))
    
    for genre in selected_genres:
        if genre != 'Overall' and genre in genre_cols:
            temp = movies_df[movies_df[genre] == 1].groupby('year')['average_rating'].mean().reset_index()
            temp['Genre'] = genre
            genre_dfs.append(temp)
    
    full_df = pd.concat(genre_dfs, ignore_index=True)
    
    # Calculate fixed axis ranges from FULL data
    all_years = sorted(full_df['year'].unique())
    y_min = full_df['average_rating'].min() - 0.1  # Add small padding
    y_max = full_df['average_rating'].max() + 0.1
    x_min = min(all_years)
    x_max = max(all_years)
    
    # Calculate current frame
    current_frame = n_intervals % len(all_years)
    current_year = all_years[current_frame]
    
    # Filter data up to current frame for animation
    animated_df = full_df[full_df['year'] <= current_year]
    
    # Create the animated figure
    fig = px.line(
        animated_df,
        x='year',
        y='average_rating',
        color='Genre',
        markers=True,
        title=f"Average Movie Rating by Year (Up to {int(current_year)})",
        labels={'year': 'Release Year', 'average_rating': 'Average Rating'}
    )
    
    # FIXED AXIS RANGES
    fig.update_layout(
        xaxis_range=[x_min, x_max],  # Fixed x-axis range
        yaxis_range=[y_min, y_max],  # Fixed y-axis range
        template='plotly_dark',
        title_x=0.5,
        margin=dict(l=60, r=60, t=80, b=60),
        legend_title_text="Genre",
        hovermode="x unified"
    )
    
    # Add a vertical line at the current year
    fig.add_vline(
        x=current_year, 
        line_dash="dash", 
        line_color="white", 
        opacity=0.7
    )
    
    # Add current year annotation
    fig.add_annotation(
        x=current_year,
        y=y_max - 0.05,  # Position at top of y-axis
        text=f"Current: {current_year}",
        showarrow=True,
        arrowhead=2,
        bgcolor="white",
        bordercolor="black",
        font=dict(color="black")
    )
    
    fig.update_traces(
        line=dict(width=3), 
        marker=dict(size=6),
        mode='lines+markers'
    )
    
    return fig

# --- Callbacks for Page 4 ---
@callback(
    Output('page-4-visited', 'data'),
    Input('url', 'pathname')
)
def track_page_visit(pathname):
    if pathname == '/page-3':
        return True
    return False

@app.callback(
    [Output('rating-scatter-4', 'figure'),
     Output('pareto-chart-4', 'figure')],
    [Input('page-4-visited', 'data'),
     Input('scatter-genre-dropdown-4', 'value')]  # Now receives a string, not list
)
def update_top_graphs_4(page_visited, selected_genre):  # Changed parameter name (singular)
    if not page_visited:
        return dash.no_update, dash.no_update

    # --- 1. SCATTER PLOT (Simplified Logic for Single Selection) ---
    if selected_genre == 'Overall' or not selected_genre:
        # Case: Overall selected or nothing -> Show everything
        scatter_df = df.copy()
        title_text = "Avg Rating vs Count (Overall)"
    else:
        # Case: Specific genre selected -> Show ONLY movies of that genre
        mask = df[selected_genre] == 1  # Assuming your genre columns are 0/1 flags
        scatter_df = df[mask]
        title_text = f"Avg Rating vs Count ({selected_genre})"

    # Aggregate data (your existing code)
    movie_stats = scatter_df.groupby('title').agg({'rating': ['mean', 'count']}).reset_index()
    movie_stats.columns = ['title', 'avg_rating', 'rating_count']

    scatter_fig = px.scatter(
        movie_stats,
        x='rating_count',
        y='avg_rating',
        hover_name='title',
        trendline='ols',
        color='avg_rating',
        color_continuous_scale='Plasma',
        title=title_text
    )

    scatter_fig.update_layout(
        height=600,
        xaxis_title='Number of Ratings',
        yaxis_title='Average Rating',
        template='plotly_dark',
        title_x=0.5,
        uirevision='fixed'
    )

    # Create pareto chart (static - doesn't change)
    user_counts = df.groupby('userId')['rating'].count().sort_values(ascending=False).reset_index()
    user_counts.columns = ['userId', 'num_ratings']

    user_counts['cum_users'] = (user_counts.index + 1) / len(user_counts) * 100
    user_counts['cum_ratings'] = user_counts['num_ratings'].cumsum() / user_counts['num_ratings'].sum() * 100

    idx80 = user_counts[user_counts['cum_ratings'] >= 80].index.min()
    if pd.notna(idx80):
        pct_users_at_80 = user_counts.loc[idx80, 'cum_users']
        cum_at_point = user_counts.loc[idx80, 'cum_ratings']
    else:
        pct_users_at_80 = None
        cum_at_point = None

    pareto_fig = go.Figure()

    # Bars (ratings per user)
    pareto_fig.add_trace(go.Bar(
        x=user_counts['cum_users'],
        y=user_counts['num_ratings'],
        name='Ratings per User',
        marker=dict(color='skyblue', line=dict(width=0)),
        marker_color='skyblue',
        yaxis='y1',
        hovertemplate='Cumulative % users: %{x:.2f}%<br>Ratings: %{y}<extra></extra>'
    ))

    # Cumulative percent line (right axis)
    pareto_fig.add_trace(go.Scatter(
        x=user_counts['cum_users'],
        y=user_counts['cum_ratings'],
        name='Cumulative % of Ratings',
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='orange', width=3),
        marker=dict(size=6),
        hovertemplate='Cumulative % users: %{x:.2f}%<br>Cumulative % ratings: %{y:.2f}%<extra></extra>'
    ))

    # Vertical 20% line spanning entire plot (paper coordinates)
    pareto_fig.add_shape(
        type="line",
        x0=20, x1=20,
        xref='x',
        y0=0, y1=1,
        yref='paper',
        line=dict(color="white", dash="dot")
    )

    # Horizontal 80% line on the right y-axis
    pareto_fig.add_shape(
        type="line",
        x0=0, x1=100,
        xref='x',
        y0=80, y1=80,
        yref='y2',
        line=dict(color="white", dash="dot")
    )

    # Annotate the crossing point (where cum_ratings >= 80)
    if pct_users_at_80 is not None:
        pareto_fig.add_trace(go.Scatter(
            x=[pct_users_at_80],
            y=[cum_at_point],
            mode='markers+text',
            text=[f"({pct_users_at_80:.1f}%, {cum_at_point:.1f}%)"],
            textposition="top center",
            marker=dict(color="red", size=10, symbol='circle'),
            showlegend=False,
            yaxis='y2'
        ))

    pareto_fig.update_layout(
        height = 600,
        xaxis=dict(title='Cumulative % of Users', showgrid=False),
        yaxis=dict(title='Ratings per User', side='left', showgrid=False),
        yaxis2=dict(
            title='Cumulative % of Ratings',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        template='plotly_dark',
        title_x=0.5,
        legend=dict(x=0.7, y=0.9),
        margin=dict(l=50, r=60, t=80, b=50),
        uirevision='fixed'
    )

    return scatter_fig, pareto_fig

@callback(
    Output('violin-plot-4', 'figure'),
    [Input('genre-dropdown-4', 'value'),
     Input('page-4-visited', 'data')]
)
def update_violin_4(selected_genres, page_visited):
    if not page_visited:
        return dash.no_update, dash.no_update

    # Handle selection
    if not selected_genres:
        selected_genres = ['Overall']

    # Compute user activity
    user_activity = df.groupby('userId')['rating'].count().reset_index()
    user_activity.columns = ['userId', 'num_ratings']

    # Merge with main df
    merged = df.merge(user_activity, on='userId', how='left')

    # Define activity level bins
    merged['activity_level'] = pd.cut(
        merged['num_ratings'],
        bins=[0, 50, 200, np.inf],
        labels=['Low Activity (≤50)', 'Medium Activity (51-200)', 'High Activity (>200)']
    )

    dfs = []  # To store dataframes for each selected genre

    for genre in selected_genres:
        if genre == 'Overall':
            temp = merged.copy()
            temp['Genre'] = 'Overall'
        else:
            temp = merged[merged[genre] == 1].copy()
            temp['Genre'] = genre
        dfs.append(temp)

    combined = pd.concat(dfs)

    # Violin Plot
    fig = px.violin(
        combined,
        x='activity_level',
        y='rating',
        color='Genre',
        box=True,
        points=False,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_layout(
        height = 600,
        template='plotly_dark',
        xaxis_title='User Activity Level',
        yaxis_title='Rating',
        title_x=0.5,
        margin=dict(l=60, r=60, t=80, b=60),
        legend_title_text="Genre",
        uirevision='fixed',
        # --- ORDER ENFORCED HERE ---
        xaxis={
            'categoryorder': 'array',
            'categoryarray': ['Low Activity (≤50)', 'Medium Activity (51-200)', 'High Activity (>200)']
        }
    )


    return fig

# --- Callbacks for Page 5 ---
@callback(
    Output('wordcloud-image-5', 'src'),
    Input('url', 'pathname')
)
def update_wordcloud_5(pathname):
    if pathname == '/page-4':
        return generate_wordcloud_figure()
    return dash.no_update

# --- Callbacks for Page 6 ---
@callback(
    Output('genre-heatmap-6', 'figure'),
    Input('genre-dropdown-6', 'value'),
)
def update_heatmap_6(selected_genres):
    if not selected_genres or len(selected_genres) < 2:
        fig = px.imshow([[0]], text_auto=True, color_continuous_scale='RdBu')
        fig.update_layout(
            title="Select at least two genres to compute correlation",
            template='plotly_dark',
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False),
            margin=dict(l=50, r=50, t=70, b=50)
        )
        return fig

    corr_matrix = movies_df[selected_genres].corr().round(2)

    fig = px.imshow(
        corr_matrix,
        x=selected_genres,
        y=selected_genres,
        color_continuous_scale='RdBu',
        zmin=-1,
        zmax=1,
        text_auto=True,
        title=f"Correlation Matrix of Selected Genres"
    )

    fig.update_layout(
        template='plotly_dark',
        title_x=0.5,
        margin=dict(l=50, r=50, t=80, b=50),
        coloraxis_colorbar=dict(title="Correlation"),
        width=900,
        height=800
    )

    return fig


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8050, debug=True, use_reloader=False)