# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup


name = "超级農農"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"}
url = "https://www.google.com/search"
params = {"q": "超级農農微博"}
r = requests.get(url, params=params, headers=headers)
soup = BeautifulSoup(r.content, "lxml")
print name, soup.find_all("cite")[0].text[18:]
