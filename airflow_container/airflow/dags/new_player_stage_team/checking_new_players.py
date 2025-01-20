import pandas as pd
from bs4 import BeautifulSoup as bs
import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from minio import Minio
import io


teams_link = 'https://baloncestoenvivo.feb.es/Equipo.aspx?i='


def open_browser():
    # Address of the machine running Selenium Wire.
    # Explicitly use 127.0.0.1 rather than localhost
    # if remote session is running locally.
    sw_options = {
        'addr': '0.0.0.0',
        'auto_config': False,
        'port': 35813
        }

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=airflow-container:35813')
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Remote(
        command_executor="http://selenium-hub:4444",
        options=chrome_options,
        seleniumwire_options=sw_options
        )
    return driver


def insert_player_image(driver, player_id, minio_api_key,
                        minio_pass_key, minio_bucket):
    photo_link = f'https://imagenes.feb.es/Foto.aspx?c={player_id}'
    for req in driver.requests:
        if req.url == photo_link:
            image_response = req.response.body
            content_length = int(req.response.headers.get('Content-Length'))
            break
    try:
        try:
            client = Minio(endpoint="minio:9000",
                           access_key=minio_api_key,
                           secret_key=minio_pass_key,
                           secure=False)
            print(client)
        except Exception as e:
            print('NO CLIENT ', e)
        object_name = f"{player_id}.png"
        file = io.BytesIO(image_response)
        print(file)
        print(minio_bucket, "------", object_name, "------", content_length)
        try:
            client.put_object(minio_bucket,
                              object_name,
                              data=file,
                              length=content_length)
            print('Image inserted')
        except Exception as e:
            print('Error putting object--- ', e)

    except Exception as e:
        print("Error inserting image into Minio ", e)


def info_table_scraper(info_table, player_id, player_name, player_link):
    divs = info_table.find_all('div')
    try:
        position = divs[2].find('span', {'class': 'string'})\
            .text.strip().replace('í', 'i')
    except Exception:
        position = None
    try:
        height = int(divs[3].find('span', {'class': 'string'})
                     .text.replace(' cm', ''))
    except Exception:
        height = None
    try:
        weight = int(divs[4].find('span', {'class': 'string'})
                     .text.replace(' Kg', ''))
    except Exception:
        weight = None
    try:
        birthday = datetime.strptime(divs[5].find('span', {'class': 'string'})
                                     .text[:10], '%d/%m/%Y').date()
    except Exception:
        birthday = None
    try:
        nationality = divs[6].find('span', {'class': 'string'}).text.strip()
    except Exception:
        nationality = None
    return pd.DataFrame({'player_id': [int(player_id)],
                         'player_name': [player_name],
                         'position': [position],
                         'height': [height],
                         'weight': [weight],
                         'birthday': [birthday],
                         'nationality': [nationality],
                         'player_link': [player_link]})


def career_path_scraper(career_path_table, player_id):
    trs = career_path_table.find('tbody').find_all('tr')[1:]
    player_ids = []
    seasons = []
    leagues = []
    team_ids = []
    team_names = []
    licenses = []
    dates_in = []
    dates_out = []
    for tr in trs:
        tds = tr.find_all('td')
        season = tds[0].text.strip()
        league = tds[1].text.strip()
        try:
            team_id = int(tds[2].find('a')
                          .get('href').replace(teams_link, ''))
        except Exception:
            team_id = None
        try:
            team_name = tds[2].text.strip()
            license = tds[3].text.strip()
        except Exception:
            team_name = None
            license = None
        try:
            date_in = datetime.strptime(tds[4].text.strip(), '%d/%m/%Y')\
                .date()
        except Exception:
            date_in = None
        try:
            date_out = datetime.strptime(tds[5].text.strip(), '%d/%m/%Y')\
                .date()
        except Exception:
            date_out = None
        player_ids.append(int(player_id))
        seasons.append(season)
        leagues.append(league)
        team_ids.append(team_id)
        team_names.append(team_name)
        licenses.append(license)
        dates_in.append(date_in)
        dates_out.append(date_out)
    return pd.DataFrame({'player_id': player_ids,
                         'season': seasons,
                         'league': leagues,
                         'team_id': team_ids,
                         'license': licenses,
                         'date_in': dates_in,
                         'date_out': dates_out})


def stats_scraper(totals_stats_table, player_id, season, team_name):
    player_ids = []
    seasons = []
    team_names = []
    stage_abbrevs = []
    stage_names = []
    ns_matches = []
    mins_total = []
    mins_avg = []
    points_totals = []
    points_avgs = []
    t2_in_totals = []
    t2_tried_totals = []
    t2_percs = []
    t2_in_avgs = []
    t2_tried_avgs = []
    t3_in_totals = []
    t3_tried_totals = []
    t3_percs = []
    t3_in_avgs = []
    t3_tried_avgs = []
    field_goals_in_totals = []
    field_goals_tried_totals = []
    field_goals_percs = []
    field_goals_in_avgs = []
    field_goals_tried_avgs = []
    free_throws_in_totals = []
    free_throws_tried_totals = []
    free_throws_percs = []
    free_throws_in_avgs = []
    free_throws_tried_avgs = []
    offensive_rebounds_totals = []
    offensive_rebounds_avgs = []
    deffensive_rebounds_totals = []
    deffensive_rebounds_avgs = []
    total_rebounds_totals = []
    total_rebounds_avgs = []
    assists_totals = []
    assists_avgs = []
    steals_totals = []
    steals_avgs = []
    turnovers_totals = []
    turnovers_avgs = []
    blocks_favor_totals = []
    blocks_favor_avgs = []
    blocks_against_totals = []
    blocks_against_avgs = []
    dunks_totals = []
    dunks_avgs = []
    personal_fouls_totals = []
    personal_fouls_avgs = []
    fouls_received_totals = []
    fouls_received_avgs = []
    efficiency_totals = []
    efficiency_avgs = []

    trs = totals_stats_table.find('tbody').find_all('tr')[2:-1]

    for tr in trs:
        try:
            separator = tr.get('class')[0]
        except Exception:
            separator = 'No'
        if separator == 'row-separator':
            season = tr.text.strip().split(':')[1].replace('. Equipo', '')\
                .strip()
            team_name = tr.text.strip().split(':')[2].strip()
        else:
            tds = tr.find_all('td')
            stage_abbrev = tds[0].text
            stage_name = tds[0].find('span').get('title')
            n_matches = int(tds[1].text.strip())
            min_total = tds[2].text
            result_seconds = ((int(min_total.split(':')[0]) * 60) +
                              int(min_total.split(':')[1])) / n_matches
            result_minutes = int(result_seconds // 60)
            result_seconds = int(result_seconds % 60)
            min_avg = datetime.strptime(f'{result_minutes}:{result_seconds}',
                                        '%M:%S').time()
            points_total = int(tds[3].text.replace(',', '.'))
            points_avg = round(points_total / n_matches, 2)
            t2_in_total = int(tds[4].text.split('-')[0])
            t2_tried_total = int(tds[4].text.split('-')[1])
            try:
                t2_perc = round(t2_in_total / t2_tried_total, 3)
            except Exception:
                t2_perc = 0
            t2_in_avg = round(t2_in_total / n_matches, 2)
            t2_tried_avg = round(t2_tried_total / n_matches, 2)
            t3_in_total = int(tds[5].text.split('-')[0])
            t3_tried_total = int(tds[5].text.split('-')[1])
            try:
                t3_perc = round(t3_in_total / t3_tried_total, 3)
            except Exception:
                t3_perc = 0
            t3_in_avg = round(t3_in_total / n_matches, 2)
            t3_tried_avg = round(t3_tried_total / n_matches, 2)
            field_goals_in_total = int(tds[6].text.split('-')[0])
            field_goals_tried_total = int(tds[6].text.split('-')[1])
            try:
                field_goals_perc = round(field_goals_in_total /
                                         field_goals_tried_total, 3)
            except Exception:
                field_goals_perc = 0
            field_goals_in_avg = round(field_goals_in_total / n_matches, 2)
            field_goals_tried_avg = round(field_goals_tried_total /
                                          n_matches, 2)
            free_throws_in_total = int(tds[7].text.split('-')[0])
            free_throws_tried_total = int(tds[7].text.split('-')[1])
            try:
                free_throws_perc = round(free_throws_in_total /
                                         free_throws_tried_total, 3)
            except Exception:
                free_throws_perc = 0
            free_throws_in_avg = round(free_throws_in_total / n_matches, 2)
            free_throws_tried_avg = round(free_throws_tried_total /
                                          n_matches, 2)
            offensive_rebounds_total = int(tds[8].text)
            offensive_rebounds_avg = round(offensive_rebounds_total /
                                           n_matches, 1)
            deffensive_rebounds_total = int(tds[9].text)
            deffensive_rebounds_avg = round(deffensive_rebounds_total /
                                            n_matches, 1)
            total_rebounds_total = offensive_rebounds_total + \
                deffensive_rebounds_total
            total_rebounds_avg = round(total_rebounds_total / n_matches, 1)
            assists_total = int(tds[11].text)
            assists_avg = round(assists_total / n_matches, 1)
            steals_total = int(tds[12].text)
            steals_avg = round(steals_total / n_matches, 1)
            turnovers_total = int(tds[13].text)
            turnovers_avg = round(turnovers_total / n_matches, 1)
            blocks_favor_total = int(tds[14].text)
            blocks_favor_avg = round(blocks_favor_total / n_matches, 1)
            blocks_against_total = int(tds[15].text)
            blocks_against_avg = round(blocks_against_total / n_matches, 1)
            dunks_total = int(tds[16].text)
            dunks_avg = round(dunks_total / n_matches, 1)
            personal_fouls_total = int(tds[17].text)
            personal_fouls_avg = round(personal_fouls_total / n_matches, 1)
            fouls_received_total = int(tds[18].text)
            fouls_received_avg = round(fouls_received_total / n_matches, 1)
            efficiency_total = int(tds[19].text)
            efficiency_avg = round(efficiency_total / n_matches, 1)

            player_ids.append(int(player_id))
            seasons.append(season)
            team_names.append(team_name)
            stage_abbrevs.append(stage_abbrev)
            stage_names.append(stage_name)
            ns_matches.append(n_matches)
            mins_total.append(min_total)
            mins_avg.append(min_avg)
            points_totals.append(points_total)
            points_avgs.append(points_avg)
            t2_in_totals.append(t2_in_total)
            t2_tried_totals.append(t2_tried_total)
            t2_percs.append(t2_perc)
            t2_in_avgs.append(t2_in_avg)
            t2_tried_avgs.append(t2_tried_avg)
            t3_in_totals.append(t3_in_total)
            t3_tried_totals.append(t3_tried_total)
            t3_percs.append(t3_perc)
            t3_in_avgs.append(t3_in_avg)
            t3_tried_avgs.append(t3_tried_avg)
            field_goals_in_totals.append(field_goals_in_total)
            field_goals_tried_totals.append(field_goals_tried_total)
            field_goals_percs.append(field_goals_perc)
            field_goals_in_avgs.append(field_goals_in_avg)
            field_goals_tried_avgs.append(field_goals_tried_avg)
            free_throws_in_totals.append(free_throws_in_total)
            free_throws_tried_totals.append(free_throws_tried_total)
            free_throws_percs.append(free_throws_perc)
            free_throws_in_avgs.append(free_throws_in_avg)
            free_throws_tried_avgs.append(free_throws_tried_avg)
            offensive_rebounds_totals.append(offensive_rebounds_total)
            offensive_rebounds_avgs.append(offensive_rebounds_avg)
            deffensive_rebounds_totals.append(deffensive_rebounds_total)
            deffensive_rebounds_avgs.append(deffensive_rebounds_avg)
            total_rebounds_totals.append(total_rebounds_total)
            total_rebounds_avgs.append(total_rebounds_avg)
            assists_totals.append(assists_total)
            assists_avgs.append(assists_avg)
            steals_totals.append(steals_total)
            steals_avgs.append(steals_avg)
            turnovers_totals.append(turnovers_total)
            turnovers_avgs.append(turnovers_avg)
            blocks_favor_totals.append(blocks_favor_total)
            blocks_favor_avgs.append(blocks_favor_avg)
            blocks_against_totals.append(blocks_against_total)
            blocks_against_avgs.append(blocks_against_avg)
            dunks_totals.append(dunks_total)
            dunks_avgs.append(dunks_avg)
            personal_fouls_totals.append(personal_fouls_total)
            personal_fouls_avgs.append(personal_fouls_avg)
            fouls_received_totals.append(fouls_received_total)
            fouls_received_avgs.append(fouls_received_avg)
            efficiency_totals.append(efficiency_total)
            efficiency_avgs.append(efficiency_avg)
    return pd.DataFrame({'player_id': player_ids,
                         'season': seasons,
                         'team_name_extended': team_names,
                         'stage_abbrev': stage_abbrevs,
                         'stage_name': stage_names,
                         'n_matches': ns_matches,
                         'min_total': mins_total,
                         'min_avg': mins_avg,
                         'points_total': points_totals,
                         'points_avg': points_avgs,
                         'twos_in_total': t2_in_totals,
                         'twos_tried_total': t2_tried_totals,
                         'twos_perc': t2_percs,
                         'twos_in_avg': t2_in_avgs,
                         'twos_tried_avg': t2_tried_avgs,
                         'threes_in_total': t3_in_totals,
                         'threes_tried_total': t3_tried_totals,
                         'threes_perc': t3_percs,
                         'threes_in_avg': t3_in_avgs,
                         'threes_tried_avg': t3_tried_avgs,
                         'field_goals_in_total': field_goals_in_totals,
                         'field_goals_tried_total': field_goals_tried_totals,
                         'field_goals_perc': field_goals_percs,
                         'field_goals_in_avg': field_goals_in_avgs,
                         'field_goals_tried_avg': field_goals_tried_avgs,
                         'free_throws_in_total': free_throws_in_totals,
                         'free_throws_tried_total': free_throws_tried_totals,
                         'free_throws_perc': free_throws_percs,
                         'free_throws_in_avg': free_throws_in_avgs,
                         'free_throws_tried_avg': free_throws_tried_avgs,
                         'offensive_rebounds_total': offensive_rebounds_totals,
                         'offensive_rebounds_avg': offensive_rebounds_avgs,
                         'deffensive_rebounds_total': deffensive_rebounds_totals,
                         'deffensive_rebounds_avg': deffensive_rebounds_avgs,
                         'total_rebounds_total': total_rebounds_totals,
                         'total_rebounds_avg': total_rebounds_avgs,
                         'assists_total': assists_totals,
                         'assists_avg': assists_avgs,
                         'turnovers_total': turnovers_totals,
                         'turnovers_avg': turnovers_avgs,
                         'blocks_favor_total': blocks_favor_totals,
                         'blocks_favor_avg': blocks_favor_avgs,
                         'blocks_against_total': blocks_against_totals,
                         'blocks_against_avg': blocks_against_avgs,
                         'dunks_total': dunks_totals,
                         'dunks_avg': dunks_avgs,
                         'personal_fouls_total': personal_fouls_totals,
                         'personal_fouls_avg': personal_fouls_avgs,
                         'fouls_received_total': fouls_received_totals,
                         'fouls_received_avg': fouls_received_avgs,
                         'efficiency_total': efficiency_totals,
                         'efficiency_avg': efficiency_avgs})


def navigating_website(ti, **op_kwargs):
    minio_api_key = op_kwargs['minio_key']
    minio_pass_key = op_kwargs['minio_pass_key']
    minio_bucket = op_kwargs['minio_bucket']

    driver = open_browser()
    result = ti.xcom_pull(task_ids='read_db_player')
    for a in result:
        player_id = a[0]
        link = a[1]
        try:
            driver.get(link)
            wait = WebDriverWait(driver, 2)
            waiting = wait.until(EC.presence_of_element_located(
                By.XPATH, "/html/body/form/div[4]/div[2]/div[3]/input[2]"))
            time.sleep(0.5)
            element = driver.find_element(
                By.XPATH, '/html/body/form/div[4]/div[2]/div[3]/input[2]')
            driver.execute_script("arguments[0].click()", element)
            print('Trajectory clicked')
            time.sleep(1)

            try:
                insert_player_image(driver,
                                    player_id,
                                    minio_api_key,
                                    minio_pass_key,
                                    minio_bucket)
            except Exception as e:
                print("Error in insert_player_image ", e)

            soup = bs(driver.page_source, 'lxml')
            player_name = soup.find('div', {'class': 'jugador'})\
                .find('div', {'class': 'nombre'}).text
            player_info_table = soup.find('div', {'class': 'info'})
            tables = soup.find_all('table')
            career_path_table = tables[0]
            totals_stats_table = tables[2]

            player_info = info_table_scraper(player_info_table,
                                             player_id, player_name, link)
            career_path = career_path_scraper(career_path_table, player_id)
            if len(career_path) == 1:
                season = career_path.loc[0].season
                team_name = career_path.loc[0].team_name
            else:
                season = '-'
                team_name = '-'
            stats = stats_scraper(totals_stats_table,
                                  player_id, season, team_name)

            ti.xcom_push(key=f'{player_id}_players_info',
                         value=player_info)
            ti.xcom_push(key=f'{player_id}_players_career_path',
                         value=career_path)
            ti.xcom_push(key=f'{player_id}_players_stats_career',
                         value=stats)
        except Exception as e:
            print(f'Error scraping {player_id}, {link}, {e}')
    driver.quit()
