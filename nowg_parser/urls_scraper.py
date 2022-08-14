from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
            write_text_file(f'{champ_url} : {i}',
                            'nowg_parser/urls/failed_received_urls3.txt')
    driver.quit()
    return flatten(urls)


def run_parse(url, page=None):
    filepath = 'nowg_parser/urls/events__urls.txt'
    try:
        events_urls = get_analize_urls(url, page)
        [write_text_file(event_url, filepath) for event_url in events_urls]
    except Exception as e:
        print(e)
        write_text_file(url, 'nowg_parser/urls/failed_parsing_urls_.txt')


def main():
    urls_file = open('nowg_parser/urls/champs_urls.txt')
    urls = urls_file.read().split(', ')
    urls_file.close()
    for url in tqdm(urls):
        run_parse(url)


if __name__ == '__main__':
    main()
    # with open('nowg_parser/urls/events_urls.txt') as f:
    #     urls = f.read().split(', ')
    #     for i, url in enumerate(urls):
    #         write_text_file(url + f' id{i}', 'nowg_parser/urls/urls_with_id.txt')
