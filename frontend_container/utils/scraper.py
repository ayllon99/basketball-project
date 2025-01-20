from utils.show_data import new_player
from utils.analysis import PlayerScraper, SearchPlayer
from utils.empty import *
from taipy.gui import notify, State


# Player Scraping
def submit_stats(state: State) -> None:
    """
    Submits player statistics to be matched with existing players.

    This function takes in a state object containing player statistics and
    scrapes for players with matching or higher statistics.

    Args:
        state (object): An object containing player statistics, including:
            - n_matches (int): The number of matches.
            - min_avg (float): The minimum average.
            - points_avg (float): The average points scored.
            - twos_in_avg (float): The average two-pointers made.
            - twos_tried_avg (float): The average two-pointers attempted.
            - twos_perc (float): The percentage of two-pointers made.
            - threes_in_avg (float): The average three-pointers made.
            - threes_tried_avg (float): The average three-pointers attempted.
            - threes_perc (float): The percentage of three-pointers made.
            - field_goals_in_avg (float): The average field goals made.
            - field_goals_tried_avg (float): The average field goals attempted.
            - field_goals_perc (float): The percentage of field goals made.
            - free_throws_in_avg (float): The average free throws made.
            - free_throws_tried_avg (float): The average free throws attempted.
            - free_throws_perc (float): The percentage of free throws made.
            - offensive_rebounds_avg (float): The average offensive rebounds.
            - deffensive_rebounds_avg (float): The average defensive rebounds.
            - total_rebounds_avg (float): The average total rebounds.
            - assists_avg (float): The average assists.
            - turnovers_avg (float): The average turnovers.
            - blocks_favor_avg (float): The average blocks in favor.
            - blocks_against_avg (float): The average blocks against.
            - dunks_avg (float): The average dunks.
            - personal_fouls_avg (float): The average personal fouls.
            - fouls_received_avg (float): The average fouls received.
            - efficiency_avg (float): The average efficiency.
            - season_scraping (str): The season to scrape.
            - league_scraping (str): The league to scrape.

    Returns:
        None

    Raises:
        Exception: If an error occurs during the scraping process.

    Notes:
        This function uses the PlayerScraper class to perform the scraping.
        The scraped players are stored in the state object.
    """
    notify(state, notification_type='I',
           message='Matching players with those stats or higher')

    stats_dict = {
        'n_matches': state.n_matches,
        'min_avg': state.min_avg,
        'points_avg': state.points_avg,
        'twos_in_avg': state.twos_in_avg,
        'twos_tried_avg': state.twos_tried_avg,
        'twos_perc': state.twos_perc,
        'threes_in_avg': state.threes_in_avg,
        'threes_tried_avg': state.threes_tried_avg,
        'threes_perc': state.threes_perc,
        'field_goals_in_avg': state.field_goals_in_avg,
        'field_goals_tried_avg': state.field_goals_tried_avg,
        'field_goals_perc': state.field_goals_perc,
        'free_throws_in_avg': state.free_throws_in_avg,
        'free_throws_tried_avg': state.free_throws_tried_avg,
        'free_throws_perc': state.free_throws_perc,
        'offensive_rebounds_avg': state.offensive_rebounds_avg,
        'deffensive_rebounds_avg': state.deffensive_rebounds_avg,
        'total_rebounds_avg': state.total_rebounds_avg,
        'assists_avg': state.assists_avg,
        'turnovers_avg': state.turnovers_avg,
        'blocks_favor_avg': state.blocks_favor_avg,
        'blocks_against_avg': state.blocks_against_avg,
        'dunks_avg': state.dunks_avg,
        'personal_fouls_avg': state.personal_fouls_avg,
        'fouls_received_avg': state.fouls_received_avg,
        'efficiency_avg': state.efficiency_avg
    }

    season = state.season_scraping
    league = state.league_scraping

    player_scraper = PlayerScraper(stats_dict, season, league)

    try:
        players_scraped = player_scraper.querying()
        print(players_scraped)
        state.players_scraped = players_scraped
        state.scraper_instructions = 'Click a row to select the player'
        notify(state, notification_type='success',
               message='Some players found!')
    except Exception:
        state.players_scraped = players_scraped_init()
        state.scraper_instructions = 'No players with those stats were found'
        notify(state, notification_type='warning',
               message='No players with those stats were found')


def clear_button(state: State) -> None:
    """
    Resets all statistics in the given state to None.

    This function is used to clear all the calculated averages and percentages
    in the state object, effectively resetting it to its initial state.

    Args:
        state (object): The state object containing the statistics to be
        cleared.

    Returns:
        None
    """
    state.n_matches = None
    state.min_avg = None
    state.points_avg = None
    state.twos_in_avg = None
    state.twos_tried_avg = None
    state.twos_perc = None
    state.threes_in_avg = None
    state.threes_tried_avg = None
    state.threes_perc = None
    state.field_goals_in_avg = None
    state.field_goals_tried_avg = None
    state.field_goals_perc = None
    state.free_throws_in_avg = None
    state.free_throws_tried_avg = None
    state.free_throws_perc = None
    state.offensive_rebounds_avg = None
    state.deffensive_rebounds_avg = None
    state.total_rebounds_avg = None
    state.assists_avg = None
    state.turnovers_avg = None
    state.blocks_favor_avg = None
    state.blocks_against_avg = None
    state.dunks_avg = None
    state.personal_fouls_avg = None
    state.fouls_received_avg = None
    state.efficiency_avg = None


def scraper_triggered(state: State, var_name: str, payload: dict) -> None:
    """
    Triggers the scraper functionality when a player is selected.

    Args:
        state (Gui): The current state of the GUI application.
        var_name (str): The name of the variable associated with the scraper
                        trigger.
        payload (dict): A dictionary containing the index of the selected
                        player.

    Returns:
        None

    Notes:
        This function retrieves the player ID and name from the
        `players_scraped` table, notifies the user that the selected player is
        being analyzed, and then calls the `new_player` function to perform
        further analysis.
    """
    table = state.players_scraped
    player_id = int(table.loc[payload['index'], 'player_id'])
    player_name = table.loc[payload['index'], 'player_name']
    notify(state, notification_type='I',
           message=f'Analyzing selected player: {player_name}')
    new_player(state, player_id)


# Player Analysis
def league_function(state: State) -> None:
    """
    Resets and initializes the state object for a new league analysis.

    This function clears existing data from the state object, preparing it for
    a fresh analysis.
    The cleared data includes team lists, player lists, and various analysis
    results.

    Args:
        state (Gui): The state object to be reset and initialized.

    Returns:
        None
    """
    state.teams_list = []
    state.players_list = []
    state.season_analysis = None
    state.team_analysis = None
    state.player_analysis = None


def season_function(state: State) -> None:
    """
    Resets and updates the state with new team and player data based on the
    selected season.

    Retrieves team IDs and names for the specified league and season.

    Args:
        state (Gui): The current state of the GUI application.
        league (str): The selected league.
        season (str): The selected season (without the first two characters).
    Returns:
        None
    """
    state.teams_list = []
    state.players_list = []
    state.team_analysis = None
    state.player_analysis = None
    searching = SearchPlayer()
    league = state.league_analysis
    season = state.season_analysis[2:]

    team_ids_dict, teams_list = searching.on_change_season(league=league,
                                                           season=season)
    state.team_ids_dict = team_ids_dict
    state.teams_list = teams_list


def team_function(state: State) -> None:
    """
    Updates the player analysis and list based on the selected team.

    Args:
        state (Gui): The current state of the GUI application.

    Returns:
        None

    Notes:
        This function resets the player analysis, retrieves the team ID from
        the selected team, and then updates the player list and IDs dictionary
        using the SearchPlayer class.
    """
    state.player_analysis = None
    searching = SearchPlayer()
    team_ids_dict = dict(dict(state.team_ids_dict)['team_id'])
    team_selected = state.team_analysis
    team_id = team_ids_dict[team_selected]
    player_ids_dict, players_list = searching.on_change_team(team_id)
    state.players_list = players_list
    state.player_ids_dict = player_ids_dict


def player_function(state: State) -> None:
    """
    Initiates player analysis by retrieving the player ID and notifying the
    user.

    Args:
        state (Gui): The current state of the GUI, containing player analysis
        and ID data.

    Returns:
        None

    Notes:
        This function triggers a notification to the user and calls the
        `new_player` function to start the analysis.
    """
    player_name = state.player_analysis
    player_ids_dict = dict(dict(state.player_ids_dict)['player_id'])
    player_id = player_ids_dict[player_name]
    notify(state, notification_type='I',
           message='Analyzing selected player')
    new_player(state, player_id)
