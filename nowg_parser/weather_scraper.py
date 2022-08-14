from fake_useragent import UserAgent
import os
from bs4 import BeautifulSoup
import requests
import csv
from tqdm import tqdm


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


def get_weather_info(soup):
    tags = soup.find_all('div', class_='row')
    weather_info = [tag.text for tag in tags if 'Weather' in tag.text]
    if weather_info:
        return weather_info[0].split('Weather:')[1]
    return ''


def get_stat(html):
    soup = BeautifulSoup(html, 'lxml')
    champ_title = strip_parentheses(
        soup.find('span', class_='LName').find('a').text)
    date = soup.find(attrs={'name': 'timeData'})['data-t']
    weather = get_weather_info(soup)
    teams_titles = [
        [a.text for a in soup.select('span.sclassName a')][0],
        [a.text for a in soup.select('span.sclassName a')][1]]
    final_result = [int(div.text)for div in soup.select('div.score')]
    total_score = sum(final_result)
    first_half_result = soup.find('span', title="Score 1st Half").text
    second_half_result = soup.find('span', title="Score 2nd Half").text
    data = {'champ_title': champ_title.strip(),
            'date': date.strip(),
            'weather': weather.strip(),
            'home': teams_titles[0].strip(),
            'away': teams_titles[1].strip(),
            'result': '{}-{}'.format(final_result[0], final_result[1]),
            'total_score': total_score,
            'first_half': first_half_result,
            'second_half': second_half_result}
    return data


def write_csv(data, file_name, order):
    with open(file_name, 'a') as file:
        writer = csv.DictWriter(file, fieldnames=order)
        is_empty = os.stat(file_name).st_size == 0
        if is_empty:
            writer.writeheader()
        writer.writerow(data)


def write_text_file(data, file_name):
    with open(file_name, 'a') as file:
        file.write(f'{data}')


def main(urls):
    for url in tqdm(urls):
        try:
            data = get_stat(get_html(url))
            order = list(data.keys())
            write_csv(data, 'nowg_parser/data/event_weather_stat.csv', order)
        except Exception as e:
            print(e)
            write_text_file(
                url, 'nowg_parser/data/event_weather_stat_failed_url.txt')
            continue


if __name__ == '__main__':
    urls_file = open('nowg_parser/urls/events__urls.txt')
    urls = urls_file.read().split(', ')
    urls_file.close()
    main(urls)
