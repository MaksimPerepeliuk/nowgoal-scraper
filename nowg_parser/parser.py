from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chromedriver_path = '/home/max/projects/nowg_parser/nowg_parser/chromedriver'
driver = webdriver.Chrome(options=chrome_options,
                          executable_path=chromedriver_path)


def flatten(lists):
    return [elem for sublists in lists for elem in sublists]


def write_text_file(data, file_name):
    with open(file_name, 'a') as file:
        file.write('{}, '.format(data))


def highlight_urls(links):
    for a in links:
        write_text_file(a.get_attribute('href'), 'analyze_urls.txt')


def get_page_data(champ_url):
    driver.get(champ_url)
    time.sleep(2)
    tds = driver.find_elements_by_css_selector('td.lsm2')
    match_analyze_urls = []
    for td in tds:
        try:
            td.click()
            links = driver.find_elements_by_css_selector(
                'a[title="Match Analyze"]')
            match_analyze_urls.append(links)
        except Exception as e:
            print(e)
            continue
    return highlight_urls(flatten(match_analyze_urls))
