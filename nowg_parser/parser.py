from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

url = 'http://info.nowgoal.group/en/League.aspx?SclassID=8'
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
chromedriver_path = '/home/max/projects/nowg_parser/nowg_parser/chromedriver'
driver = webdriver.Chrome(options=chrome_options,
                          executable_path=chromedriver_path)


def get_match_analize_urls(champ_url, driver):
    driver.get(champ_url)
    time.sleep(0.5)
    a = driver.find_elements_by_css_selector('a[title="Match Analyze"]')
    return a
