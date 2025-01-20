import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from seleniumwire import webdriver
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By


teams_link = 'https://baloncestoenvivo.feb.es/Equipo.aspx?i='


def getting_sql_query(ti):
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


def open_browser():
    # Address of the machine running Selenium Wire.
    # Explicitly use 127.0.0.1 rather than localhost if remote session is
    # running locally.
    sw_options = {
        'addr': '0.0.0.0',
        'auto_config': False,
        'port': 35811
        }

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=airflow-container:35811')
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Remote(
        command_executor="http://selenium-hub:4444",
        options=chrome_options,
        seleniumwire_options=sw_options
        )
    return driver


def navigating_website(ti, **op_kwargs):
    urls = [op_kwargs['url_primera'],
            op_kwargs['url_segunda'],
            op_kwargs['url_tercera']]
    driver = open_browser()
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
