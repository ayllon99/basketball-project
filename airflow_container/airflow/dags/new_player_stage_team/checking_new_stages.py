import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from ..extracting.utils import browser


def getting_sql_query(ti):
    """
    Retrieves scraped stage data and constructs an SQL INSERT query.

    This function pulls the scraped stage data from the previous task,
    formats it into SQL-compatible strings, and prepares the values for
    insertion into the database.

    Args:
        ti: The TaskInstance object containing the context and
            information about the task execution.

    Returns:
        tuple: A tuple containing:
            - str: The formatted SQL INSERT query string
            - list: A flattened list of values to be inserted
    """
    df = ti.xcom_pull(task_ids='scraping_new_stages',
                      key='stages_found')
    columns_sql = ', '.join([f'"{col}"' for col in df.columns])
    placeholders = ', '.join(['%s'] * len(df.columns))
    value_lists = [tuple(row) for row in df.values]
    query = f"""
        INSERT INTO stages ({columns_sql})
        VALUES {', '.join(['(' + placeholders + ')'
                           for _ in range(len(value_lists))])
                }"""
    return query, [item for sublist in value_lists for item in sublist]


def inserting_stages(ti, **op_kwargs):
    """
    Inserts stages data into a PostgreSQL database table.

    This function serves as an Airflow task that executes a SQL query to insert
    new stages data.
    It retrieves the SQL query and parameters from the `getting_sql_query`
    function and executes it using Airflow's `SQLExecuteQueryOperator`.

    Args:
        ti (TaskInstance): The Airflow TaskInstance object.
        **op_kwargs: Additional keyword arguments passed to the Airflow
                     operator.
            - postgres_connection (str): The connection ID for the PostgreSQL
                                         database.

    Returns:
        None

    Raises:
        KeyError: If the required `postgres_connection` is not found in
                  `op_kwargs`.
    """
    postgres_connection = op_kwargs['postgres_connection']
    query, params = getting_sql_query(ti)
    print(query, params)
    SQLExecuteQueryOperator(
        task_id="upload_to_postgres",
        conn_id=postgres_connection,
        sql=query,
        parameters=params,
        autocommit=True
    ).execute(params)


def navigating_website(ti, **op_kwargs):
    """Navigates through a list of specified websites to extract stage
    information.

    This function uses a browser driver to visit each website, parse the HTML
    content, and extract stage IDs and names. It compares the found stages with
    a list of expected stage IDs and collects information for stages that
    match.

    Args:
        ti (TaskInstance): The task instance object from Airflow.
        **op_kwargs: Additional keyword arguments containing the URLs to visit.
            Expected keys are 'url_primera', 'url_segunda', and 'url_tercera'.

    Returns:
        None
    """
    urls = [op_kwargs['url_primera'],
            op_kwargs['url_segunda'],
            op_kwargs['url_tercera']]
    driver = browser.open_browser()
    result = ti.xcom_pull(task_ids='read_db_stages')
    stage_ids = []
    stage_names = []
    years = []
    for url in urls:
        driver.get(url)
        time.sleep(2.5)
        stages = bs(driver.page_source, 'lxml')\
            .find('select',
                  {'name':
                   '_ctl0:MainContentPlaceHolderMaster:gruposDropDownList'})\
            .find_all('option')
        stages_ids_found = [stage.get('value')
                            for stage in stages
                            if stage.get('value') in result]

        for stage_id in stages_ids_found:
            result.remove(stage_id)
            stage_ids.append(stage_id)
            stage_names.append([stage.text for stage in stages
                                if stage.get('value') == stage_id][0])
            years.append(2024)

    df = pd.DataFrame({'stage_id': stage_ids,
                       'stage_name': stage_names,
                       'year': years})
    ti.xcom_push(key='stages_found', value=df)
    driver.quit()
