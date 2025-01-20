import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from selenium.webdriver.common.by import By
from datetime import datetime
from extracting.utils import browser


teams_link = 'https://baloncestoenvivo.feb.es/Equipo.aspx?i='
matches_link = 'https://baloncestoenvivo.feb.es/Partido.aspx?p='


def matchday_scraper(soup, stage_id, category):
    match_ids = []
    home_team_ids = []
    away_team_ids = []
    stage_ids = []
    matchdays = []
    home_scores = []
    away_scores = []
    dates = []
    times = []
    match_links = []
    categories = []

    matchday = int(soup.find('h1', {'class': 'titulo-modulo'}).text.strip()
                   .replace('Resultados Jornada ', '')[:-12])
    trs = soup.find_all('div', {'class': 'responsive-scroll'})[0] \
        .find('tbody').find_all('tr')[1:]
    for tr in trs:
        try:
            tds = tr.find_all('td')
            home_team_id = int(tds[0].find_all('a')[0].get('href')
                               .replace(teams_link, ''))
            away_team_id = int(tds[0].find_all('a')[1].get('href')
                               .replace(teams_link, ''))

            home_score = int(tds[1].text.strip().split('-')[0])
            away_score = int(tds[1].text.strip().split('-')[1])

            match_link = tds[1].find('a').get('href')
            match_id = int(match_link.replace(matches_link, ''))
            try:
                date = datetime.strptime(tds[2].text.strip(), '%d/%m/%Y')\
                    .date()
            except Exception:
                date = datetime.strptime('01/01/1900', '%d/%m/%Y').date()
            try:
                time = datetime.strptime(tds[3].text.strip(), '%H:%M').time()
            except Exception:
                time = datetime.strptime('00:00', '%H:%M').time()

            match_ids.append(match_id)
            home_team_ids.append(home_team_id)
            away_team_ids.append(away_team_id)
            stage_ids.append(stage_id)
            matchdays.append(matchday)
            home_scores.append(home_score)
            away_scores.append(away_score)
            dates.append(date)
            times.append(time)
            match_links.append(match_link)
            categories.append(category)
        except Exception:
            print(f'Error in {tr}')

    df = pd.DataFrame({'match_id': match_ids,
                       'home_team_id': home_team_ids,
                       'away_team_id': away_team_ids,
                       'stage_id': stage_ids,
                       'matchday': matchdays,
                       'home_score': home_scores,
                       'away_score': away_scores,
                       'date': dates,
                       'time': times,
                       'match_link': match_links,
                       'category': categories})

    return df, match_links


def getting_sql_query(ti, match_day, stage_id):
    df = ti.xcom_pull(task_ids="scraping_results",
                      key=f"stage_id_{stage_id}_matchday_{match_day}_df_results")
    columns_sql = ", ".join([f'"{col}"' for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    value_lists = [tuple(row) for row in df.values]
    query = f"""\
        INSERT INTO results ({columns_sql}) \
        VALUES {', '.join(['(' + placeholders + ')'
                           for _ in range(len(value_lists))])}
    """
    return query, [item for sublist in value_lists for item in sublist]


def inserting_to_postgres(ti, **op_kwargs):
    postgres_connection = op_kwargs['postgres_connection']
    stages_ids = ti.xcom_pull(task_ids='evaluate_matchdays', key='groups')
    for stage_id in stages_ids:
        match_days = ti.xcom_pull(task_ids='evaluate_matchdays',
                                  key=f'{stage_id}_match_days')
        print(match_days)
        stage_id = int(stage_id)
        for match_day in match_days:
            query, params = getting_sql_query(ti, match_day, stage_id)
            print(query, params)
            SQLExecuteQueryOperator(
                task_id="upload_to_postgres",
                conn_id=postgres_connection,
                sql=query,
                parameters=params,
                autocommit=True,
            ).execute(params)


def results_scraper(ti, **op_kwargs):
    url = op_kwargs["url"]
    category = op_kwargs["category"]

    driver = browser.open_browser()
    time.sleep(1)

    driver.get(url)
    print(ti)

    stages_ids = ti.xcom_pull(task_ids="evaluate_matchdays", key="groups")
    for stage_id in stages_ids:
        match_days = ti.xcom_pull(task_ids="evaluate_matchdays",
                                  key=f"{stage_id}_match_days")
        print(f"{stage_id}_match_days")
        print(match_days)

        driver.find_element(By.CSS_SELECTOR, f"option[value='{stage_id}']")\
            .click()
        time.sleep(2)

        for match_day in match_days:
            driver.find_element(
                By.XPATH, f'/html/body/form/div[4]/div[2]/div[3]/select[3]/option[{match_day}]'
            ).click()
            time.sleep(3)

            soup = bs(driver.page_source, "lxml")

            results, match_links = matchday_scraper(soup, stage_id, category)
            ti.xcom_push(key=f"stage_id_{stage_id}_matchday_{match_day}_match_links",
                         value=match_links)
            ti.xcom_push(key=f"stage_id_{stage_id}_matchday_{match_day}_df_results",
                         value=results)

    driver.quit()
