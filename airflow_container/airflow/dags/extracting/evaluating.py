from bs4 import BeautifulSoup as bs
import time
from selenium.webdriver.common.by import By
import json
from datetime import datetime, timedelta
from extracting.utils import browser


def check_page(driver, match_day):
    """
    Checks if all matches on a given page have been successfully extracted.

    Args:
        driver (webdriver): The Selenium webdriver object used to interact with the webpage.
        match_day (int): The match day to select from the dropdown menu.

    Returns:
        bool: True if all matches have been successfully extracted, False otherwise.

    Notes:
        This function assumes that the webpage has a specific structure, with a dropdown menu
        containing match days and a table of matches. It uses Selenium to select the match day
        and then parses the HTML of the page using BeautifulSoup to extract the match links.
    """
    driver.find_element(
        By.XPATH,
        f'/html/body/form/div[4]/div[2]/div[3]/select[3]/option[{match_day}]')\
            .click()
    time.sleep(2.5)
    soup = bs(driver.page_source, 'lxml')
    trs = soup.find_all(
        'div', {'class': 'responsive-scroll'})[0]\
        .find('tbody').find_all('tr')[1:]
    n_matches = []
    for tr in trs:
        try:
            tds = tr.find_all('td')
            home_score = int(tds[1].text.strip().split('-')[0])
            away_score = int(tds[1].text.strip().split('-')[1])
            match_link = tds[1].find('a').get('href')
            n_matches.append(match_link)
        except Exception:
            pass
    if len(n_matches) == len(trs):
        return True
    else:
        return False


def check_new_stages(driver, dates_left, url):
    """
    Checks for new stages on a webpage.

    Args:
        driver (object): The web driver used to access the webpage.
        dates_left (dict): A dictionary containing the existing stages.
        url (str): The URL of the webpage to check.

    Returns:
        tuple: A boolean indicating whether new stages were detected and a list
               of the new stage IDs.

    Notes:
        This function uses BeautifulSoup to parse the HTML content of the webpage.
    """
    driver.get(url)
    time.sleep(3)
    try:
        actual_stages = dates_left.keys()
    except Exception:
        actual_stages = []
    new_stages = bs(driver.page_source, 'lxml').find(
        'select', {'name':
                   '_ctl0:MainContentPlaceHolderMaster:gruposDropDownList'})\
        .find_all('option')
    new_stages_ids = []
    for new_stage in new_stages:
        new_stages_ids.append(new_stage.get('value'))
    new_detected = [stage_id for stage_id in new_stages_ids
                    if stage_id not in actual_stages]
    detected = True if len(new_detected) > 0 else False

    return detected, new_detected


def refresh_dates(driver, new_detected, dates_left, url, file_path):
    """
    Refreshes the dates for the given stages by scraping the webpage and
    updates the dates_left dictionary.

    Args:
        driver (webdriver): The webdriver instance used to navigate the
                            webpage.
        new_detected (list): A list of stage IDs to refresh dates for.
        dates_left (dict): A dictionary to store the refreshed dates for each
                           stage.
        url (str): The URL of the webpage to scrape.
        file_path (str): The file path to save the updated dates_left
                         dictionary.

    Returns:
        dict: The updated dates_left dictionary.

    Notes:
        This function uses BeautifulSoup to parse the HTML content of the
        webpage and extract the matchday dates.
        The extracted dates are then stored in the dates_left dictionary and
        saved to a file.
    """
    driver.get(url)
    time.sleep(3)
    for stage_id in new_detected:
        driver.find_element(By.CSS_SELECTOR, f"option[value='{stage_id}']")\
            .click()
        time.sleep(2)
        matchdays_list = bs(driver.page_source, 'lxml').find(
            'select',
            {'name':
             '_ctl0:MainContentPlaceHolderMaster:jornadasDropDownList'})\
            .find_all('option')
        dates_left[stage_id] = {matchday.text.split('(')[0]:
                                matchday.text.split('(')[1].replace(')', '')
                                for matchday in matchdays_list}

    with open(file_path, 'w') as file:
        json.dump(dates_left, file)

    return dates_left


def new_results(ti, **op_kwargs):
    """
    Extracts new results from a website and updates the file with the new
    results.

    Args:
        ti (TaskInstance): The task instance.
        **op_kwargs: Additional keyword arguments.
            - url (str): The URL of the website to extract results from.
            - file_path (str): The path to the file containing the dates to
                               scrape.

    Returns:
        bool: True if new results are found, False otherwise.
    """
    url = op_kwargs['url']
    file_path = op_kwargs['file_path']
    driver = browser.open_browser()
    with open(file_path, 'r') as file:
        a = file.read()
        a = a.replace("'", '"')
        if a != '':
            dates_left = json.loads(a)
        else:
            dates_left = {}

    detected, new_detected = check_new_stages(driver, dates_left, url)
    if detected:
        dates_left = refresh_dates(driver, new_detected,
                                   dates_left, url, file_path)

    dates_to_scrape_dict = {}
    for stage_id in dates_left.keys():
        dates_to_scrape = []
        for matchday, value in dates_left[stage_id].items():
            today = datetime.today()
            j = datetime.strptime(dates_left[stage_id][matchday], '%d/%m/%Y')
            if j + timedelta(3) < today:
                dates_to_scrape.append(j.strftime('%d/%m/%Y'))
        dates_to_scrape_dict[stage_id] = dates_to_scrape

    matches_ready = {}
    matches_to_delete = {}
    if len([value for key, sublist in dates_to_scrape_dict.items()
            for value in sublist]) > 1:

        time.sleep(1)
        driver.get(url)
        time.sleep(2.5)
        stages = bs(driver.page_source, 'lxml').find(
            'select', {
                'name':
                '_ctl0:MainContentPlaceHolderMaster:gruposDropDownList'})\
            .find_all('option')

        stages_ids = []
        for stage in stages:
            stages_ids.append(stage.get('value'))

        for stage_id in stages_ids:
            driver.find_element(By.CSS_SELECTOR,
                                f"option[value='{stage_id}']").click()
            time.sleep(3)
            matchdays = bs(driver.page_source, 'lxml').find(
                'select',
                {'name':
                 '_ctl0:MainContentPlaceHolderMaster:jornadasDropDownList'})\
                .find_all('option')

            dates_to_delete = []
            match_days = []
            for match_day in range(1, len(matchdays) + 1):
                matchday = driver.find_element(
                    By.XPATH,
                    f'/html/body/form/div[4]/div[2]/div[3]/select[3]/option[{match_day}]')\
                        .text
                matchday = matchday.replace(')', '')
                date = matchday.split('(')[1]
                if date in [value for key, sublist in
                            dates_to_scrape_dict.items()
                            for value in sublist]:
                    result = check_page(driver, match_day)
                    if result:
                        dates_to_delete.append(date)
                        match_days.append(match_day)
            matches_ready[stage_id] = match_days
            matches_to_delete[stage_id] = dates_to_delete

        new_dict = {}
        for key, jornadas in dates_left.items():

            if len(matches_to_delete[key]) > 0:
                new_dict[key] = {jornada: date
                                 for jornada, date in jornadas.items()
                                 if date not in matches_to_delete[key]}
            else:
                new_dict[key] = jornadas

        with open(file_path, 'w') as file:
            json.dump(new_dict, file)

        if len([value for key, sublist in matches_ready.items()
                for value in sublist]) > 0:
            stages_ids_ready = []
            for stage_id in matches_ready.keys():
                ti.xcom_push(key=f'{stage_id}_match_days',
                             value=matches_ready[stage_id])
                stages_ids_ready.append(stage_id)
            ti.xcom_push(key=f'groups', value=stages_ids_ready)
            driver.quit()
            return True
        else:
            driver.quit()
            return False
