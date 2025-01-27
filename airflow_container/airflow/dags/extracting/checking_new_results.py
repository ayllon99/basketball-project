from bs4 import BeautifulSoup as bs
import time
from selenium.webdriver.common.by import By
import json
from datetime import datetime, timedelta
from extracting.utils import browser


def check_page(driver, match_day):
    """Checks a webpage for new match results.

    Args:
        driver (object): The webdriver used to interact with the webpage.
        match_day (int): The match day to select on the webpage.

    Returns:
        bool: Whether all matches on the page have been successfully extracted.

    """
    driver.find_element(
        By.XPATH,
        f'/html/body/form/div[4]/div[2]/div[3]/select[3]/option[{match_day}]')\
        .click()
    time.sleep(2.5)
    soup = bs(driver.page_source, 'lxml')
    trs = soup.find_all('div', {'class': 'responsive-scroll'})[0]\
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
        driver (object): The web driver object used to navigate the webpage.
        dates_left (dict): A dictionary containing the current stages and their
                           corresponding dates.
        url (str): The URL of the webpage to check for new stages.

    Returns:
        tuple: A tuple containing two values:
            - detected (bool): True if new stages are detected, else False.
            - new_detected (list): A list of IDs of the new stages detected.

    """
    driver.get(url)
    time.sleep(3)
    try:
        actual_stages = dates_left.keys()
    except Exception:
        actual_stages = []
    new_stages = bs(driver.page_source, 'lxml')\
        .find('select',
              {'name':
               '_ctl0:MainContentPlaceHolderMaster:gruposDropDownList'})\
        .find_all('option')
    new_stages_ids = []
    for new_stage in new_stages:
        new_stages_ids.append(new_stage.get('value'))
    new_detected = [stage_id for stage_id in new_stages_ids
                    if stage_id not in actual_stages]
    detected = True if len(new_detected) > 0 else False

    return detected, new_detected


def new_results(ti, **op_kwargs):
    """
    Checks for new results by comparing existing dates with the ones available
    on the webpage.

    Args:
        ti: An instance of the TaskInstance object from Airflow.
        **op_kwargs: Keyword arguments containing the URL and file path.
            - url (str): The URL of the webpage to scrape.
            - file_path (str): The path to the file containing the existing
                               dates.

    Returns:
        bool: True if new results are found, False otherwise.

    Notes:
        This function uses a web driver to navigate to the webpage, extracts
        the existing dates from the file, and checks for new stages and dates
        to scrape. If new results are found, it triggers the evaluator by
        pushing a value to the XCom and returns True.

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
        ti.xcom_push(key='trigger_evaluator', value=True)
        print('NEW STAGE to scrape found!')
        return True

    dates_to_scrape_dict = {}
    for stage_id in dates_left.keys():
        dates_to_scrape = []
        for matchday, value in dates_left[stage_id].items():
            today = datetime.today()
            j = datetime.strptime(dates_left[stage_id][matchday], '%d/%m/%Y')
            if j + timedelta(3) < today:
                dates_to_scrape.append(j.strftime('%d/%m/%Y'))
        dates_to_scrape_dict[stage_id] = dates_to_scrape

    if len([value for key, sublist in dates_to_scrape_dict.items()
            for value in sublist]) > 1:
        time.sleep(1)
        driver.get(url)
        time.sleep(2.5)
        stages = bs(driver.page_source, 'lxml')\
            .find('select',
                  {'name':
                   '_ctl0:MainContentPlaceHolderMaster:gruposDropDownList'})\
            .find_all('option')

        stages_ids = []
        for stage in stages:
            stages_ids.append(stage.get('value'))

        for stage_id in stages_ids:
            driver.find_element(By.CSS_SELECTOR,
                                f"option[value='{stage_id}']").click()
            time.sleep(3)
            matchdays = bs(driver.page_source, 'lxml')\
                .find('select',
                      {'name':
                       '_ctl0:MainContentPlaceHolderMaster:jornadasDropDownList'})\
                .find_all('option')

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
                        print('Date to scrape found!')
                        ti.xcom_push(key='trigger_evaluator', value=True)
                        driver.quit()
                        return True
    ti.xcom_push(key='trigger_evaluator', value=False)
    driver.quit()
    return False
