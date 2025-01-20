import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from seleniumwire import webdriver
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


def getting_sql_query(ti):
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
    # Explicitly use 127.0.0.1 rather than localhost
    # if remote session is running locally.
    sw_options = {
        'addr': '0.0.0.0',
        'auto_config': False,
        'port': 35812
        }

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=airflow-container:35812')
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
