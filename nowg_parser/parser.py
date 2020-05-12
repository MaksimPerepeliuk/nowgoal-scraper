import requests
from bs4 import BeautifulSoup


def get_html(url):
    r = requests.get(url)
    if r.ok:
        return r.text
    return print(r.status_code)


def get_content(html):
    soup = BeautifulSoup(html, 'lxml')
    h1 = soup.find('a')
    return h1


print(get_content(get_html('http://www.google.com')))
