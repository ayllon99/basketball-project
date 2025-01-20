import plotly
import plotly.express as px
import pandas as pd


def chart_fail() -> plotly.graph_objs.Figure:
    """
    Generates an empty line chart with an error message to be displayed when
    chart creation fails.

    Returns:
        fig (plotly.graph_objs.Figure): A Plotly figure object containing the
        error chart.
    """
    fig = px.line(data_frame=pd.DataFrame({}),
                  title='ERROR CREATING CHART')
    fig.update_layout(xaxis_title='ERROR CREATING CHART',
                      yaxis_title='ERROR CREATING CHART')
    return fig


def table_fail() -> pd.DataFrame:
    return pd.DataFrame({})


def players_scraped_init() -> pd.DataFrame:
    """
    Initializes an empty pandas DataFrame to store player statistics.

    The DataFrame contains columns for various player statistics, including:
    - Player identification (player_id, player_name)
    - Season and team information (season, team_name)
    - Game statistics (n_matches, min_avg, points_avg, etc.)
    - Shooting statistics (twos_in_avg, twos_tried_avg, twos_perc, etc.)
    - Rebounding statistics (offensive_rebounds_avg, deffensive_rebounds_avg,
                             total_rebounds_avg)
    - Playmaking statistics (assists_avg, turnovers_avg)
    - Defensive statistics (blocks_favor_avg, blocks_against_avg)
    - Miscellaneous statistics (dunks_avg, personal_fouls_avg,
                                fouls_received_avg, efficiency_avg)

    Returns:
        pd.DataFrame: An empty DataFrame with the specified columns.
    """
    df = pd.DataFrame({'player_id': [], 'player_name': [], 'season': [],
                       'team_name': [], 'n_matches': [], 'min_avg': [],
                       'points_avg': [], 'twos_in_avg': [],
                       'twos_tried_avg': [], 'twos_perc': [],
                       'threes_in_avg': [], 'threes_tried_avg': [],
                       'threes_perc': [], 'field_goals_in_avg': [],
                       'field_goals_tried_avg': [], 'field_goals_perc': [],
                       'free_throws_in_avg': [], 'free_throws_tried_avg': [],
                       'free_throws_perc': [], 'offensive_rebounds_avg': [],
                       'deffensive_rebounds_avg': [], 'total_rebounds_avg': [],
                       'assists_avg': [], 'turnovers_avg': [],
                       'blocks_favor_avg': [], 'blocks_against_avg': [],
                       'dunks_avg': [], 'personal_fouls_avg': [],
                       'fouls_received_avg': [], 'efficiency_avg': []})
    return df
