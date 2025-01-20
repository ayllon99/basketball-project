from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


def getting_sql_query(ti, table, match_id):
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
