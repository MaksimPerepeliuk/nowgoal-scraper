import requests
from bs4 import BeautifulSoup


r = requests.get('http://www.nowgoal.group/analysis/1763774.html')
soup = BeautifulSoup(r.text, 'lxml')
trs = soup.find_all('tr', bgcolor="#FFECEC")
print(len(trs))
