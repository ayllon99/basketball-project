from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


def getting_sql_query(ti, table, player_id, task):
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
