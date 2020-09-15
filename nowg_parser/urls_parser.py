from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from nowg_parser.logs.loggers import app_logger
from multiprocessing import Pool
from tqdm import tqdm
import time


def get_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chromedriver_path = 'nowg_parser/chromedriver'
    return webdriver.Chrome(options=chrome_options,
                            executable_path=chromedriver_path)

def chunk(list_, size):
    result = []
    chunk = []
    for elem in list_:
        if len(chunk) == size:
            result.append(chunk)
            chunk = []
        chunk.append(elem)
    result.append(chunk)
    return result


def write_text_file(data, file_name):
    with open(file_name, 'a') as file:
        file.write('{}, '.format(data))


def flatten(lists):
    return [elem for sublists in lists for elem in sublists]


def extract_urls(links):
    urls = []
    for a in links:
        urls.append(a.get_attribute('href'))
    return urls


def get_extend_urls():
    doble_years = ['2018-2019', '2017-2018', '2016-2017',
                   '2015-2016', '2014-2015', '2013-2014',
                   '2012-2013', '2011-2012']
    single_years = ['2018', '2017', '2016', '2015',
                    '2014', '2013', '2012', '2011']
    content_file = open('nowg_parser/urls/champ_urls.txt')
    urls = content_file.read().split('\n')
    content_file.close()
    ext_urls = []
    for url in urls:
        ext_urls.append(url)
        for doble_year, single_year in zip(doble_years, single_years):
            if '2019-2020' in url:
                new_urls = url.replace('2019-2020', doble_year)
                ext_urls.append(new_urls)
            elif '2019' in url:
                new_urls = url.replace('2019', single_year)
                ext_urls.append(new_urls)
    return ext_urls

    
def get_analize_urls(champ_url, page=None):
    driver = get_driver()
    driver.get(champ_url)
    time.sleep(2)
    cup_match_td = driver.find_elements_by_css_selector('td.cupmatch_rw2')
    if len(cup_match_td) > 0:
        cup_match_td[0].click()
    time.sleep(1)
    tds = driver.find_elements_by_css_selector('td.lsm2')
    tds_select = tds if not page else [tds[page]]
    urls = []
    for i, td in enumerate(tds_select):
        try:
            td.click()
            time.sleep(2)
            links = driver.find_elements_by_css_selector(
                'a[title="Match Analyze"]')
            if len(links) == 0:
                links = driver.find_elements_by_css_selector(
                    'a[title="Match Analysis"]')
            event_urls = extract_urls(links)
            urls.append(event_urls)
        except Exception:
            app_logger.exception(f'err received analysis url on {champ_url} page {i}')
            write_text_file(f'{champ_url} : {i}', 'nowg_parser/urls/failed_received_urls3.txt')
    driver.quit()
    return flatten(urls)


def run_parse(url, page=None):
    app_logger.info(f'Start parsing urls on {url}')
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

if __name__ == '__main__':
    main(8)
    with open('nowg_parser/urls/events_urls.txt') as f:
    urls = f.read().split(', ')
    for i, url in enumerate(urls):
        write_text_file(url + f' id{i}', 'nowg_parser/urls/urls_with_id.txt')
