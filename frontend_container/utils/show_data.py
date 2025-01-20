import plotly.graph_objects
from taipy.gui import notify, State
import plotly.express as px
import plotly
from utils.analysis import *
from utils.processer import *
from utils.empty import *


def new_player(state: State, player_id: int) -> None:
    """
    Initializes a new player with the given ID and updates the GUI state.

    This function retrieves the player's stats, personal info, and images,
    and then updates the GUI state accordingly.
    It also handles exceptions and notifies the user if there are any errors.

    Args:
        state (Gui): The GUI state to be updated.
        player_id (int): The ID of the new player.

    Returns:
        None
    """
    # New player id
    state.player_id = player_id
    player_stats = PlayerStats(player_id)

    # Personal info + path ----------------------------------------------------
    player_stats.info(state)
    state.name = player_stats.player_name
    state.age = f'{player_stats.age} years old'
    state.position = player_stats.position
    state.nationality = player_stats.nationality

    state.player_path = player_stats.path(state)

    state.last_season = player_stats.last_season
    state.last_league = player_stats.last_league

    state.player_image = player_stats.player_image()
    state.player_image_height = player_stats.player_image_height
    state.player_image_width = player_stats.player_image_width

    # Shootings images ----------------------------------------------------
    image_1, image_2, image_3 = player_stats.shootings_images()

    state.image_1 = image_1
    state.image_2 = image_2
    state.image_3 = image_3

    # Table stats -------------------------------------------------------------
    # Stat mode return to default
    stat_mode = 'AVERAGE'
    state.stat_mode = stat_mode
    try:
        player_stats_table = player_stats.stats_avg_table()
        state.player_stats_table = player_stats_table
    except Exception:
        state.player_stats_table = table_fail()
        notify(state=state, notification_type='error',
               message=f"""Error getting {stat_mode
                                          .lower()} stats of this player""")
    # Chart -------------------------------------------------------------------
    try:
        list_of_stats = list(player_stats_table.columns)
        state.stats_columns = [x for x in list_of_stats if x not in
                               ['MIN', 'SEASON', 'TEAM_NAME_EXTENDED',
                                'STAGE_NAME_EXTENDED']]
        # Stat to show return to default
        stats_to_show = ['POINTS']
        state.stats_to_show = stats_to_show
        state.figg = create_fig(state, player_stats_table,
                                stats_to_show,
                                stat_mode)
    except Exception:
        state.stats_columns = []
        state.stats_to_show = []
        state.figg = chart_fail()


def on_mode(state: State) -> None:
    """
    Updates the player statistics table based on the current mode.

    Args:
        state (Gui): The current state of the GUI.

    Returns:
        None

    Raises:
        Exception: If an error occurs while retrieving player statistics.
    """
    player_id = state.player_id
    player_stats = PlayerStats(player_id)
    mode = state.stat_mode
    try:
        if mode == 'AVERAGE':
            state.player_stats_table = player_stats.stats_avg_table()

        elif mode == 'TOTAL':
            state.player_stats_table = player_stats.stats_total_table()

    except Exception:
        state.player_stats_table = table_fail()
        notify(state=state, notification_type='error',
               message=f'Error getting {mode.lower()} stats of this player')
    # Modify chart figure to show info with the current mode
    on_stats_selector(state)


def on_stats_selector(state: State) -> None:
    """
    Handles the selection of statistics to display.

    This function is triggered when the user selects new statistics to display.
    It retrieves the selected statistics, the current mode, and the player
    statistics table from the state.
    It then creates a new figure using the `create_fig` function and updates
    the state with the new figure.

    Args:
        state (object): The current state of the application, containing the
        selected statistics, mode, and player statistics table.

    Returns:
        None

    Raises:
        Exception: If an error occurs while creating the new figure, the error
        is caught and printed to the console.
        The state is then updated with a failed chart using the `chart_fail`
        function.
    """
    try:
        stats_to_show = state.stats_to_show
        mode = state.stat_mode
        df = state.player_stats_table

        state.figg = create_fig(state, df, stats_to_show, mode)
    except Exception as e:
        print('Error in on_selector ', e)
        state.figg = chart_fail()


def create_fig(state: State, df: pd.DataFrame, stats_to_show: list,
               stat_mode: str) -> plotly.graph_objs.Figure:
    """
    Creates a figure based on the provided data and statistics to show.

    Args:
        state (Gui): The current state of the GUI.
        df (pd.DataFrame): The DataFrame containing the data.
        stats_to_show (list): A list of statistics to show in the figure.
        stat_mode (str): The mode of the statistics, either 'AVERAGE' or
                         'TOTAL'.

    Returns:
        fig (plotly.graph_objs.Figure): A figure object representing the data.

    Raises:
        Exception: If an error occurs while creating the figure.

    Notes:
        If there is only one data point, a bar chart is created instead of a
        line chart.
        If an error occurs, a failure chart is returned and an error
        notification is sent.
    """
    try:
        if len(stats_to_show) > 1:
            stats = ', '.join([f'{col}' for col in stats_to_show])
        else:
            stats = stats_to_show[0]
        title = f'{stats} IN {stat_mode} BY SEASON'

        title = title.upper()
        if stat_mode == 'AVERAGE':
            dff = proccess_df_avg(df)
        elif stat_mode == 'TOTAL':
            dff = proccess_df_total(df)

        dff = dff.reset_index()
        dff = dff.sort_values("SEASON")

        if len(dff) > 1:
            fig = px.line(data_frame=dff, x='SEASON',
                          y=stats_to_show, title=title)
        else:
            season = dff.loc[0].SEASON
            title = f'{stats} IN {stat_mode} BY 20{season}'
            melted_df = pd.melt(dff, id_vars=[], value_vars=stats_to_show)
            fig = px.bar(data_frame=melted_df, x='variable', y='value',
                         title=title)
    except Exception as e:
        print(f'Error in create_fig in player: {state.player_id}', e)
        fig = chart_fail()
        notify(state=state, notification_type='error',
               message='Error creating chart for this player')
    return fig
