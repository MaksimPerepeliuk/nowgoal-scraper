from bs4 import BeautifulSoup
from nowg_parser.urls_parser import get_driver, write_text_file, chunk
from nowg_parser.make_event_data import make_event_data
import csv
from tqdm import tqdm
from multiprocessing import Pool
from math import ceil
from nowg_parser.logs.loggers import app_logger
from multiprocessing import Pool
from tqdm import tqdm
import time
import os


def write_csv(filename, data, order):
    with open(filename, 'a') as file:
        writer = csv.DictWriter(file, fieldnames=order)
        is_empty = os.stat(filename).st_size == 0
        if is_empty:
            writer.writeheader()
        writer.writerow(data)


def get_html(url):
    app_logger.info(f'Start receive html on {url}')
    try:
        with get_driver() as driver:
            driver.get(url)
            time.sleep(1)
            html = driver.page_source
    except Exception:
        app_logger.exception('Err received html on {url}')
        write_text_file(url, 'nowg_parser/logs/failed_stat_url.txt')
    return html


def find_stat_table(tables):
    for table in tables:
        tr = table.select('tr')[0]
        if tr.select('th')[0].text.strip() == 'Tech Statistics':
            return table
    raise Exception('Stat table not found')


def get_event_stats(stat_html, info_html, event_id):
    app_logger.info(f'Start stat parse')
    soup = BeautifulSoup(stat_html, 'lxml')
    stat_table = find_stat_table(soup.select('table.bhTable'))
    trs = stat_table.select('tr')
    event_info = get_event_info(info_html)
    data = {}
    for tr in trs[1:]:
        tds = tr.select('td')
        row_name = tds[2].text.strip()
        home_score = tds[1].text.strip()
        away_score = tds[3].text.strip()
        data[row_name] = [home_score, away_score]
    return {'id': event_id, **event_info, **make_event_data(data)}


def get_odds_change(html, odds_info_url):
    soup = BeautifulSoup(html, 'lxml')
    bookm = soup.select('p')[0].text.split(':')[0]
    trs = soup.select('tr')
    home_team = trs[0].select('td')[0].text.strip()
    away_team = trs[0].select('td')[2].text.strip()
    odds_change = {
        'odds_url': odds_info_url,
        'bookm': bookm,
        'home_team': home_team,
        'away_team': away_team,
        'home_odds': [],
        'draw_odds': [],
        'away_odds': [],
        'hwr': [],
        'dr': [],
        'awr': [],
        'return': [],
        'change_times': []
    }
    for tr in trs[1:]:
        tds = tr.select('td')
        odds_change['home_odds'].append(tds[0].text)
        odds_change['draw_odds'].append(tds[1].text)
        odds_change['away_odds'].append(tds[2].text)
        odds_change['hwr'].append(tds[3].text)
        odds_change['dr'].append(tds[4].text)
        odds_change['awr'].append(tds[5].text)
        odds_change['return'].append(tds[6].text)
        odds_change['change_times'].append(tds[-1].text.strip())
    return odds_change

def get_event_info(html):
    soup = BeautifulSoup(html, 'lxml')
    date = soup.select('span#match_time')[0].text.strip().split('\xa0')[0]
    try:
        champ_title = soup.select('span.LName')[0].find('a').text.strip()
    except:
        champ_title = soup.select('div.vs span.LName')[0].text.strip()
    teams = soup.select('div#headVs span.sclassName a')
    home_team = teams[0].text.strip()
    away_team = teams[1].text.strip()
    final_result = f"{soup.select('div.score')[0].text.strip()}-{soup.select('div.score')[1].text.strip()}"
    first_half_result = soup.find('span', title="Score 1st Half").text.strip()
    event_info = {
        'date': date,
        'championate': champ_title,
        'home_team': home_team,
        'away_team': away_team,
        'result_score': final_result,
        'first_half_score': first_half_result
    }
    return event_info


def get_odds_info(html, odds_info_url):
    app_logger.info(f'Start stat parse')
    soup = BeautifulSoup(html, 'lxml')
    event_info = get_event_info(html)
    pinnacle_row = soup.select('tr#oddstr_177')
    sbobet_row = soup.select('tr#oddstr_474')
    betfair_row = soup.select('tr#oddstr_2')
    xbet_row = soup.select('tr#oddstr_1047')
    marathon_row = soup.select('tr#oddstr_816')
    odds_rows = [pinnacle_row, sbobet_row,
                 betfair_row, xbet_row,
                 marathon_row]
    bookms = ['pinnacle', 'sbobet', 'betfair', '1xbet', 'marathon']
    odds_data = []
    for i, odds_row in enumerate(odds_rows):
        try:
            odds_url = odds_row[0].select('td')[2]['onclick'].split("'")[1]
            odds_change_info = get_odds_change(get_html(odds_url), odds_info_url)
            odds_data.append({**event_info, **odds_change_info})
        except Exception:
            app_logger.info(f'Received odds info on {odds_info_url} odds_url iter not found {bookms[i]}')
    if len(odds_data) == 0:
        app_logger.debug('odds data not found on {odds_info_url}')
        write_text_file(odds_info_url, 'nowg_parser/logs/failed_odds_stats.txt')
    return odds_data


def run_parse(event_url):
    app_logger.info(f'Start parsing urls on {event_url}')
    odds_file = 'nowg_parser/data/odds_stats.csv'
    try:
        url, event_id = event_url
        odds_url = url.replace('analysis', '1x2').replace('html', 'htm')
        odds_info = get_odds_info(get_html(odds_url), odds_url)
        for odds_stat in odds_info:
            write_csv(odds_file, odds_stat, odds_stat.keys())
    except Exception:
        app_logger.exception(f'Fail parser on url {odds_url}')
        write_text_file(url, 'nowg_parser/logs/failed_parsing_stats.txt')


def run_multi_parse(urls, n_proc):
    app_logger.info(f'Start multiprocess function urls - {len(urls)} num processes - {n_proc}')
    with Pool(n_proc) as p:
        r = list(tqdm(p.imap(run_parse, urls), total=len(urls)))


if __name__ == '__main__':
    urls_file = open('nowg_parser/urls/urls_with_id.txt')
    urls = urls_file.read().split(', ')
    urls_file.close()
    events_urls = [(url.split(' id')[0], int(url.split(' id')[1])) for url in urls]
    run_multi_parse(events_urls, 8)

