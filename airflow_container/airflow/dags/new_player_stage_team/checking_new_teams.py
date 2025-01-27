from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from selenium.webdriver.common.by import By
from ..extracting.utils import browser
from ..env_variables import *


def getting_sql_query(ti):
    """
    Retrieves scraped team data and constructs an SQL INSERT query.

    This function pulls data from the previous task in an Airflow DAG, 
    processes it into a structured format suitable for an SQL query, 
    and returns both the query string and the corresponding values.

    Args:
        ti (TaskInstance): The TaskInstance object from Airflow, used to pull
                           XCom data.

    Returns:
        tuple: A tuple containing:
            - str: The SQL INSERT query string.
            - list: A flattened list of values to be inserted into the
                    database.
    """
    df = ti.xcom_pull(task_ids='scraping_new_teams', key='teams_found')
    columns_sql = ', '.join([f'"{col}"' for col in df.columns])
    placeholders = ', '.join(['%s'] * len(df.columns))
    value_lists = [tuple(row) for row in df.values]
    query = f"""
        INSERT INTO teams ({columns_sql})
        VALUES {', '.join(['(' + placeholders + ')'
                           for _ in range(len(value_lists))])
                }"""
    return query, [item for sublist in value_lists for item in sublist]


def inserting_teams(ti, **op_kwargs):
    """
    Inserts new teams into the PostgreSQL database using the provided SQL query
    and parameters.

    Args:
        ti (TaskInstance): The TaskInstance object from Airflow.
        **op_kwargs: Additional keyword arguments containing the connection
                     details.
        
    The function retrieves the PostgreSQL connection from op_kwargs, constructs
    the SQL query and parameters, prints them for logging, and then executes
    the query using SQLExecuteQueryOperator with autocommit enabled.
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
    """
    Navigates through a series of websites to extract team information and
    updates the database.

    This function is part of an Airflow DAG workflow. It uses browser
    automation to scrape team data from multiple web pages, checks against
    existing team IDs, and updates the database with newly found teams.

    Args:
        ti (TaskInstance): The Airflow TaskInstance object used to pull and
        push data via XCom.
        **op_kwargs: Additional keyword arguments containing the URLs to
                    navigate:
            - url_primera (str): URL for the first division teams.
            - url_segunda (str): URL for the second division teams.
            - url_tercera (str): URL for the third division teams.

    Returns:
        None
            - This function does not return a value but pushes a DataFrame
            containing the found teams to XCom with the key 'teams_found'.

    Raises:
        Exception: If there is an error during browser navigation or data
                   extraction.

    Note:
        - The function uses Selenium for browser automation and BeautifulSoup
        for HTML parsing.
        - The browser instance is properly quit at the end of the function to
        clean up resources.
        - The resulting DataFrame contains columns for team_id, team_name, and
        year.
    """
    urls = [op_kwargs['url_primera'],
            op_kwargs['url_segunda'],
            op_kwargs['url_tercera']]
    driver = browser.open_browser()
    result = ti.xcom_pull(task_ids='read_db_teams')
    result = ['952224', '952044']
    team_ids_found = []
    team_names_found = []
    years = []
    for url in urls:
        driver.get(url)
        time.sleep(2.5)
        stages = bs(driver.page_source, 'lxml')\
            .find('select',
                  {'name':
                   '_ctl0:MainContentPlaceHolderMaster:gruposDropDownList'})\
            .find_all('option')
        for stage in range(1, len(stages)):
            driver.find_element(By.XPATH,
                                f'/html/body/form/div[4]/div[2]/div[3]/select[2]/option[{stage}]')\
                                    .click()
            time.sleep(3)
            rows = bs(driver.page_source, 'lxml')\
                .find('table',
                      {'id':
                       '_ctl0_MainContentPlaceHolderMaster_clasificacionDataGrid'})\
                .find_all('tr')[1:]
            team_ids = [row.find('a').get('href')
                        .replace(teams_link, '')
                        for row in rows if row.find('a').get('href')
                        .replace(teams_link, '')
                        in result]
            team_names = [row.find('a').text
                          for row in rows
                          if row.find('a').get('href')
                          .replace(teams_link, '')
                          in result]
            team_ids_found.extend(team_ids)
            team_names_found.extend(team_names)
            for id in team_ids:
                result.remove(id)

    years = [2024] * len(team_ids_found)
    df = pd.DataFrame({'team_id': team_ids_found,
                       'team_name': team_names_found,
                       'year': years})
    ti.xcom_push(key='teams_found', value=df)
    driver.quit()
