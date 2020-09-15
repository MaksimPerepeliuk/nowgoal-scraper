from bs4 import BeautifulSoup
from nowg_parser.urls_parser import get_driver, write_text_file
from nowg_parser.make_event_data import make_event_data
import csv
from tqdm import tqdm
from multiprocessing import Pool
from math import ceil
from nowg_parser.logs.loggers import app_logger
from multiprocessing import Pool
from tqdm import tqdm
import time


def get_html(url):
    app_logger.info(f'Start receive html on {url}')
    try:
        driver = get_driver()
        driver.get(url)
        time.sleep(0.5)
        html = driver.page_source
        return html
    except Exception:
        app_logger.exception('Err received html on {url}')
        write_text_file(url, 'nowg_parser/logs/failed_stat_url.txt')

def find_stat_table(tables):
    for table in tables:
        tr = table.select('tr')[0]
        if tr.select('th')[0].text.strip() == 'Tech Statistics':
            return table
    raise Exception('Stat table not found')


def get_event_stats(html):
    app_logger.info(f'Start stat parse')
    soup = BeautifulSoup(html, 'lxml')
    stat_table = find_stat_table(soup.select('table.bhTable'))
    trs = stat_table.select('tr')
    data = {}
    for tr in trs[1:]:
        tds = tr.select('td')
        row_name = tds[2].text.strip()
        home_score = tds[1].text.strip()
        away_score = tds[3].text.strip()
        data[row_name] = [home_score, away_score]
    return make_event_data(data)


def get_odds_change(html, event_id):
    soup = BeautifulSoup(html, 'lxml')
    bookm = soup.select('p')[0].text.split(':')[0]
    trs = soup.select('tr')
    home_team = trs[0].select('td')[0].text.strip()
    away_team = trs[2].select('td')[0].text.strip()
    odds_change = {
        'event_id': event_id,
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

def get_odds_info(html, event_id):
    app_logger.info(f'Start stat parse')
    soup = BeautifulSoup(html, 'lxml')
    pinnacle_row = soup.select('tr#oddstr_177')
    sbobet_row = soup.select('tr#oddstr_474')
    betfair_row = soup.select('tr#oddstr_2')
    xbet_row = soup.select('tr#oddstr_1047')
    marathon_row = soup.select('tr#oddstr_816')
    odds_rows = [pinnacle_row, sbobet_row,
                 betfair_row, xbet_row,
                 marathon_row]
    odds_data = []
    for odds_row in odds_rows:
        try:
            odds_url = odds_row[0].select('td')[2]['onclick'].split("'")[1]
            print(get_odds_change(get_html(odds_url), event_id))
        except Exception:
            app_logger.exception('Err on received odds info')

    return odds_data

# print(get_odds_info(get_html('http://www.nowgoal.group/1x2/1154137.htm'), 1))
# url = 'http://data.nowgoal.group/1x2/OddsHistory.aspx?id=90474561&r1=Everton&r2=West%20Ham%20United&Company=Pinnacle'
# print(get_event_stats(get_html('http://data.nowgoal.group/detail/1154137.html')))

def run_parse(event):
    app_logger.info(f'Start parsing urls on {url}')
    url, event_id = event
    filepath = 'nowg_parser/urls/events_urls.txt'
    try:
        events_urls = get_analize_urls(url, page)
        [write_text_file(event_url, filepath) for event_url in events_urls]
    except Exception:
        app_logger.exception(f'Fail parser on url {url}')
        write_text_file(url, 'nowg_parser/urls/failed_parsing_urls3.txt')


def run_multi_parse(urls, n_proc):
    app_logger.info(f'Start multiprocess function urls - {len(urls)} num processes - {n_proc}')
    pool = Pool(n_proc)
    pool.map(run_parse, urls)
    pool.close()
    pool.join()


def main(n_proc):
    urls_file = open('nowg_parser/urls/argentina_urls.txt')
    urls = urls_file.read().split(', ')
    urls_file.close()
    urls_chunks = chunk(urls, n_proc)
    for urls_chunk in tqdm(urls_chunks):
        run_multi_parse(urls_chunk, n_proc)


def parse_failed_urls():
    urls_file = open('nowg_parser/urls/failed_received_urls2.txt')
    urls = urls_file.read().split(', ')
    urls_file.close()
    for url in tqdm(urls):
        parts = url.split('::')
        run_parse(parts[0], int(parts[-1]))

# if __name__ == '__main__':
#     main(8)

