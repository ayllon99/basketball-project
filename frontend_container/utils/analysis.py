import pandas as pd
from datetime import datetime, timedelta
import psycopg2
from minio import Minio
from PIL import Image
import io
from utils.shootings import generate_image
from utils.variables import config
from utils.empty import *
from taipy.gui import notify, State


class PlayerScraper:
    """
    A class responsible for scraping player statistics from a database.

    This class provides methods to construct and execute a query,
    process the retrieved data,
    and return the processed statistics.
    The class interacts with a database and provides a way
    to retrieve player statistics based on specified conditions.

    Attributes:
        cur: A database cursor object.

    Methods:
        connect: Establishes a connection to the database.
        close_connection: Closes the database connection.
        _create_query: Constructs a query based on specified conditions.
        _get_query: Executes a query to retrieve data
                    and processes the results.
        _proccess_df: Processes a pandas DataFrame by applying
                      transformations to its columns.
        querying: Executes a query, processes the results,
                  and returns the processed data.
    """

    def __init__(self, stats_dict: dict, season: str, league: str) -> None:
        """
        Initializes the PlayerScraper class with the provided statistics
        dictionary, season, and league.

        Args:
            stats_dict (dict): A dictionary containing statistics data.
            season (str): The season for which the analysis is being performed.
            The first two characters are ignored.
            league (str): The league for which the analysis is being performed.

        Attributes:
            postgres_database (str): The name of the PostgreSQL database.
            postgres_host (str): The host of the PostgreSQL database.
            postgres_user (str): The username for the PostgreSQL database.
            postgres_pass (str): The password for the PostgreSQL database.
            conn (None): The database connection object (initialized as None).
            cur (None): The database cursor object (initialized as None).
            stats_dict (dict): The provided statistics dictionary.
            season (str): The season for which the analysis is being performed
                          (with the first two characters removed).
            league (str): The league for which the analysis is being performed.
        """
        # Variables to access to data
        self.postgres_database = config['postgres_database']
        self.postgres_host = config['postgres_host']
        self.postgres_user = config['postgres_user']
        self.postgres_pass = config['postgres_pass']
        self.conn = None
        self.cur = None
        # Data
        # Players shown have played at least 1 match
        if stats_dict['n_matches'] is None:
            stats_dict['n_matches'] = 1
        self.stats_dict = stats_dict
        self.season = season[2:]
        self.league = league

    def connect(self) -> None:
        """
        Connects to the PostgreSQL database.

        Uses the psycopg2 library to establish a connection
        to the PostgreSQL database.
        """
        self.conn = psycopg2.connect(
            dbname=self.postgres_database,
            host=self.postgres_host,
            user=self.postgres_user,
            password=self.postgres_pass
        )
        self.cur = self.conn.cursor()

    def close_connection(self) -> None:
        """
        Closes the connection to the PostgreSQL database.

        Closes the cursor and connection objects to free up system resources.
        """
        self.cur.close()
        self.conn.close()

    def _create_query(self) -> tuple[str, str, list]:
        """
        Creates a query based on the provided statistics dictionary.

        This function constructs a SQL query by iterating over the
        statistics dictionary
        and adding conditions for each non-null value. It also handles
        the 'min_avg' key separately, converting it to a timedelta object.

        Args:
            None (uses instance variables: self.stats_dict,
                  self.season, self.league)

        Returns:
            tuple: A tuple containing three elements:
                - where_clause (str): The WHERE clause of the query
                                      as a string.
                - league_clause (str): The league clause of the query
                                       as a string.
                - params (list): A list of parameters to be used in the query.

        Notes:
            - The function assumes that the statistics dictionary contains
            keys that correspond to column names in the database table.
            - The 'min_avg' key is handled separately and is converted
            to a timedelta object.
        """
        if self.stats_dict['min_avg'] is not None and\
            ":" in self.stats_dict['min_avg']:
            minutes, seconds = self.stats_dict['min_avg'].split(':')
            clause = f"min_avg >= %s AND "
            min_param = timedelta(hours=0, minutes=minutes, seconds=seconds)
        elif self.stats_dict['min_avg'] is not None and\
            ":" not in self.stats_dict['min_avg']:
            minutes = int(self.stats_dict['min_avg'])
            clause = f"min_avg >= %s AND "
            min_param = timedelta(hours=0, minutes=minutes, seconds=0)
        else:
            clause = ''
            min_param = None

        stats_dict = {key: value for key, value in self.stats_dict.items()
                      if value is not None and key != 'min_avg'}

        query = " AND ".join(f"{key} >= %s" for key in stats_dict.keys())
        where_clause = clause + query
        params = list(stats_dict.values())
        params.insert(0, self.season)
        if where_clause:
            where_clause = "WHERE " + where_clause

        if min_param is not None:
            params.insert(1, min_param)

        if self.league is not None:
            league_clause = "WHERE pcp.league = %s"
            params.append(self.league)
        else:
            league_clause = ""
        print(where_clause, league_clause, params)
        return where_clause, league_clause, params

    def _get_query(self, where_clause: str, league_clause: str,
                   params: list) -> pd.DataFrame:
        """
        Execute a SQL query to retrieve player statistics from the database.

        This function constructs a SQL query using the provided `where_clause`
        and `league_clause` to filter the data. It then executes the query,
        fetches the results, and returns them as a pandas DataFrame.

        Parameters
        ----------
        where_clause : str
            A SQL WHERE clause to filter the data in the `stats_table` CTE.
        league_clause : str
            A SQL clause to filter the data in the `stats_path_table`
            CTE based on the league.
        params : list
            A list of parameters to be used in the SQL query.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the player statistics.

        Notes
        -----
        The query uses three Common Table Expressions (CTEs): `temporal`,
        `stats_table`, and `stats_path_table`.
        The `temporal` CTE calculates the average statistics for each player
        in each season.
        The `stats_table` CTE applies the `where_clause` filter to the
        `temporal` CTE.
        The `stats_path_table` CTE joins the `stats_table` CTE with the
        `players_career_path` table and applies the `league_clause` filter.
        The final query selects the desired columns from the `stats_path_table`
        CTE and joins it with the `players_info` table to get the player names.
        """
        full_query = f"""
            WITH temporal AS(
                SELECT season, player_id,
                SUM(n_matches) AS n_matches,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN '00:00'
                    WHEN SUM(n_matches)!=0
                        THEN DATE_TRUNC('second', '00:00:00' +
                                        (SUM(EXTRACT(EPOCH FROM min_avg)
                                            * n_matches) / SUM(n_matches))
                                        * INTERVAL '1 second')
                END AS min_avg,
                CASE
                WHEN SUM(n_matches)=0
                        THEN 0
                WHEN SUM(n_matches)!=0
                        THEN SUM(points_avg*n_matches)/SUM(n_matches)
                END AS points_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(twos_in_avg*n_matches)/SUM(n_matches)
                END AS twos_in_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(twos_tried_avg*n_matches)/SUM(n_matches)
                END AS twos_tried_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(twos_perc*n_matches)/SUM(n_matches)
                END AS twos_perc,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(threes_in_avg*n_matches)/SUM(n_matches)
                END AS threes_in_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(threes_tried_avg*n_matches)/SUM(n_matches)
                END AS threes_tried_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(threes_perc*n_matches)/SUM(n_matches)
                END AS threes_perc,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(field_goals_in_avg*n_matches)/SUM(n_matches)
                END AS field_goals_in_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(field_goals_tried_avg*n_matches) /
                            SUM(n_matches)
                END AS field_goals_tried_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(field_goals_perc*n_matches)/SUM(n_matches)
                END AS field_goals_perc,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(free_throws_in_avg*n_matches)/SUM(n_matches)
                END AS free_throws_in_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(free_throws_tried_avg*n_matches) /
                            SUM(n_matches)
                END AS free_throws_tried_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(free_throws_perc*n_matches)/SUM(n_matches)
                END AS free_throws_perc,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(offensive_rebounds_avg*n_matches) /
                            SUM(n_matches)
                END AS offensive_rebounds_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(deffensive_rebounds_avg*n_matches) /
                            SUM(n_matches)
                END AS deffensive_rebounds_avg,
                CASE
                    WHEN SUM(n_matches)=0
                        THEN 0
                    WHEN SUM(n_matches)!=0
                        THEN SUM(total_rebounds_avg*n_matches)/SUM(n_matches)
                END AS total_rebounds_avg,
                CASE
                    WHEN SUM(n_matches)=0
                    THEN 0
                    WHEN SUM(n_matches)!=0
                    THEN SUM(assists_avg*n_matches)/SUM(n_matches)
                END AS assists_avg,
                CASE
                    WHEN SUM(n_matches)=0
                    THEN 0
                    WHEN SUM(n_matches)!=0
                    THEN SUM(turnovers_avg*n_matches)/SUM(n_matches)
                END AS turnovers_avg,
                CASE
                    WHEN SUM(n_matches)=0
                    THEN 0
                    WHEN SUM(n_matches)!=0
                    THEN SUM(blocks_favor_avg*n_matches)/SUM(n_matches)
                END AS blocks_favor_avg,
                CASE
                    WHEN SUM(n_matches)=0
                    THEN 0
                    WHEN SUM(n_matches)!=0
                    THEN SUM(blocks_against_avg*n_matches)/SUM(n_matches)
                END AS blocks_against_avg,
                CASE
                    WHEN SUM(n_matches)=0
                    THEN 0
                    WHEN SUM(n_matches)!=0
                    THEN SUM(dunks_avg*n_matches)/SUM(n_matches)
                END AS dunks_avg,
                CASE
                    WHEN SUM(n_matches)=0
                    THEN 0
                    WHEN SUM(n_matches)!=0
                    THEN SUM(personal_fouls_avg*n_matches)/SUM(n_matches)
                END AS personal_fouls_avg,
                CASE
                    WHEN SUM(n_matches)=0
                    THEN 0
                    WHEN SUM(n_matches)!=0
                    THEN SUM(fouls_received_avg*n_matches)/SUM(n_matches)
                END AS fouls_received_avg,
                CASE
                    WHEN SUM(n_matches)=0
                    THEN 0
                    WHEN SUM(n_matches)!=0
                    THEN SUM(efficiency_avg*n_matches)/SUM(n_matches)
                END AS efficiency_avg
                FROM players_stats_career
                WHERE season = %s
                GROUP BY season, player_id
                ORDER BY season, player_id DESC),
            stats_table AS(
                SELECT *
                FROM temporal
                {where_clause} ),
            stats_path_table AS(
                SELECT pcp.league,pcp.team_name,st.season,
                        st.player_id AS player_id,
                        st.n_matches,st.min_avg,
                        st.points_avg,st.twos_in_avg,
                        st.twos_tried_avg,st.twos_perc,
                        st.threes_in_avg,st.threes_tried_avg,
                        st.threes_perc,st.field_goals_in_avg,
                        st.field_goals_tried_avg,st.field_goals_perc,
                        st.free_throws_in_avg,st.free_throws_tried_avg,
                        st.free_throws_perc,st.offensive_rebounds_avg,
                        st.deffensive_rebounds_avg,st.total_rebounds_avg,
                        st.assists_avg,st.turnovers_avg,st.blocks_favor_avg,
                        st.blocks_against_avg,st.dunks_avg,
                        st.personal_fouls_avg,st.fouls_received_avg,st.efficiency_avg
                FROM stats_table AS st
                LEFT JOIN players_career_path AS pcp
                ON st.player_id = pcp.player_id AND st.season = pcp.season
                {league_clause})

            SELECT spt.player_id,player_name,season,team_name,n_matches,
                min_avg,points_avg,
                twos_in_avg,twos_tried_avg,twos_perc,threes_in_avg,
                threes_tried_avg,threes_perc,field_goals_in_avg,
                field_goals_tried_avg,field_goals_perc,free_throws_in_avg,
                free_throws_tried_avg,free_throws_perc,offensive_rebounds_avg,
                deffensive_rebounds_avg,total_rebounds_avg,assists_avg,
                turnovers_avg,blocks_favor_avg,blocks_against_avg,dunks_avg,
                personal_fouls_avg,fouls_received_avg,efficiency_avg
            FROM stats_path_table AS spt
            LEFT JOIN players_info as pi
            ON spt.player_id = pi.player_id
            """

        self.cur.execute(full_query, params)
        df = pd.DataFrame(self.cur.fetchall())
        df.columns = ['player_id', 'player_name', 'season', 'team_name',
                      'n_matches', 'min_avg', 'points_avg',
                      'twos_in_avg', 'twos_tried_avg', 'twos_perc',
                      'threes_in_avg', 'threes_tried_avg', 'threes_perc',
                      'field_goals_in_avg', 'field_goals_tried_avg',
                      'field_goals_perc', 'free_throws_in_avg',
                      'free_throws_tried_avg', 'free_throws_perc',
                      'offensive_rebounds_avg',	'deffensive_rebounds_avg',
                      'total_rebounds_avg', 'assists_avg', 'turnovers_avg',
                      'blocks_favor_avg', 'blocks_against_avg', 'dunks_avg',
                      'personal_fouls_avg', 'fouls_received_avg',
                      'efficiency_avg']
        return df

    def _proccess_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes a pandas DataFrame by applying various transformations
        to its columns.

        The transformations include:
        - Converting player names to uppercase
        - Converting the number of matches to integers
        - Formatting the average minutes played as a time string
        - Rounding various statistics to two decimal places

        Args:
            df (pd.DataFrame): The DataFrame to be processed

        Returns:
            pd.DataFrame: The processed DataFrame

        Notes:
            This function modifies the input DataFrame in-place and returns the
            modified DataFrame.
        """
        df['player_name'] = df['player_name'].apply(lambda x: x.upper())
        df['n_matches'] = df['n_matches'].apply(lambda x: int(x))
        df['min_avg'] = df['min_avg']\
            .apply(lambda x: (datetime(1900, 1, 1) + x).time()
                   .strftime("%M:%S"))
        df['points_avg'] = df['points_avg'].apply(lambda x: round(x, 2))
        df['twos_in_avg'] = df['twos_in_avg'].apply(lambda x: round(x, 2))
        df['twos_tried_avg'] = df['twos_tried_avg']\
            .apply(lambda x: round(x, 2))
        df['twos_perc'] = df['twos_perc'].apply(lambda x: round(float(x), 2))
        df['threes_in_avg'] = df['threes_in_avg'].apply(lambda x: round(x, 2))
        df['threes_tried_avg'] = df['threes_tried_avg']\
            .apply(lambda x: round(x, 2))
        df['threes_perc'] = df['threes_perc']\
            .apply(lambda x: round(float(x), 2))
        df['field_goals_in_avg'] = df['field_goals_in_avg']\
            .apply(lambda x: round(x, 2))
        df['field_goals_tried_avg'] = df['field_goals_tried_avg']\
            .apply(lambda x: round(x, 2))
        df['field_goals_perc'] = df['field_goals_perc']\
            .apply(lambda x: round(float(x), 2))
        df['free_throws_in_avg'] = df['free_throws_in_avg']\
            .apply(lambda x: round(x, 2))
        df['free_throws_tried_avg'] = df['free_throws_tried_avg']\
            .apply(lambda x: round(x, 2))
        df['free_throws_perc'] = df['free_throws_perc']\
            .apply(lambda x: round(float(x), 2))
        df['offensive_rebounds_avg'] = df['offensive_rebounds_avg']\
            .apply(lambda x: round(x, 2))
        df['deffensive_rebounds_avg'] = df['deffensive_rebounds_avg']\
            .apply(lambda x: round(x, 2))
        df['total_rebounds_avg'] = df['total_rebounds_avg']\
            .apply(lambda x: round(x, 2))
        df['assists_avg'] = df['assists_avg'].apply(lambda x: round(x, 2))
        df['turnovers_avg'] = df['turnovers_avg'].apply(lambda x: round(x, 2))
        df['blocks_favor_avg'] = df['blocks_favor_avg']\
            .apply(lambda x: round(x, 2))
        df['blocks_against_avg'] = df['blocks_against_avg']\
            .apply(lambda x: round(x, 2))
        df['dunks_avg'] = df['dunks_avg'].apply(lambda x: round(x, 2))
        df['personal_fouls_avg'] = df['personal_fouls_avg']\
            .apply(lambda x: round(x, 2))
        df['fouls_received_avg'] = df['fouls_received_avg']\
            .apply(lambda x: round(x, 2))
        df['efficiency_avg'] = df['efficiency_avg']\
            .apply(lambda x: round(x, 2))
        return df

    def querying(self) -> pd.DataFrame:
        """
        Executes a query to retrieve data, processes the results, and returns
        the processed data.

        The function connects to a database, constructs a query based on
        specified conditions, retrieves the data, processes it, and then closes
        the database connection.

        Returns:
            pandas.DataFrame: The processed data retrieved from the query.

        Notes:
            The query construction and data processing are handled by the
            `_create_query` and `_proccess_df` methods respectively.
        """
        self.connect()

        where_clause, league_clause, params = self._create_query()
        df = self._get_query(where_clause, league_clause, params)

        df_processed = self._proccess_df(df)

        self.close_connection()

        return df_processed


class SearchPlayer:
    """
    A class used to search for players and teams in a database.

    The SearchPlayer class provides methods to connect to a PostgreSQL
    database, retrieve team and player information, and close the database
    connection.

    Attributes:
    ----------
    postgres_database : str
        The name of the PostgreSQL database to connect to.
    postgres_host : str
        The host of the PostgreSQL database to connect to.
    postgres_user : str
        The username to use when connecting to the PostgreSQL database.
    postgres_pass : str
        The password to use when connecting to the PostgreSQL database.
    conn : psycopg2 connection object
        The connection object to the PostgreSQL database.
    cur : psycopg2 cursor object
        The cursor object to execute SQL queries on the PostgreSQL database.

    Methods:
    -------
    connect()
        Connects to the PostgreSQL database.
    close_connection()
        Closes the connection to the PostgreSQL database.
    on_change_season(league: str, season: str) -> tuple[dict, list]
        Retrieves a list of teams and their corresponding IDs for a given
        league and season.
    on_change_team(team_id: int) -> tuple[dict, list]
        Retrieves a list of player names and a dictionary mapping player names
        to IDs for a given team.
    """
    def __init__(self) -> None:
        """
        Initializes the SearchPlayer class.

        This method sets up the connection parameters for the PostgreSQL
        database, including the database name, host, username, and password.
        It also initializes the connection and cursor objects to None.

        Attributes:
        ----------
        postgres_database : str
            The name of the PostgreSQL database to connect to.
        postgres_host : str
            The host of the PostgreSQL database to connect to.
        postgres_user : str
            The username to use when connecting to the PostgreSQL database.
        postgres_pass : str
            The password to use when connecting to the PostgreSQL database.
        conn : psycopg2 connection object
            The connection object to the PostgreSQL database.
        cur : psycopg2 cursor object
            The cursor object to execute SQL queries on the PostgreSQL
            database.

        Returns:
        -------
        None
        """
        # Variables to access to data
        self.postgres_database = config['postgres_database']
        self.postgres_host = config['postgres_host']
        self.postgres_user = config['postgres_user']
        self.postgres_pass = config['postgres_pass']
        self.conn = None
        self.cur = None

    def connect(self) -> None:
        """
        Connects to the PostgreSQL database.

        Uses the psycopg2 library to establish a connection to the PostgreSQL
        database.
        """
        self.conn = psycopg2.connect(
            dbname=self.postgres_database,
            host=self.postgres_host,
            user=self.postgres_user,
            password=self.postgres_pass
        )
        self.cur = self.conn.cursor()

    def close_connection(self) -> None:
        """
        Closes the connection to the PostgreSQL database.

        Closes the cursor and connection objects to free up system resources.
        """
        self.cur.close()
        self.conn.close()

    def on_change_season(self, league: str, season: str) -> tuple[dict, list]:
        """
        Retrieves a list of teams and their corresponding IDs for a given
        league and season.

        Parameters
        ----------
        league : str
            The name of the league to query.
        season : str
            The season to query.

        Returns
        -------
        ids_dict : dict
            A dictionary mapping team names to their IDs, with the season.
        teams_list : list
            A sorted list of team names.

        Notes
        -----
        This function connects to a database, executes a SQL query to retrieve
        the team data,
        and then closes the connection. The query filters teams by the
        specified league and season.
        """
        self.connect()
        params = [league, season]
        self.cur.execute("""
                         SELECT DISTINCT team_id,team_name,season
                         FROM public.players_career_path
                         WHERE league = %s AND season = %s
                            """, params)
        df = pd.DataFrame(self.cur.fetchall())
        df.columns = ['team_id', 'team_name', 'season']
        teams_list = df['team_name'].tolist()
        df.set_index('team_name', inplace=True)
        ids_dict = df.to_dict()
        teams_list.sort()
        self.close_connection()
        return ids_dict, teams_list

    def on_change_team(self, team_id: int) -> tuple[dict, list]:
        """
        Retrieves a list of player names and a dictionary mapping player
        names to IDs for a given team.

        Args:
            team_id (int): The ID of the team for which to retrieve player
            information.

        Returns:
            tuple: A tuple containing:
                - player_ids_dict (dict): A dictionary mapping player names
                to IDs.
                - names_list (list): A list of player names.

        Notes:
            This function connects to a database, executes a SQL query to
            retrieve
            the required information, and then closes the database connection.
        """
        self.connect()
        params = [team_id]
        self.cur.execute("""
                         SELECT DISTINCT players_info.player_id,
                            players_info.player_name
                        FROM public.players_matches_stats AS stats
                        LEFT JOIN players_info
                            ON players_info.player_id = stats.player_id
                        WHERE stats.team_id = %s
                         AND players_info.player_name IS NOT NULL
                            """, params)
        df = pd.DataFrame(self.cur.fetchall())
        df.columns = ['player_id', 'player_name']
        names_list = df['player_name'].to_list()
        df.set_index('player_name', inplace=True)
        player_ids_dict = df.to_dict()
        self.close_connection()
        return player_ids_dict, names_list


class PlayerStats:
    """
    A class used to retrieve and process basketball player statistics from
    a database.

    The class provides methods to connect to the database, execute queries to
    fetch player statistics, process the retrieved data, and then close the
    database connection.

    Attributes:
    ----------
    cur : object
        A cursor object to execute SQL queries.

    Methods:
    -------
    connect()
        Establishes a connection to the database.
    close_connection()
        Closes the database connection.
    _get_stats_avg_query(params)
        Retrieves average statistics data from the database for a given player.
    _process_stats_avg(df)
        Processes and formats a Pandas DataFrame containing basketball team
        statistics.
    stats_avg_table()
        Retrieves and processes average statistics data from the database for a
        given player.
    """
    def __init__(self, player_id: int) -> None:
        """
        Initializes the PlayerStats class.

        Parameters:
        ----------
        player_id : int
            The ID of the player.

        Returns:
        -------
        None
        """
        # Variables to access to data
        self.conn = None
        self.cur = None
        self.postgres_database = config['postgres_database']
        self.postgres_host = config['postgres_host']
        self.postgres_user = config['postgres_user']
        self.postgres_pass = config['postgres_pass']
        self.minio_host = config['minio_host']
        self.minio_port = config['minio_port']
        self.minio_api_key = config['minio_api_key']
        self.minio_pass_key = config['minio_pass_key']
        self.bucket_name = config['bucket_name']
        # Player id
        self.player_id = player_id
        # Info
        self.player_name = None
        self.position = None
        self.age = None
        self.nationality = None
        # Path
        self.last_season = None
        self.last_league = None
        # Player image
        self.image_not_found_path = config['image_not_found_path']
        self.player_image_width = None
        self.player_image_height = None

    def connect(self) -> None:
        """
        Connects to the PostgreSQL database.

        Uses the psycopg2 library to establish a connection to the PostgreSQL
        database.
        """
        self.conn = psycopg2.connect(
            dbname=self.postgres_database,
            host=self.postgres_host,
            user=self.postgres_user,
            password=self.postgres_pass
        )
        self.cur = self.conn.cursor()

    def close_connection(self) -> None:
        """
        Closes the connection to the PostgreSQL database.

        Closes the cursor and connection objects to free up system resources.
        """
        self.cur.close()
        self.conn.close()

    def _get_info(self) -> pd.DataFrame:
        """Retrieves player information from the database.

        Args:
            None (uses the `self.player_id` attribute)

        Returns:
            pd.DataFrame: A DataFrame containing the player's information.

        Notes:
            This function queries the `public.players_info` table
            in the database.
        """
        params = [self.player_id]
        self.cur.execute("""
                         SELECT player_id, player_name, position, birthday,
                            nationality
                         FROM public.players_info
                         WHERE player_id = %s
                         """, params)
        df = pd.DataFrame(self.cur.fetchall())
        df.columns = ['player_id', 'player_name', 'position', 'birthday',
                      'nationality']
        return df

    def info(self, state: State) -> None:
        """
        Retrieves and updates the player's personal information.

        Attempts to connect to a database, fetch the player's data, and
        calculate their age.
        If successful, updates the object's attributes with the player's name,
        position, age, and nationality.
        If an error occurs, sets the object's attributes to 'Error' and sends
        a notification.

        Args:
            state: The current state of the application.

        Returns:
            None
        """
        try:
            self.connect()
            df = self._get_info()
            birthday = df.loc[0].birthday
            today = datetime.today()
            age = today.year - birthday.year - ((today.month, today.day) <
                                                (birthday.month, birthday.day))

            player_name = df.loc[0].player_name
            self.player_name = player_name.upper()
            self.position = df.loc[0].position
            self.age = age
            self.nationality = df.loc[0].nationality

            self.close_connection()
        except Exception:
            self.player_name = 'Error'
            self.position = 'Error'
            self.age = 'Error'
            self.nationality = 'Error'
            notify(state=state, notification_type='error',
                   message=f'Error getting personal data of this player')
        return

    def _get_path(self) -> pd.DataFrame:
        """
        Retrieves and processes the career path of a specific player,
        including seasons, leagues, teams, match statistics, and average
        efficiencies and minutes.

        Args:
        None explicitly. Uses class-level parameters:
        - `self.player_id` (integer): Unique identifier of the player
        in the database.

        Returns:
        - pd.DataFrame: DataFrame containing detailed career path information.

        Note: This method accesses database using psycopg, performing joins,
              group by, and order operations, implying reliance on pre-set
              connections (not shown in snippet).
        """
        params = [self.player_id, self.player_id, self.player_id]
        self.cur.execute("""
            SELECT season,league,team_name,n_matches, efficiency_avg, min_avg
            FROM(SELECT ROW_NUMBER()
                    OVER (PARTITION BY season,league,team_name,n_matches,
                         efficiency_avg,min_avg ORDER BY season,team_name)
                         AS r_number,*
                FROM(WITH pathh AS(SELECT
                                    substring(team_name,
                                              position('[' in team_name) + 1,
                                              position(']' in team_name) -
                                              position('[' in team_name) - 1)
                                    AS path_team_name,*
                                FROM players_career_path
                                WHERE player_id = %s)

                    SELECT stats.season AS season, league,
                         pathh.team_name AS team_name, n_matches,
                         efficiency_avg, min_avg
                    FROM(WITH temporal AS (SELECT season, team_name_extended,
                                            CONCAT(TRUNC(weighted,0),':',
                                             ROUND((MOD(weighted,1)
                                                * 60::integer),0))
                                            AS min_avg
                                    FROM(SELECT season, team_name_extended,
                                          SUM(ROUND((
                                               SPLIT_PART(
                                                min_total, ':', 1)::integer +
                                               SPLIT_PART(
                                                min_total, ':', 2)::integer /
                                                60::numeric)
                                               , 2)
                                             ) / SUM(n_matches) AS weighted
                                        FROM public.players_stats_career
                                        WHERE player_id = %s
                                        GROUP BY season,team_name_extended))

                        SELECT players_stats_career.season,
                            players_stats_career.team_name_extended,
                            SUM(n_matches) AS n_matches,
                            ROUND(SUM(efficiency_avg * n_matches)::numeric /
                             SUM(n_matches)::numeric,2) AS efficiency_avg,
                            temporal.min_avg
                        FROM players_stats_career
                        INNER JOIN temporal
                         ON temporal.season = players_stats_career.season AND
                          temporal.team_name_extended = players_stats_career.team_name_extended
                        WHERE player_id = %s
                        GROUP BY players_stats_career.season,
                         players_stats_career.team_name_extended,
                         temporal.min_avg
                        ORDER BY season DESC) AS stats
                    LEFT JOIN pathh
                         ON stats.season = pathh.season AND
                         (stats.team_name_extended = pathh.team_name OR
                           stats.team_name_extended = pathh.path_team_name)
                    )
                )
            WHERE r_number=1
            ORDER BY season DESC;
        """, params)
        df = pd.DataFrame(self.cur.fetchall())
        df.columns = ['season', 'league', 'team_name', 'n_matches',
                      'efficiency', 'min_avg']
        df['n_matches'] = df['n_matches'].apply(lambda x: int(x))
        df['efficiency'] = df['efficiency'].apply(lambda x: round(float(x), 2))
        return df

    def path(self, state: State) -> pd.DataFrame:
        """
        Retrieves the path data for a player and returns it as a pandas
        DataFrame.

        The path data includes information such as the season, league,
        team name, number of matches, efficiency, and minutes per match.

        Args:
            state: The current state of the application.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the path data.

        Raises:
            Exception: If an error occurs while connecting to the database or
                retrieving the path data. In this case, an error notification
                is sent and a failed table is returned.

        Notes:
            This function connects to the database, retrieves the path data,
            and then closes the connection. If an error occurs, it catches the
            exception, sends an error notification, and returns a failed table.
        """
        try:
            self.connect()
            df = self._get_path()

            # Column name displayed on the front
            df.columns = ['SEASON', 'LEAGUE', 'TEAM NAME', 'NUMBER OF MATCHES',
                          'EFFICIENCY', 'MINUTES PER MATCH']
            try:
                self.last_season = df.loc[0].SEASON
                self.last_league = df.loc[0].LEAGUE
            except Exception:
                self.last_season = '-'
                self.last_league = '-'

            self.close_connection()
        except Exception:
            df = table_fail()
            self.last_season = 'Error'
            self.last_league = 'Error'
            notify(state=state, notification_type='error',
                   message=f'Error getting path data of this player')
        return df

    def _get_player_image(self) -> tuple[bytes, int, int]:
        """
        Retrieves a player's image from a Minio bucket and resizes it if
        necessary.

        Returns:
            tuple: A tuple containing the image data, width, and height of
                   the image.

        Raises:
            Exception: If an error occurs while retrieving the image from
                       Minio.

        Notes:
            If the image is not found in the Minio bucket, a default image is
            used instead.
        """
        client = Minio(endpoint=f"{self.minio_host}:{self.minio_port}",
                       access_key=self.minio_api_key,
                       secret_key=self.minio_pass_key, secure=False)
        bucket_name = self.bucket_name
        object_name = f'{self.player_id}.png'
        try:
            response = client.get_object(bucket_name, object_name)
            image_data = response.read()
            image_stream = io.BytesIO(image_data)
            image = Image.open(image_stream)
            width, height = image.size
            height_limit = 250
            if height != height_limit:
                prop = round(height/width, 2)
                height = height_limit
                width = round(height/prop, 0)
        except Exception:
            print('IMAGE NOT FOUND')
            with open(self.image_not_found_path, 'rb') as f:
                image_data = f.read()
            image_stream = io.BytesIO(image_data)
            image = Image.open(image_stream)
            width, height = image.size
            width = f"{width}px"
            height = f"{height}px"
        return image_data, width, height

    def player_image(self) -> bytes:
        """
        Retrieves the player image data along with its dimensions.

        This method fetches the image data and its corresponding width and
        height.
        The image dimensions are stored as instance variables for later use.

        Returns:
            bytes: The raw image data of the player.

        Attributes:
            player_image_width (int): The width of the player image.
            player_image_height (int): The height of the player image.
        """
        image_data, width, height = self._get_player_image()
        self.player_image_width = width
        self.player_image_height = height

        return image_data

    def _get_shooting_query(self) -> pd.DataFrame:
        """
        Retrieves shooting statistics for a specific player from the database.

        This function connects to the database, executes a SQL query to fetch
        shooting data for the given player, and returns the results as a pandas
        DataFrame.

        The query fetches the season, shooting location, success status,
        and total number of shots for each combination of these factors.
        The results are then grouped by season, shooting location, and success
        status, and ordered by season and shooting location in descending
        order.

        Args:
            None (player_id is an instance variable)

        Returns:
            pd.DataFrame: A DataFrame containing the shooting statistics for
            the player.
                The DataFrame has the following columns:
                    - season (str): The season in which the shots were taken.
                    - shoot_from (str): The location from which the shots were
                                        taken.
                    - success (bool): Whether the shots were successful.
                    - total (int): The total number of shots taken.
        """
        self.connect()
        params = [self.player_id]
        self.cur.execute("""
            SELECT season, shoot_from, success, COUNT(*)
            FROM shootings
            LEFT JOIN results
            ON shootings.match_id = results.match_id
            WHERE player_id = %s
            GROUP BY season, shoot_from, success
            ORDER BY season, shoot_from DESC
        """, params)
        df = pd.DataFrame(self.cur.fetchall())
        df.columns = ['season', 'shoot_from', 'success', 'total']
        self.close_connection()
        return df

    def _process_in_out_shootings(self, df: pd.DataFrame) -> dict:
        """
        Process in and out shootings data from a given DataFrame.

        This function iterates over each row in the DataFrame, checks the
        success status of each shot, and updates the corresponding statistics
        for the season and shooting location.

        Args:
            df (pd.DataFrame): A DataFrame containing shooting data with
            columns 'season', 'shoot_from', 'success', and 'total'.

        Returns:
            dict: A dictionary with season as the key and another dictionary
            as the value.
                The inner dictionary has shooting locations as keys and a
                dictionary with 'in' and 'out' counts as the value.

        Notes:
            The shooting locations are: 'Zone', 'Right Corner Three',
            'Right Corner Middle', 'Right Side Three', 'Right Side Middle',
            'Front Three', 'Front Middle', 'Left Side Three',
            'Left Side Middle', 'Left Corner Three', 'Left Corner Middle'.
        """
        stats = {}
        for year in df['season'].unique():
            stats[year] = {}
            stats[year]['Zone'] = {'in': 0, 'out': 0}
            stats[year]['Right Corner Three'] = {'in': 0, 'out': 0}
            stats[year]['Right Corner Middle'] = {'in': 0, 'out': 0}
            stats[year]['Right Side Three'] = {'in': 0, 'out': 0}
            stats[year]['Right Side Middle'] = {'in': 0, 'out': 0}
            stats[year]['Front Three'] = {'in': 0, 'out': 0}
            stats[year]['Front Middle'] = {'in': 0, 'out': 0}
            stats[year]['Left Side Three'] = {'in': 0, 'out': 0}
            stats[year]['Left Side Middle'] = {'in': 0, 'out': 0}
            stats[year]['Left Corner Three'] = {'in': 0, 'out': 0}
            stats[year]['Left Corner Middle'] = {'in': 0, 'out': 0}
        for row in range(len(df)):
            success = df.loc[row].success
            if success:
                stats[df.loc[row].season][df.loc[row].shoot_from]['in'] = \
                    df.loc[row].total
            else:
                stats[df.loc[row].season][df.loc[row].shoot_from]['out'] = \
                    df.loc[row].total
        return stats

    def _shooting_stats(self) -> tuple[dict, list]:
        """
        Retrieves and processes shooting statistics.

        This method fetches shooting data, organizes it by year, and calculates
        the number of shots attempted, made, and missed.

        Returns:
            tuple: A dictionary containing shooting statistics for each year
                   and a list of the most recent three years for which data is
                   available.

        Notes:
            The dictionary has the following structure:
                {
                    year: {
                        key: {
                            'in': number of shots made,
                            'out': number of shots missed,
                            'tried': total number of shots attempted
                        }
                    }
                }
            If no data is available, the method returns an empty dictionary and
                a list of the current year and the two preceding years.
        """
        df = self._get_shooting_query()
        dict_in_out = self._process_in_out_shootings(df)

        dict_shootings = {}
        for year, values in dict_in_out.items():
            new_values = {}
            for key, value in values.items():
                new_values[key] = {
                    'in': value['in'],
                    'out': value['out'],
                    'tried': value['in'] + value['out']
                }
            dict_shootings[year] = new_values
        keys = list(dict_shootings.keys())
        keys.sort(reverse=True)
        if len(keys) > 0:
            years = [keys[0], keys[0] - 1, keys[0] - 2]
        else:
            years = [datetime.today().year, datetime.today().year - 1,
                     datetime.today().year - 2]
        return dict_shootings, years

    def shootings_images(self) -> tuple[bytes, bytes, bytes]:
        """
        Generate images representing shooting statistics for each year.

        This function generates a list of images, where each image corresponds
        to the shooting statistics for a specific year. The images are then
        returned as bytes objects.

        Returns:
            tuple: A tuple containing the first three images as bytes objects.

        Notes:
            The number of images returned is fixed at three, regardless of the
            number of years in the statistics. If there are more than three
            years, only the first three will be returned.
        """
        dict_shootings, years = self._shooting_stats()
        images = []
        for year in years:
            fig = generate_image(dic_stats=dict_shootings, year=year)
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            images.append(buf)
        final_images = []
        for i, image_buffer in enumerate(images):
            final_images.append(image_buffer.getvalue())
            image_buffer.seek(0)
        image_1 = final_images[0]
        image_2 = final_images[1]
        image_3 = final_images[2]

        return image_1, image_2, image_3

    def _get_stats_total_query(self) -> pd.DataFrame:
        """
        Retrieves the total statistics for a player's career.

        This method executes a SQL query to fetch the total statistics for a
        player from the 'players_stats_career' table. The query groups the
        results by season, team name, and stage name, and orders them in
        descending order by season.

        Args:
            None (uses the `self.player_id` attribute)

        Returns:
            pd.DataFrame: A DataFrame containing the total statistics for
            the player.

        """
        params = [self.player_id]
        self.cur.execute("""
            SELECT season,
                   team_name_extended,
                   stage_name_extended,
                   SUM(n_matches) AS n_matches,
                   MIN(min_total) AS min_total,
                   SUM(points_total) AS points_total ,
                   SUM(twos_in_total) AS twos_in_total,
                   SUM(twos_tried_total) AS twos_tried_total,
                   CASE
                       WHEN SUM(twos_tried_total)=0
                         THEN 0
                       WHEN SUM(twos_tried_total)!=0
                         THEN SUM(twos_in_total) / SUM(twos_tried_total)
                   END AS twos_perc,
                   SUM(threes_in_total) AS threes_in_total,
                   SUM(threes_tried_total) AS threes_tried_total,
                   CASE
                       WHEN SUM(threes_tried_total)=0
                         THEN 0
                       WHEN SUM(threes_tried_total)!=0
                         THEN SUM(threes_in_total) / SUM(threes_tried_total)
                   END AS threes_perc,
                   SUM(field_goals_in_total) AS field_goals_in_total,
                   SUM(field_goals_tried_total) AS field_goals_tried_total,
                   CASE
                       WHEN SUM(field_goals_tried_total)=0
                         THEN 0
                       WHEN SUM(field_goals_tried_total)!=0
                         THEN SUM(field_goals_in_total) /
                            SUM(field_goals_tried_total)
                   END AS field_goals_perc,
                   SUM(free_throws_in_total) AS free_throws_in_total,
                   SUM(free_throws_tried_total) AS free_throws_tried_total,
                   CASE
                       WHEN SUM(free_throws_tried_total)=0
                         THEN 0
                       WHEN SUM(free_throws_tried_total)!=0
                         THEN SUM(free_throws_in_total) /
                            SUM(free_throws_tried_total)
                   END AS free_throws_perc,
                   SUM(offensive_rebounds_total) AS offensive_rebounds_total,
                   SUM(deffensive_rebounds_total)
                         AS deffensive_rebounds_total,
                   SUM(total_rebounds_total) AS total_rebounds_total,
                   SUM(assists_total) AS assists_total,
                   SUM(turnovers_total) AS turnovers_total,
                   SUM(blocks_favor_total) AS blocks_favor_total,
                   SUM(blocks_against_total) AS blocks_against_total,
                   SUM(dunks_total)AS dunks_total,
                   SUM(personal_fouls_total) AS personal_fouls_total,
                   SUM(fouls_received_total) AS fouls_received_total,
                   SUM(efficiency_total) AS efficiency_total
            FROM players_stats_career
            WHERE player_id = %s
            GROUP BY season,team_name_extended,stage_name_extended
            ORDER BY season DESC
        """, params)

        df = pd.DataFrame(self.cur.fetchall())
        df.columns = ['season', 'team_name_extended', 'stage_name_extended',
                      'n_matches', 'min_total', 'points_total',
                      'twos_in_total', 'twos_tried_total', 'twos_perc',
                      'threes_in_total', 'threes_tried_total',
                      'threes_perc', 'field_goals_in_total',
                      'field_goals_tried_total', 'field_goals_perc',
                      'free_throws_in_total', 'free_throws_tried_total',
                      'free_throws_perc', 'offensive_rebounds_total',
                      'deffensive_rebounds_total', 'total_rebounds_total',
                      'assists_total', 'turnovers_total',
                      'blocks_favor_total', 'blocks_against_total',
                      'dunks_total', 'personal_fouls_total',
                      'fouls_received_total', 'efficiency_total']

        return df

    def _process_stats_total(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes a pandas DataFrame containing team statistics by applying
        data type conversions and rounding where necessary.

        Parameters
        ----------
        df : pandas.DataFrame
            A DataFrame containing team statistics.

        Returns
        -------
        pandas.DataFrame
            The input DataFrame with data type conversions and rounding
            applied.
        """
        df['n_matches'] = df['n_matches'].apply(lambda x: int(x))
        df['points_total'] = df['points_total'].apply(lambda x: int(x))
        df['twos_in_total'] = df['twos_in_total'].apply(lambda x: int(x))
        df['twos_tried_total'] = df['twos_tried_total'] \
            .apply(lambda x: int(x))
        df['twos_perc'] = df['twos_perc']\
            .apply(lambda x: round(float(x), 2))
        df['threes_in_total'] = df['threes_in_total']\
            .apply(lambda x: int(x))
        df['threes_tried_total'] = df['threes_tried_total']\
            .apply(lambda x: int(x))
        df['threes_perc'] = df['threes_perc']\
            .apply(lambda x: round(float(x), 2))
        df['field_goals_in_total'] = df['field_goals_in_total']\
            .apply(lambda x: int(x))
        df['field_goals_tried_total'] = df['field_goals_tried_total']\
            .apply(lambda x: int(x))
        df['field_goals_perc'] = df['field_goals_perc']\
            .apply(lambda x: round(float(x), 2))
        df['free_throws_in_total'] = df['free_throws_in_total']\
            .apply(lambda x: int(x))
        df['free_throws_tried_total'] = df['free_throws_tried_total']\
            .apply(lambda x: int(x))
        df['free_throws_perc'] = df['free_throws_perc']\
            .apply(lambda x: round(float(x), 2))
        df['offensive_rebounds_total'] = df['offensive_rebounds_total']\
            .apply(lambda x: int(x))
        df['deffensive_rebounds_total'] = df['deffensive_rebounds_total']\
            .apply(lambda x: int(x))
        df['total_rebounds_total'] = df['total_rebounds_total']\
            .apply(lambda x: int(x))
        df['assists_total'] = df['assists_total'].apply(lambda x: int(x))\

        df['turnovers_total'] = df['turnovers_total'].apply(lambda x: int(x))
        df['blocks_favor_total'] = df['blocks_favor_total']\
            .apply(lambda x: int(x))
        df['blocks_against_total'] = df['blocks_against_total']\
            .apply(lambda x: int(x))
        df['dunks_total'] = df['dunks_total'].apply(lambda x: int(x))
        df['personal_fouls_total'] = df['personal_fouls_total']\
            .apply(lambda x: int(x))
        df['fouls_received_total'] = df['fouls_received_total']\
            .apply(lambda x: int(x))
        df['efficiency_total'] = df['efficiency_total']\
            .apply(lambda x: int(x))

        return df

    def stats_total_table(self) -> pd.DataFrame:
        """
        Retrieves and processes statistics data from the database to create a
        total statistics table.

        The function connects to the database, retrieves the data, processes it
        and then returns a pandas DataFrame with the statistics. The statistics
        table includes data on points, shots, field goals, free throws,
        rebounds, assists, turnovers, blocks, fouls and efficiency for a given
        season.

        Returns:
            pd.DataFrame: A pandas DataFrame with the processed statistics.
        """
        self.connect()
        df = self._get_stats_total_query()
        df_processed = self._process_stats_total(df)

        df_processed.columns = ['SEASON', 'TEAM_NAME_EXTENDED',
                                'STAGE_NAME_EXTENDED', 'N_MATCHES', 'MIN',
                                'POINTS', 'TWOS_IN', 'TWOS_TRIED',
                                'TWOS_PERC', 'THREES_IN', 'THREES_TRIED',
                                'THREES_PERC', 'FIELD_GOALS_IN',
                                'FIELD_GOALS_TRIED', 'FIELD_GOALS_PERC',
                                'FREE_THROWS_IN', 'FREE_THROWS_TRIED',
                                'FREE_THROWS_PERC', 'OFFENSIVE_REBOUNDS',
                                'DEFFENSIVE_REBOUNDS', 'TOTAL_REBOUNDS',
                                'ASSISTS', 'TURNOVERS', 'BLOCKS_FAVOR',
                                'BLOCKS_AGAINST', 'DUNKS', 'PERSONAL_FOULS',
                                'FOULS_RECEIVED', 'EFFICIENCY']
        self.close_connection()

        return df_processed

    def _get_stats_avg_query(self) -> pd.DataFrame:
        """
        Retrieves player career statistics averages from the database.

        The function queries the 'players_stats_career' table in the database
        to get the average statistics of a player over their career. It then
        fetches all the results and loads them into a pandas DataFrame for
        further analysis.

        Parameters:
        ----------
        self.player_id : int
            The unique ID of the player to retrieve statistics for.

        Returns:
        -------
        pd.DataFrame
            A DataFrame containing the average career statistics for the
            player, including season, team name, stage name, number of matches,
            and various averages (e.g. minutes played, points, twos attempted,
            threes attempted, rebounds, assists, etc.).
        """
        params = [self.player_id]
        self.cur.execute("""
            SELECT season,
                   team_name_extended,
                   stage_name_extended,
                   SUM(n_matches) AS n_matches,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN '00:00'
                       WHEN SUM(n_matches)!=0
                         THEN DATE_TRUNC('second', '00:00:00' +
                                         (SUM(EXTRACT(EPOCH FROM min_avg)
                                                * n_matches) / SUM(n_matches))
                                         * INTERVAL '1 second')
                   END AS min_avg,
                   CASE
                   WHEN SUM(n_matches)=0
                         THEN 0
                   WHEN SUM(n_matches)!=0
                         THEN SUM(points_avg*n_matches)/SUM(n_matches)
                   END AS points_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(twos_in_avg*n_matches)/SUM(n_matches)
                   END AS twos_in_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(twos_tried_avg*n_matches)/SUM(n_matches)
                   END AS twos_tried_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(twos_perc*n_matches)/SUM(n_matches)
                   END AS twos_perc,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(threes_in_avg*n_matches)/SUM(n_matches)
                   END AS threes_in_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(threes_tried_avg*n_matches)/SUM(n_matches)
                   END AS threes_tried_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(threes_perc*n_matches)/SUM(n_matches)
                   END AS threes_perc,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(field_goals_in_avg*n_matches)/SUM(n_matches)
                   END AS field_goals_in_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(field_goals_tried_avg*n_matches) /
                              SUM(n_matches)
                   END AS field_goals_tried_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(field_goals_perc*n_matches)/SUM(n_matches)
                   END AS field_goals_perc,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(free_throws_in_avg*n_matches)/SUM(n_matches)
                   END AS free_throws_in_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(free_throws_tried_avg*n_matches) /
                              SUM(n_matches)
                   END AS free_throws_tried_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(free_throws_perc*n_matches)/SUM(n_matches)
                   END AS free_throws_perc,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(offensive_rebounds_avg*n_matches) /
                              SUM(n_matches)
                   END AS offensive_rebounds_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(deffensive_rebounds_avg*n_matches) /
                              SUM(n_matches)
                   END AS deffensive_rebounds_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                         THEN 0
                       WHEN SUM(n_matches)!=0
                         THEN SUM(total_rebounds_avg*n_matches)/SUM(n_matches)
                   END AS total_rebounds_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                        THEN 0
                       WHEN SUM(n_matches)!=0
                        THEN SUM(assists_avg*n_matches)/SUM(n_matches)
                   END AS assists_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                        THEN 0
                       WHEN SUM(n_matches)!=0
                        THEN SUM(turnovers_avg*n_matches)/SUM(n_matches)
                   END AS turnovers_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                        THEN 0
                       WHEN SUM(n_matches)!=0
                        THEN SUM(blocks_favor_avg*n_matches)/SUM(n_matches)
                   END AS blocks_favor_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                        THEN 0
                       WHEN SUM(n_matches)!=0
                        THEN SUM(blocks_against_avg*n_matches)/SUM(n_matches)
                   END AS blocks_against_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                        THEN 0
                       WHEN SUM(n_matches)!=0
                        THEN SUM(dunks_avg*n_matches)/SUM(n_matches)
                   END AS dunks_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                        THEN 0
                       WHEN SUM(n_matches)!=0
                        THEN SUM(personal_fouls_avg*n_matches)/SUM(n_matches)
                   END AS personal_fouls_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                        THEN 0
                       WHEN SUM(n_matches)!=0
                        THEN SUM(fouls_received_avg*n_matches)/SUM(n_matches)
                   END AS fouls_received_avg,
                   CASE
                       WHEN SUM(n_matches)=0
                        THEN 0
                       WHEN SUM(n_matches)!=0
                        THEN SUM(efficiency_avg*n_matches)/SUM(n_matches)
                   END AS efficiency_avg
            FROM players_stats_career
            WHERE player_id = %s
            GROUP BY season, team_name_extended, stage_name_extended
            ORDER BY season DESC
            """, params)

        df = pd.DataFrame(self.cur.fetchall())
        df.columns = ['season', 'team_name_extended', 'stage_name_extended',
                      'n_matches', 'min_avg', 'points_avg', 'twos_in_avg',
                      'twos_tried_avg', 'twos_perc', 'threes_in_avg',
                      'threes_tried_avg', 'threes_perc', 'field_goals_in_avg',
                      'field_goals_tried_avg', 'field_goals_perc',
                      'free_throws_in_avg', 'free_throws_tried_avg',
                      'free_throws_perc', 'offensive_rebounds_avg',
                      'deffensive_rebounds_avg', 'total_rebounds_avg',
                      'assists_avg', 'turnovers_avg', 'blocks_favor_avg',
                      'blocks_against_avg', 'dunks_avg', 'personal_fouls_avg',
                      'fouls_received_avg', 'efficiency_avg']

        return df

    def _process_stats_avg(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processes and formats a Pandas DataFrame containing basketball
        team statistics.

        The function performs the following operations:
        - Converts 'n_matches' to integers
        - Converts 'min_avg' to a string in 'MM:SS' format
        - Rounds all other statistical columns to two decimal places

        Args:
            df (pandas.DataFrame): DataFrame containing basketball team
                                   statistics.

        Returns:
            pandas.DataFrame: The processed and formatted DataFrame.
        """
        df['n_matches'] = df['n_matches'].apply(lambda x: int(x))
        df['min_avg'] = df['min_avg']\
            .apply(lambda x: (datetime(1900, 1, 1) + x).time()
                   .strftime("%M:%S"))
        df['points_avg'] = df['points_avg'].apply(lambda x: round(x, 2))
        df['twos_in_avg'] = df['twos_in_avg'].apply(lambda x: round(x, 2))
        df['twos_tried_avg'] = df['twos_tried_avg']\
            .apply(lambda x: round(x, 2))
        df['twos_perc'] = df['twos_perc'].apply(lambda x: round(float(x), 2))
        df['threes_in_avg'] = df['threes_in_avg'].apply(lambda x: round(x, 2))
        df['threes_tried_avg'] = df['threes_tried_avg']\
            .apply(lambda x: round(x, 2))
        df['threes_perc'] = df['threes_perc']\
            .apply(lambda x: round(float(x), 2))
        df['field_goals_in_avg'] = df['field_goals_in_avg']\
            .apply(lambda x: round(x, 2))
        df['field_goals_tried_avg'] = df['field_goals_tried_avg']\
            .apply(lambda x: round(x, 2))
        df['field_goals_perc'] = df['field_goals_perc']\
            .apply(lambda x: round(float(x), 2))
        df['free_throws_in_avg'] = df['free_throws_in_avg']\
            .apply(lambda x: round(x, 2))
        df['free_throws_tried_avg'] = df['free_throws_tried_avg']\
            .apply(lambda x: round(x, 2))
        df['free_throws_perc'] = df['free_throws_perc']\
            .apply(lambda x: round(float(x), 2))
        df['offensive_rebounds_avg'] = df['offensive_rebounds_avg']\
            .apply(lambda x: round(x, 2))
        df['deffensive_rebounds_avg'] = df['deffensive_rebounds_avg']\
            .apply(lambda x: round(x, 2))
        df['total_rebounds_avg'] = df['total_rebounds_avg']\
            .apply(lambda x: round(x, 2))
        df['assists_avg'] = df['assists_avg'].apply(lambda x: round(x, 2))
        df['turnovers_avg'] = df['turnovers_avg'].apply(lambda x: round(x, 2))
        df['blocks_favor_avg'] = df['blocks_favor_avg']\
            .apply(lambda x: round(x, 2))
        df['blocks_against_avg'] = df['blocks_against_avg']\
            .apply(lambda x: round(x, 2))
        df['dunks_avg'] = df['dunks_avg'].apply(lambda x: round(x, 2))
        df['personal_fouls_avg'] = df['personal_fouls_avg']\
            .apply(lambda x: round(x, 2))
        df['fouls_received_avg'] = df['fouls_received_avg']\
            .apply(lambda x: round(x, 2))
        df['efficiency_avg'] = df['efficiency_avg']\
            .apply(lambda x: round(x, 2))

        return df

    def stats_avg_table(self) -> pd.DataFrame:
        """
        Retrieves and processes average statistics data from the database.

        This function connects to the database, executes a query to fetch
        average statistics, processes the retrieved data, and then closes
        the database connection.

        Returns:
            pandas.DataFrame: A DataFrame containing the processed average
            statistics data.

        Notes:
            - This function relies on the `_get_stats_avg_query` and
            `_process_stats_avg` methods to fetch and process the data,
            respectively.
            - The database connection is managed by the `connect` and
            `close_connection` methods.
        """
        self.connect()
        df = self._get_stats_avg_query()
        df_processed = self._process_stats_avg(df)

        df_processed.columns = ['SEASON', 'TEAM_NAME_EXTENDED',
                                'STAGE_NAME_EXTENDED', 'N_MATCHES', 'MIN',
                                'POINTS', 'TWOS_IN', 'TWOS_TRIED',
                                'TWOS_PERC', 'THREES_IN', 'THREES_TRIED',
                                'THREES_PERC', 'FIELD_GOALS_IN',
                                'FIELD_GOALS_TRIED', 'FIELD_GOALS_PERC',
                                'FREE_THROWS_IN', 'FREE_THROWS_TRIED',
                                'FREE_THROWS_PERC', 'OFFENSIVE_REBOUNDS',
                                'DEFFENSIVE_REBOUNDS', 'TOTAL_REBOUNDS',
                                'ASSISTS', 'TURNOVERS', 'BLOCKS_FAVOR',
                                'BLOCKS_AGAINST', 'DUNKS', 'PERSONAL_FOULS',
                                'FOULS_RECEIVED', 'EFFICIENCY']
        self.close_connection()

        return df_processed
