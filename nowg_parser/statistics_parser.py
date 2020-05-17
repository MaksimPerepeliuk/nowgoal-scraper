from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin, urlunsplit
import time


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome(options=chrome_options,
                          executable_path='nowg_parser/chromedriver')


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
    return [tag.text for tag in tags if 'Weather' in tag.text][0]


def get_score(value):
    if value == '':
        return 0
    return value.split('-')


def data_cast(scorred, missed, count):
    prefix = 'last{}m'.format(count)
    return {prefix+'_score_goals': scorred['goals'],
            prefix+'_score_corners': scorred['corners'],
            prefix+'_missed_goals': missed['goals'],
            prefix+'_missed_corners': missed['corners']}


def get_score_missed_stat(trs, team, type_):
    scorred = {'goals': 0, 'corners': 0}
    missed = {'goals': 0, 'corners': 0}
    result_stat = {}
    events_count = 0
    for tr in trs[4:]:
        try:
            tds = tr.select('td')
            table_home_team = tds[2].text
            final_score = get_score(tds[3].text)
            corner_score = get_score(tds[5].text)
            if team == table_home_team:
                scorred['goals'] += int(final_score[0])
                scorred['corners'] += int(corner_score[0])
                missed['goals'] += int(final_score[1])
                missed['corners'] += int(corner_score[1])
                events_count += 1
            else:
                scorred['goals'] += int(final_score[1])
                scorred['corners'] += int(corner_score[1])
                missed['goals'] += int(final_score[0])
                missed['corners'] += int(corner_score[0])
                events_count += 1
        except Exception:
            continue

        if events_count == 5:
            data = data_cast(scorred, missed, 5)
            result_stat.update(data)

        if events_count == 10:
            data = data_cast(scorred, missed, 10)
            result_stat.update(data)

    data = data_cast(scorred, missed, events_count)
    result_stat.update(data)
    return result_stat


def get_common_stat(trs, team):
    result_data = {}
    for tr in trs[3:6]:
        tds = tr.select('td')
        title = tds[0].text
        result_data[team+'_'+title+'_match'] = int(tds[1].text)
        result_data[team+'_'+title+'_win'] = int(tds[2].text)
        result_data[team+'_'+title+'_draw'] = int(tds[3].text)
        result_data[team+'_'+title+'_lose'] = int(tds[4].text)
        result_data[team+'_'+title+'_odds%'] = float(tds[5].text[:-1])
        result_data[team+'_'+title+'_over'] = int(tds[7].text)
        result_data[team+'_'+title+'_over%'] = float(tds[8].text[:-1])
        result_data[team+'_'+title+'_under'] = int(tds[9].text)
        result_data[team+'_'+title+'_under%'] = float(tds[10].text[:-1])
    return result_data


def get_stat(html):
    soup = BeautifulSoup(html, 'lxml')
    champ_title = strip_parentheses(
        soup.find('span', class_='LName').find('a').text)
    weather = find_weather_info(soup).split('Weather:')[1]
    teams_titles = [
        [a.text for a in soup.select('span.sclassName a')][0],
        [a.text for a in soup.select('span.sclassName a')][1]]
    final_result = [int(div.text)for div in soup.select('div.score')]
    total_score = sum(final_result)
    first_half_result = soup.find('span', title="Score 1st Half").text
    second_half_result = soup.find('span', title="Score 2nd Half").text
    data = {'champ_title': champ_title,
            'weather': weather,
            'home': teams_titles[0],
            'away': teams_titles[1],
            'result': '{}-{}'.format(final_result[0], final_result[1]),
            'total_score': total_score,
            'first_half': first_half_result,
            'second_half': second_half_result}
    h2h_stat = get_score_missed_stat(
        soup.select('table#table_v3 tr'), teams_titles[0], 'head2head')
    home_prev_stat = get_score_missed_stat(
        soup.select('table#table_v1 tr'), teams_titles[0], 'home_prev')
    away_prev_stat = get_score_missed_stat(
        soup.select('table#table_v2 tr'), teams_titles[1], 'away_prev')
    date_box = soup.select('tbody table tr td table.date_box tr')
    home_box, away_box = date_box[:7], date_box[7:14]
    home_common_stat = get_common_stat(home_box, 'home_team')
    away_common_stat = get_common_stat(away_box, 'away_team')
    data.update(h2h_stat)
    data.update(home_prev_stat)
    data.update(away_prev_stat)
    data.update(home_common_stat)
    data.update(away_common_stat)
    return data


def get_table_data(html):
    soup = BeautifulSoup(html, 'lxml')
    kind_odds = soup.find('span', class_='on').text
    trs = soup.select('span#dataList tr')
    print(kind_odds, len(trs))


def get_kelly_info(url):
    driver.get(url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    trs = soup.select('div#ivsi tr')
    print(len(trs))


get_kelly_info('http://www.nowgoal.group/1x2/old_1432800.htm')


def get_odds_info(html):
    soup = BeautifulSoup(html, 'lxml')
    url_schema = 'http://data.nowgoal.com'
    data = {}
    trs = soup.select('tr')[2:]
    for tr in trs:
        tds = tr.select('td')
        book_name = tds[0].text
        if 'Sbobet' in book_name:
            data['close_HW_1x2'] = tds[1].find('span').text
            data['open_HW_1x2'] = tds[1].text.split(data['close_HW_1x2'])[0]
            data['close_D_1x2'] = tds[2].find('span').text
            data['open_D_1x2'] = tds[2].text.split(data['close_D_1x2'])[0]
            data['close_AW_1x2'] = tds[3].find('span').text
            data['open_AW_1x2'] = tds[3].text.split(data['close_AW_1x2'])[0]
            data['close_AH_value'] = tds[5].find('span').text
            data['open_AH_value'] = tds[5].text.split(
                data['close_AH_value'])[0]
            data['close_AH_home'] = tds[4].find('span').text
            data['open_AH_home'] = tds[4].text.split(
                data['close_AH_home'])[0]
            data['close_AH_away'] = tds[6].find('span').text
            data['open_AH_away'] = tds[6].text.split(
                data['close_AH_away'])[0]
            data['close_OU_value'] = tds[8].find('span').text
            data['open_OU_value'] = tds[8].text.split(
                data['close_OU_value'])[0]
            data['close_OU_home'] = tds[7].find('span').text
            data['open_OU_home'] = tds[7].text.split(
                data['close_OU_home'])[0]
            data['close_OU_away'] = tds[9].find('span').text
            data['open_OU_away'] = tds[9].text.split(
                data['close_OU_away'])[0]
            similar_cf = get_html(
                url_schema + tds[10].select('a')[1]['href'])
            similar_cf_data = get_similar_cf_data(similar_cf)


# get_odds_info(get_html('http://data.nowgoal.com/oddscomp/987471.html'))

# new_type = 'http://www.nowgoal.group/analysis/1763774.html'
# old_type = 'http://data.nowgoal.group/analysis/987471.html'
# from_new_to_old = 'http://data.nowgoal.group/analysis/1426148.html'

# print(get_stat(get_html(old_type)))

# def get_kelly_info(url):
#     url_parts = urlparse(url)
#     path_parts = url_parts.path.split('/')
#     for i in range(1, 6, 2):
#         new_path = '/{}/{}{}'.format(path_parts[1], i, path_parts[2][1:])
#         new_url = urljoin(url, new_path)
#         driver.get(new_url)
#         time.sleep(2)
#         html = driver.page_source
#         data = get_table_data(html)
    # for i in range(1, 4):
    #     page_url = '{}/{}/{}{}'.format(
    #         url_parts[0], url_parts[1], i, tail_url)
    #     driver.get(page_url)
    #     time.sleep(2)
    #     # menu = soup.select('div.menu span')[1]['onclick']
    #     trs = driver.find_elements_by_css_selector('span#dataList tr')
    #     print(len(trs))
