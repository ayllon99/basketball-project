from utils.analysis import *
from utils.scraper import *
from utils.show_data import *
from utils.empty import *
from taipy.gui import State


def init(state: State) -> None:
    """
    Initializes the application with a default player.

    Args:
        state (Gui): The current state of the graphical user interface.

    Returns:
        None

    Notes:
        By default, the application is initialized with Marc Gasol's player ID
        (360978).
    """
    # Marc Gasol id by default ------------------------------------------------
    player_id = 360978
    new_player(state, player_id)


# Player Scraper default ------------------------------------------------------
season_scraping = "2023/24"
league_scraping = "LEB ORO"
n_matches = None
min_avg = None
points_avg = None
twos_in_avg = None
twos_tried_avg = None
twos_perc = None
threes_in_avg = None
threes_tried_avg = None
threes_perc = None
field_goals_in_avg = None
field_goals_tried_avg = None
field_goals_perc = None
free_throws_in_avg = None
free_throws_tried_avg = None
free_throws_perc = None
offensive_rebounds_avg = None
deffensive_rebounds_avg = None
total_rebounds_avg = None
assists_avg = None
turnovers_avg = None
blocks_favor_avg = None
blocks_against_avg = None
dunks_avg = None
personal_fouls_avg = None
fouls_received_avg = None
efficiency_avg = None

players_scraped = players_scraped_init()
scraper_instructions = ''
# Lists used in Scraper AND Analysis ------------------------------------------
leagues_list = ['LEB ORO', 'LEB PLATA', 'LIGA EBA']
seasons_list = ['2023/24', '2022/23', '2021/22', '2020/21', '2019/20',
                '2018/19', '2017/18', '2016/17', '2015/16']

# Player Analysis default -----------------------------------------------------
league_analysis = 'LEB ORO'
season_analysis = None
team_analysis = None
player_analysis = None
player_id_selected = None
teams_list = []
players_list = []

# Empty by default
team_ids_dict = ''
player_ids_dict = ''

# Player Analysis -------------------------------------------------------------
# Personal info + path
player_id = None
name = None
age = None
position = None
nationality = None

player_path = None

last_season = None
last_league = None

player_image = None
player_image_width = None
player_image_height = None


# Shootings
image_1, image_2, image_3 = None, None, None

# Table stats
stat_mode = None
player_stats_table = None

# Chart
list_of_stats = None
stats_columns = None
# Stat to show by default
stats_to_show = None
figg = None
