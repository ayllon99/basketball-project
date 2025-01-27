from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


def getting_sql_query(ti, table, player_id, task):
    """
    Construct an SQL INSERT query and prepare data for execution.

    This function builds an INSERT SQL query string and prepares the
    corresponding data values from a DataFrame pulled using Airflow's XCom
    system.

    Args:
        ti (TaskInstance): The Airflow TaskInstance object used to pull XCom
                           data.
        table (str): The name of the target database table.
        player_id (str): A unique identifier for the player.
        task (str): The task ID from which to pull the data.

    Returns:
        tuple: A tuple containing the constructed SQL query string and a list
        of data values to be used when executing the query.
    """
    df = ti.xcom_pull(task_ids=task, key=f'{player_id}_{table}')
    columns_sql = ', '.join([f'"{col}"' for col in df.columns])
    placeholders = ', '.join(['%s'] * len(df.columns))
    value_lists = [tuple(row) for row in df.values]
    query = f"""
        INSERT INTO {table} ({columns_sql})
        VALUES {', '.join(['(' + placeholders + ')'
                           for _ in range(len(value_lists))])
                }"""
    return query, [item for sublist in value_lists for item in sublist]


def inserting_players_info(ti, **op_kwargs):
    """
    Inserts new player information into the PostgreSQL database.

    Args:
        ti (TaskInstance): The task instance object.
        **op_kwargs: Additional keyword arguments containing the connection
                     details.

    Returns:
        None

    Note:
        This function pulls data from XCom, processes it, and executes SQL
        queries to upload the data to the specified PostgreSQL database.
    """
    postgres_connection = op_kwargs['postgres_connection']
    result = ti.xcom_pull(task_ids='read_db')
    players_ids = [a[0] for a in result]
    for player_id in players_ids:
        query, params = getting_sql_query(ti, 'players_info', player_id,
                                          'scraping_new_players')
        print(query, params)
        SQLExecuteQueryOperator(
            task_id="upload_to_postgres",
            conn_id=postgres_connection,
            sql=query,
            parameters=params,
            autocommit=True,
        ).execute(params)


def inserting_players_career_path(ti, **op_kwargs):
    """
    Inserts new player career path data into the database.

    This function retrieves data from an upstream task, processes it to extract
    player IDs, and then executes SQL queries to insert the career path
    information for each player into the Postgres database.

    Args:
        ti: TaskInstance object that provides access to task information and
            methods.
        **op_kwargs: Additional keyword arguments that are passed to the task.
                     Must include a 'postgres_connection' key containing the
                     connection ID for the Postgres database.

    Returns:
        None

    Side Effects:
        - Inserts new records into the players_career_path table in the
        Postgres database.
    """
    postgres_connection = op_kwargs['postgres_connection']
    result = ti.xcom_pull(task_ids='read_db')
    players_ids = [a[0] for a in result]
    for player_id in players_ids:
        query, params = getting_sql_query(ti, 'players_career_path', player_id,
                                          'scraping_new_players')
        print(query, params)
        SQLExecuteQueryOperator(
            task_id="upload_to_postgres",
            conn_id=postgres_connection,
            sql=query,
            parameters=params,
            autocommit=True,
        ).execute(params)


def inserting_players_stats_career(ti, **op_kwargs):
    """
    Inserts new player career statistics into the database.

    This function retrieves player data, constructs and executes SQL queries
    to upload the player statistics to a PostgreSQL database.

    Args:
        ti: The TaskInstance object from Airflow.
        **op_kwargs: Additional keyword arguments. Must contain
                     'postgres_connection' key with the connection ID for
                     PostgreSQL.

    Returns:
        None
    """
    postgres_connection = op_kwargs['postgres_connection']
    result = ti.xcom_pull(task_ids='read_db')
    players_ids = [a[0] for a in result]
    for player_id in players_ids:
        query, params = getting_sql_query(ti, 'players_stats_career',
                                          player_id, 'scraping_new_players')
        print(query, params)
        SQLExecuteQueryOperator(
            task_id="upload_to_postgres",
            conn_id=postgres_connection,
            sql=query,
            parameters=params,
            autocommit=True,
        ).execute(params)
