from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
import time


# def get_page_source(url):
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--window-size=1920x1080")
#     driver = webdriver.Chrome(options=chrome_options,
#                               executable_path='nowg_parser/chromedriver')
#     driver.get(url)
#     time.sleep(2)
#     a = driver.find_elements_by_css_selector('div.right')
#     print(11111111111, a)


def get_html(url):
    user_agent = UserAgent().chrome
    r = requests.get(url, headers={'User-Agent': user_agent})
    if r.ok:
        return r.text
    print(r.status_code)


def strip_parentheses(string):
    if string[0] == '[':
        return string[1:-1]
    return string


def find_weather_info(soup):
    tags = soup.find_all('div', class_='row')
    return [tag.text for tag in tags if 'Weather' in tag.text]


def get_score(value):
    print(value)
    if value == '':
        return 0
    return value.split('-')


def get_head_to_head_stat(soup, home_team):
    trs = soup.select('table#table_v3 tr')
    home_away_score = {'goals': [0, 0], 'corner': [0, 0]}
    away_home_score = {'goals': [0, 0], 'corner': [0, 0]}
    count_hh_games = 0

    for tr in trs[4:]:  # возможно 3й элемент уже сыгран
        try:
            tds = tr.select('td')
            hh_home_team = tds[2].text
            final_score = get_score(tds[3].text)
            corner_score = get_score(tds[5].text)
            if home_team == hh_home_team:
                home_away_score['goals'][0] += int(final_score[0])
                home_away_score['goals'][1] += int(final_score[1])
                home_away_score['corner'][0] += int(corner_score[0])
                home_away_score['corner'][1] += int(corner_score[1])
            else:
                away_home_score['goals'][0] += int(final_score[0])
                away_home_score['goals'][1] += int(final_score[1])
                away_home_score['corner'][0] += int(corner_score[0])
                away_home_score['corner'][1] += int(corner_score[1])
        except Exception:
            continue
    home_team_goals = home_away_score['goals'][0] + away_home_score['goals'][1]
    home_team_corners = home_away_score['corner'][0] + \
        away_home_score['corner'][1]
    away_team_goals = home_away_score['goals'][1] + away_home_score['goals'][0]
    away_team_corners = home_away_score['corner'][1] + \
        away_home_score['corner'][0]

    return {'count_hh_games': count_hh_games,
            'HH_total_home_goals': home_team_goals,
            'HH_total_home_corners': home_team_corners,
            'HH_total_away_goals': away_team_goals,
            'HH_total_away_corners': away_team_corners,
            'HH_curent_order_home_goals': home_away_score['goals'][0],
            'HH_curent_order_away_goals': home_away_score['goals'][1],
            'HH_curent_order_home_corners': home_away_score['corner'][0],
            'HH_curent_order_away_corners': home_away_score['corner'][1]}


def get_main_stat(html):
    soup = BeautifulSoup(html, 'lxml')
    champ_title = strip_parentheses(
        soup.find('span', class_='LName').find('a').text)
    weather = find_weather_info(soup)
    teams_title = [
        [a.text for a in soup.select('span.sclassName a')][0],
        [a.text for a in soup.select('span.sclassName a')][1]]
    final_result = [int(div.text)for div in soup.select('div.score')]
    total_score = sum(final_result)
    first_half_result = soup.find('span', title="Score 1st Half").text
    second_half_result = soup.find('span', title="Score 2nd Half").text
    hh_stat = get_head_to_head_stat(soup, teams_title[0])
    trs = soup.find_all('tr', bgcolor="#FFECEC")
    # print(second_half_result)


new_type = 'http://www.nowgoal.group/analysis/1763774.html'
old_type = 'http://data.nowgoal.group/analysis/987471.html'
from_new_to_old = 'http://data.nowgoal.group/analysis/1426148.html'

get_main_stat(get_html(from_new_to_old))
# get_main_stat(get_html(old_type))

# get_main_stat(get_html(new_type))
# get_main_stat(get_html(old_type))
