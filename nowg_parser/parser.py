from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chromedriver_path = '/home/max/projects/nowg_parser/nowg_parser/chromedriver'
driver = webdriver.Chrome(options=chrome_options,
                          executable_path=chromedriver_path)


def write_text_file(data, file_name):
    with open(file_name, 'a') as file:
        file.write('{}, '.format(data))


def flatten(lists):
    return [elem for sublists in lists for elem in sublists]


def highlight_urls(links):
    if not links:
        return
    for a in links:
        write_text_file(a.get_attribute('href'), 'match_analize.txt')


def write_analize_urls(champ_url):
    driver.get(champ_url)
    time.sleep(1)
    cup_match_td = driver.find_elements_by_css_selector('td.cupmatch_rw2')
    if cup_match_td:
        cup_match_td[0].click()
    time.sleep(1)
    tds = driver.find_elements_by_css_selector('td.lsm2')
    for td in tds:
        try:
            td.click()
            links = driver.find_elements_by_css_selector(
                'a[title="Match Analyze"]')
            if not links:
                links = driver.find_elements_by_css_selector(
                    'a[title="Match Analysis"]')
            highlight_urls(links)
        except Exception as e:
            print(e)
            continue


def get_extend_urls():
    doble_years = ['2018-2019', '2017-2018', '2016-2017',
                   '2015-2016', '2014-2015', '2013-2014']
    one_years = ['2019', '2018', '2017', '2016', '2015', '2014']
    content = open('data/competitions_urls.txt').read()
    urls = content.split(', ')

    for url in urls:
        for doble_year, one_year in zip(doble_years, one_years):
            if '2019-2020' in url:
                new_urls = url.replace('2019-2020', doble_year)
                urls.append(new_urls)
            elif '2020' in url:
                new_urls = url.replace('2020', doble_year)
                urls.append(new_urls)
    return urls


def main():
    urls = get_extend_urls()
    for url in urls:
        try:
            write_analize_urls(url)
        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    main()
