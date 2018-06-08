# -*- coding: UTF-8 -*-
from __future__ import print_function
import requests
from lxml import etree
import re
import utils
from selenium import webdriver
from bs4 import BeautifulSoup
import datetime
import os
import json
import sys


"""

Followers details:
This requires more information in cookie to access: _T_WM
I think using selenium with simulated web browser behavior it is achievable, but
1. I don't fully understand the package
2. not very familiar with xtree path (bs4 is better)
Leave it until I know what happened

url = "https://weibo.cn/1776448504/fans?page=19&display=0&retcode=6102"
r = requests.get(url, cookies={"Cookie": "_T_WM=ec1a4454c0d9d6d28bb947142ca09f4f; SUB=_2A253gE9VDeThGeVM6FQZ9yvOyD6IHXVUi1EdrDV6PUJbkdBeLUbdkW1NTKWBvjMxvfXWbMrYJ01hTA-fdYsQshDp; SUHB=0OM0IZCuuDil4y; SCF=Aj52M7AisY2zemY_Am0nKcL71Og-kwj4KrbW9HkL8O51TjMxprJ7l2Sryhd6P9gtzV7sn1wG4n0t3QM9ZNxcc0w.; SSOLoginState=1518616325"}, headers=headers)

"""

# in case old cookie method fails
def get_cookie_with_selenium(username, password):
    chromePath = "/usr/local/bin/chromedriver"
    wd = webdriver.Chrome(executable_path=chromePath)
    loginUrl = 'http://www.weibo.com/login.php'
    wd.get(loginUrl)
    wd.find_element_by_xpath('//*[@id="loginname"]').send_keys(username)
    wd.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input').send_keys(password)
    wd.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()

    req = requests.Session()
    cookies = wd.get_cookies()
    print(cookies)
    for cookie in cookies:
        req.cookies.set(cookie["name"], cookie["value"])
    url = "http://chart.weibo.com/chart?rank_type=6&version=v1"
    r = req.get(url)
    print(r.content)


# Manually concatenate cookies from response header
def get_cookie(username, password):

    payload = {"username": username,
               "password": password,
               "savestate": "1",
               "ec": "0",
               "entry": "mweibo",
               "mainpageflag": "1"}
    headers = {"Accept-Encoding": "gzip, deflate, br",
               "Connection": "keep-alive",
               "Content-Length": "162",
               "Content-Type": "application/x-www-form-urlencoded",
               "Host": "passport.weibo.cn",
               "Origin": "https://passport.weibo.cn",
               "Referer": "https://passport.weibo.cn/signin/login",
               "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"}
    url = "https://passport.weibo.cn/sso/login"
    response = utils.request(url, "cookie", data=payload, headers=headers)
    if response is not None:
        return response.get_cookie_data()
    else:
        return None


'''
curl -H 'Host: chart.weibo.com'
    -H 'Cache-Control: max-age=0'
    -H 'Upgrade-Insecure-Requests: 1'
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    -H 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7'
    -H 'Cookie: login_sid_t=b689be1da75c3e30c88ca9aa4371b135; cross_origin_proto=SSL; _s_tentry=passport.weibo.com; Apache=4200097554956.783.1518665647383; SINAGLOBAL=4200097554956.783.1518665647383; ULV=1518665647389:1:1:1:4200097554956.783.1518665647383:; STAR-G0=13a69f4f7468fb922d999343597548de; UOR=,,login.sina.com.cn; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTdxv_d-bjYALZqEF93-os5JpX5K2hUgL.FoeEe0qRS0-Ee0z2dJLoI0YLxKnL1K5L1-BLxKnL12-L1h.LxKqL12-LBKMLxK-LBKBLBKMLxK-L12qL1KBLxKBLBonL1hMLxK-LBozL1h2t; ALF=1559528706; SSOLoginState=1527992707; SCF=Aj52M7AisY2zemY_Am0nKcL71Og-kwj4KrbW9HkL8O517oKZRofb_QPG4qYxYhsm5zKyLCJT01QWh3E-pVX5Rz8.; SUB=_2A252FyHUDeThGeVM6FQZ9yvOyD6IHXVVZRQcrDV8PUNbmtBeLWHSkW9NTKWBvn9UvVUe676zdYzFcUZrOaamNoGE; SUHB=02M_U7vB7LcaoU; wvr=6; rank_type=6; WBStorage=5548c0baa42e6f3d|undefined'
    --compressed 'http://chart.weibo.com/chart?rank_type=6'
'''

# This method is used to caluclate the post on chart.weibo.com and recording their four features.
def get_chart(cookie):

    headers = {
        "Host": "chart.weibo.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        "Cookie": cookie["Cookie"]
    }

    for rank in [3, 5, 6]:
        for page in [1, 2]:
            url = "http://chart.weibo.com/chart?rank_type=%s&page=%s" % (rank, page)
            response = requests.get(url, headers=headers)

            soup = BeautifulSoup(response.content, "lxml")
            name_divs = soup.find_all("div", class_=re.compile("sr_name S_func1"))
            read_num_divs = soup.find_all("li", class_=re.compile("arr1 clearfix"))
            interaction_num_divs = soup.find_all("li", class_=re.compile("arr2 clearfix"))
            affection_num_divs = soup.find_all("li", class_=re.compile("arr3 clearfix"))
            loveness_num_divs = soup.find_all("li", class_=re.compile("arr4 clearfix"))
            for name_div, read_div, inter_div, affect_div, loveness_div in zip(name_divs, read_num_divs, interaction_num_divs, affection_num_divs, loveness_num_divs):
                name = name_div.text.encode("utf-8")
                read_num = read_div.find_all("span", class_="pro_num")[0].text
                interaction_num = inter_div.find_all("span", class_="pro_num")[0].text
                affection_num = affect_div.find_all("span", class_="pro_num")[0].text
                loveness_num = loveness_div.find_all("span", class_="pro_num")[0].text
                print(name, read_num, interaction_num, affection_num, loveness_num)

    # get_followers(cookie, "caixukun")

def get_post_data(cookie):
    username = "1776448504"  # TODO: change username freely
    url = "https://weibo.cn/%s" % username
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    for div in soup.find_all("div", class_="c"):
        if div.get("id") is None:
            continue

        div_id = div.get("id")
        assert div_id.startswith("M_")
        mid = url_to_mid(div_id[2:])
        url = "https://pay.biz.weibo.com/aj/getprice/advance?mid=%s&touid=%s" % (mid, username)
        headers = {
            "Host": "pay.biz.weibo.com",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "Cookie": cookie["Cookie"]
        }
        data = requests.get(url, headers=headers)
        data = json.loads(data.content)

        for a in div.find_all("a"):
            if a.text.encode("utf-8").startswith("评论"):
                print(username, div_id, mid, "".join(re.findall("[(\d+)]", a.text.encode("utf-8"))))
            if a.text.encode("utf-8").startswith("赞"):
                print(username, div_id, mid, "".join(re.findall("[(\d+)]", a.text.encode("utf-8"))))
            if a.text.encode("utf-8").startswith("转发"):
                print(username, div_id, mid, "".join(re.findall("[(\d+)]", a.text.encode("utf-8"))))
        print(username, div_id, mid, data["data"]["self_price"])


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def base62_encode(num, alphabet=ALPHABET):

    """Encode a number in Base X
    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num

def url_to_mid(url):

    url = str(url)[::-1]
    size = len(url) / 4 if len(url) % 4 == 0 else len(url) / 4 + 1
    result = []
    for i in range(size):
        s = url[i * 4: (i + 1) * 4][::-1]
        s = str(base62_decode(str(s)))
        s_len = len(s)
        if i < size - 1 and s_len < 7:
            s = (7 - s_len) * '0' + s
        result.append(s)
    result.reverse()
    return int(''.join(result))


def get_followers(cookie, name):

    def retrive_followers_content(cookie, username):
        url = "https://weibo.cn/%s?display=0&retcode=6102" % username
        response = requests.get(url, "html", cookies=cookie)
        return response

    def extract_follower_from_content(content):
        selector = etree.HTML(content)
        str_gz = selector.xpath("//div[@class='tip2']/a/text()")[1]
        pattern = r"\d+\.?\d*"
        guid = re.findall(pattern, str_gz, re.M)
        followers = int(guid[0])
        return followers

    username = "caizicaixukun"
    response = retrive_followers_content(cookie, username)
    if response is None:
        return None
    start_time = response.start_time.strftime("%Y%m%d,%H:%M:%S.%f")
    finish_time = response.finish_time.strftime("%Y%m%d,%H:%M:%S.%f")
    followers = extract_follower_from_content(response.get_html())
    return start_time, finish_time, name, username, followers


def get_all_followers(cookie):
    def print_follower_count_header(f):
        raise

    date = datetime.date.today().strftime("%Y%m%d")
    filename = "%s_follower_counts.csv" % date

    usernames = []
    with open("weibo_ids.csv") as f:
        for line in f.readlines():
            segs = line.strip().split(",")
            name = segs[0].decode("GB2312").encode("utf-8")
            username = segs[2]
            if username == "id":
                continue
            usernames.append((name, username))

    is_file = os.path.isfile(filename)
    with open(filename, "a") as f:
        if not is_file:
            print_follower_count_header(f)
        # username = "caizicaixukun"
        for name, username in usernames:
            utils.log_print("[** LOG **] Get followers %s" % name)
            res = get_followers(cookie, name, username)
            if res is None:
                utils.log_print("[** ERROR LOG **] Failed getting followers %s" % name)
                date = datetime.date.today().strftime("%Y%m%d")
                time = datetime.datetime.now().strftime("%Y%m%d,%H:%M:%S.%f")
                with open(".%s_error.log" % date, "a") as f_err:
                    print("Failed", time, name, username, file=f_err)
            else:
                utils.log_print("[** LOG **] Succeed getting followers %s" % name)
                start_time, finish_time, name, username, followers = res
                print(start_time, finish_time, name, username, followers)
    return filename


if __name__ == "__main__":
    username, password = sys.argv[1], sys.argv[2]
    # cookie = get_cookie(username, password)
    # get_chart(cookie)
    get_cookie_with_selenium(username, password)
