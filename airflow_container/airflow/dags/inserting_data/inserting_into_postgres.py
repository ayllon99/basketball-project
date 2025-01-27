from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


def getting_sql_query(ti, table, match_id):
    """
    Constructs an SQL query for inserting data into a PostgreSQL table.
    
    Args:
        ti (TaskInstance): The TaskInstance object from Airflow.
        table (str): The name of the PostgreSQL table to insert data into.
        match_id (str): The identifier for the specific match data being
                        processed.
        
    Returns:
        tuple: A tuple containing:
            - str: The constructed SQL query string
            - list: A list of parameters to be used with the SQL query
            
    Example:
        For a DataFrame with columns 'id' and 'name', the generated query might
        look like:
            "INSERT INTO my_table ("id", "name") VALUES (%s, %s), (%s, %s)"
    """
    df = ti.xcom_pull(task_ids='scraping_match_info',
                      key=f'{match_id}_{table}')
    try:
        columns_sql = ', '.join([f'"{col}"' for col in df.columns])
        placeholders = ', '.join(['%s'] * len(df.columns))
        value_lists = [tuple(row) for row in df.values]
        query = f"""
            INSERT INTO {table} ({columns_sql})
            VALUES {', '.join(['(' + placeholders + ')'
                               for _ in range(len(value_lists))])
                    }"""
        params = [item for sublist in value_lists for item in sublist]
    except Exception:
        query = f'SELECT * FROM {table} LIMIT %s;'
        params = ['1']
    return query, params


def teams_match_stats_insert_data(ti, **op_kwargs):
    """
    Inserts team match statistics data into a PostgreSQL database for each
    match ID.

    Args:
        ti: The Airflow context task instance, used for XCom communication.
        **op_kwargs: Additional keyword arguments passed to the operator.
            - postgres_connection (str): The connection ID for the PostgreSQL
                                         database.

    Returns:
        None

    Raises:
        Exception: If there is an error executing the SQL query or retrieving
                   data.
    """
    postgres_connection = op_kwargs['postgres_connection']
    match_ids = ti.xcom_pull(task_ids='scraping_match_info',
                             key='match_ids')
    for match_id in match_ids:
        query, params = getting_sql_query(ti, 'teams_matches_stats', match_id)
        print(query, params)
        SQLExecuteQueryOperator(
            task_id="upload_to_postgres",
            conn_id=postgres_connection,
            sql=query,
            parameters=params,
            autocommit=True
        ).execute(params)


def match_partials_insert_data(ti, **op_kwargs):
    """
    Inserts partial match data into a PostgreSQL database.

    This function pulls match IDs from XCom, processes each match ID to get
    the corresponding SQL query and parameters, and executes the SQL query
    to insert the data into the database.

    Args:
        ti (TaskInstance): The TaskInstance object that holds the context
            and any returned XCom values from previous tasks.
        **op_kwargs: Additional keyword arguments that are passed to the
            operator. Must contain 'postgres_connection' key with the
            connection ID for PostgreSQL.

    Returns:
        None

    """
    postgres_connection = op_kwargs['postgres_connection']
    match_ids = ti.xcom_pull(task_ids='scraping_match_info', key='match_ids')
    for match_id in match_ids:
        query, params = getting_sql_query(ti, 'match_partials', match_id)
        params = [int(param) for param in params]
        print(query, params)
        SQLExecuteQueryOperator(
            task_id="upload_to_postgres",
            conn_id=postgres_connection,
            sql=query,
            parameters=params,
            autocommit=True
        ).execute(params)


def players_matches_stats_insert_data(ti, **op_kwargs):
    """
    Inserts player match statistics data into a Postgres database.

    This function is designed to be used within an Apache Airflow DAG.
    It retrieves match IDs from a previous task, generates the necessary SQL
    queries, and executes them to insert player statistics into the database.

    Args:
        ti (TaskInstance): The TaskInstance object from Airflow, used to pull
                           XCom values.
        **op_kwargs: Additional keyword arguments passed from the task context.
            - postgres_connection (str): The connection ID for the Postgres
                                         database.

    Returns:
        None

    """
    postgres_connection = op_kwargs['postgres_connection']
    match_ids = ti.xcom_pull(task_ids='scraping_match_info', key='match_ids')
    for match_id in match_ids:
        query, params = getting_sql_query(ti, 'players_matches_stats',
                                          match_id)
        print(query, params)
        SQLExecuteQueryOperator(
            task_id="upload_to_postgres",
            conn_id=postgres_connection,
            sql=query,
            parameters=params,
            autocommit=True
        ).execute(params)


def shootings_insert_data(ti, **op_kwargs):
    """
    Inserts shooting data into a Postgres database for each match.

    This function retrieves match IDs from an upstream task, constructs SQL
    queries, and executes them to insert the data into the appropriate database
    table.

    Args:
        ti (TaskInstance): The TaskInstance object from Airflow, used to
                           retrieve XCom values from previous tasks.
        **op_kwargs: Additional keyword arguments passed to the Airflow
                     operator, including the Postgres connection ID.

    Returns:
        None
    """
    postgres_connection = op_kwargs['postgres_connection']
    match_ids = ti.xcom_pull(task_ids='scraping_match_info', key='match_ids')
    for match_id in match_ids:
        query, params = getting_sql_query(ti, 'shootings', match_id)
        print(query, params)
        SQLExecuteQueryOperator(
            task_id="upload_to_postgres",
            conn_id=postgres_connection,
            sql=query,
            parameters=params,
            autocommit=True,
        ).execute(params)


def shooting_chart_availability_insert_data(ti, **op_kwargs):
    """
    Inserts shooting chart availability data into a Postgres database.

    This function pulls match IDs from XCom, generates the necessary SQL
    queries, and executes them to upload the data into the appropriate tables.

    Args:
        ti: The TaskInstance object used to pull and push data from XCom.
        **op_kwargs: Additional keyword arguments containing the Postgres
                     connection ID.
    Returns:
        None
    """
    postgres_connection = op_kwargs['postgres_connection']
    match_ids = ti.xcom_pull(task_ids='scraping_match_info', key='match_ids')
    for match_id in match_ids:
        query, params = getting_sql_query(ti, 'shooting_chart_availability',
                                          match_id)
        print(query, params)
        SQLExecuteQueryOperator(
            task_id="upload_to_postgres",
            conn_id=postgres_connection,
            sql=query,
            parameters=params,
            autocommit=True
        ).execute(params)
