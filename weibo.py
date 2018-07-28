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
import argparse


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
    wd.find_element_by_xpath(
        '//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input').send_keys(password)
    wd.find_element_by_xpath(
        '//*[@id="pl_login_form"]/div/div[3]/div[6]/a').click()

    req = requests.Session()
    cookies = wd.get_cookies()
    print(cookies)
    for cookie in cookies:
        req.cookies.set(cookie["name"], cookie["value"])
    url = "http://chart.weibo.com/chart?rank_type=6&version=v1"
    r = req.get(url)
    print(r.content)


class Cookie(object):

    def __init__(self):
        self.cookie_parts = {}

    def set(self, key, value):
        self.cookie_parts[key] = value

    def get_cookie(self):
        cookies = []
        for key, value in self.cookie_parts.items():
            cookies.append("%s=%s" % (key, value))
        return " ".join(cookies)


# 获取微博登录的cookie，分三步。第一步登录，获取SUB, SUHB, SCF和SSOLogin
# 然后读取https://m.weibo.cn，获取M_WEIBOCN_PARAMS和_T_WM
# 最后登录独立超话，获取WEIBOCN_FROM并更新M_WEIBOCN_PARAMS
def get_cookie(username, password):

    cookie = Cookie()

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
    response = requests.post(url, data=payload, headers=headers)

    for info in response.headers["Set-Cookie"].split():
        if info.startswith("SUB=") or info.startswith("SUHB=") or info.startswith("SCF=") or info.startswith("SSOLoginState="):
            key, value = info.split("=")
            cookie.set(key, value)

    '''
    curl 'https://m.weibo.cn/' 
    -H 'authority: m.weibo.cn' 
    -H 'upgrade-insecure-requests: 1' 
    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' 
    -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' 
    -H 'referer: https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn%2F' 
    -H 'accept-encoding: gzip, deflate, br' 
    -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7' 
    -H 'cookie: SUB=_2A252GUo0DeThGeVM6FQZ9yvOyD6IHXVV4lZ8rDV6PUJbkdBeLRbikW1NTKWBvlMd6utP8-GniJG48Z69mYN_MLcM; SUHB=0QSp1-7WD51Jix; SCF=Aj52M7AisY2zemY_Am0nKcL71Og-kwj4KrbW9HkL8O511BUUv7LFPRgmmi6VLFtweCnnDEZFxb6DXYNUEBPSkx8.; SSOLoginState=1528642148' 
    --compressed
    '''
    headers = {
        "authority": "m.weibo.cn",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "referer": "https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn%2F",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        "cookie": cookie.get_cookie()
    }
    url = "https://m.weibo.cn"
    response = requests.get(url, headers=headers)
    for info in response.headers["Set-Cookie"].split():
        if info.startswith("M_WEIBOCN_PARAMS") or info.startswith("_T_WM"):
            key, value = info.split("=")
            cookie.set(key, value)
    cookie.set("MLOGIN", "1;")

    # 随意选择了一个超话尝试了一下
    page_id = "100808066f8f58c6a0520a79d77ce704ab5ae6"
    headers = {
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "referer": "https://m.weibo.cn/p/%s" % page_id,
        "authority": "m.weibo.cn",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": cookie.get_cookie()
    }
    utils.log_print("[** LOG **] Get Cookies %r" % cookie.get_cookie())
    url = "https://m.weibo.cn/p/%s" % page_id
    response = requests.get(url, headers=headers)
    for info in response.headers["Set-Cookie"].split():
        if info.startswith("M_WEIBOCN_PARAMS") or info.startswith("WEIBOCN_FROM"):
            key, value = info.split("=")
            cookie.set(key, value)
            utils.log_print("[** LOG **] Get Current Cookie %r" %
                            cookie.get_cookie())

    return cookie

    # get_followers(cookie, "caixukun")



# 为了获取某条评论的评论，赞，转发数量，需要计算出一个这条微博的mid值
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


'''
curl 'https://m.weibo.cn/api/container/getIndex?containerid=1008084df10e1237b5578013705ae934cc0b5a' 
-H 'cookie: _T_WM=2347d44799bd017a7c42d4b0778e9eff; WEIBOCN_FROM=1110006030; ALF=1530701067; SCF=Aj52M7AisY2zemY_Am0nKcL71Og-kwj4KrbW9HkL8O519CB_gPvclMRjWoBZ1JpYr7_h4F81dOxbdG6-pz2FcR0.; SUB=_2A252EWkXDeThGeVM6FQZ9yvOyD6IHXVV-ndfrDV6PUJbktBeLWjckW1NTKWBvpSLDufBiIX08-g5g_RhTpQRWURW; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTdxv_d-bjYALZqEF93-os5JpX5K-hUgL.FoeEe0qRS0-Ee0z2dJLoI0YLxKnL1K5L1-BLxKnL12-L1h.LxKqL12-LBKMLxK-LBKBLBKMLxK-L12qL1KBLxKBLBonL1hMLxK-LBozL1h2t; SUHB=0sqROPqomMAY9G; SSOLoginState=1528109383; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D1008084df10e1237b5578013705ae934cc0b5a_-_main%26fid%3D1008084df10e1237b5578013705ae934cc0b5a%26uicode%3D10000011' 
-H 'accept-encoding: gzip, deflate, br' 
-H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7' 
-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' 
-H 'accept: application/json, text/plain, */*' 
-H 'referer: https://m.weibo.cn/p/1008084df10e1237b5578013705ae934cc0b5a' 
-H 'authority: m.weibo.cn' 
-H 'x-requested-with: XMLHttpRequest' 
--compressed
'''
# 获取用于签到的地址


def get_super_sign_info(cookie, page_id):

    headers = {
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "referer": "https://m.weibo.cn/p/%s" % page_id,
        "authority": "m.weibo.cn",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": cookie.get_cookie()
    }

    url = "https://m.weibo.cn/api/container/getIndex?containerid=%s" % page_id
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    return data["data"]["pageInfo"]["toolbar_menus"][0]["scheme"]


'''
curl 'https://m.weibo.cn/api/config' 
-H cookie 
-H 'accept-encoding: gzip, deflate, br' 
-H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7' 
-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' 
-H 'accept: application/json, text/plain, */*' 
-H 'referer: https://m.weibo.cn/p/1008084df10e1237b5578013705ae934cc0b5a' 
-H 'authority: m.weibo.cn' 
-H 'x-requested-with: XMLHttpRequest' --compressed
'''
# 获取用于签到的st数据，需要作为data post到服务器


def get_config(cookie, page_id):

    headers = {
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "referer": "https://m.weibo.cn/p/%s" % page_id,
        "authority": "m.weibo.cn",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": cookie.get_cookie()
    }

    url = "https://m.weibo.cn/api/config"
    response = requests.get(url, headers=headers)
    data = json.loads(response.content)
    return data["data"]["st"]


'''
curl 'https://m.weibo.cn/api/container/button?sign=44b7be&request_url=http%3A%2F%2Fi.huati.weibo.com%2Fmobile%2Fsuper%2Factive_checkin%3Fpageid%3D10080877197fd1ded939d5a32cac51e9200c47' 
-H 'cookie: _T_WM=2347d44799bd017a7c42d4b0778e9eff; 
    WEIBOCN_FROM=1110006030; 
    ALF=1530701067; 
    SCF=Aj52M7AisY2zemY_Am0nKcL71Og-kwj4KrbW9HkL8O519CB_gPvclMRjWoBZ1JpYr7_h4F81dOxbdG6-pz2FcR0.; 
    SUB=_2A252EWkXDeThGeVM6FQZ9yvOyD6IHXVV-ndfrDV6PUJbktBeLWjckW1NTKWBvpSLDufBiIX08-g5g_RhTpQRWURW; 
    SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTdxv_d-bjYALZqEF93-os5JpX5K-hUgL.FoeEe0qRS0-Ee0z2dJLoI0YLxKnL1K5L1-BLxKnL12-L1h.LxKqL12-LBKMLxK-LBKBLBKMLxK-L12qL1KBLxKBLBonL1hMLxK-LBozL1h2t; 
    SUHB=0sqROPqomMAY9G; 
    SSOLoginState=1528109383; 
    MLOGIN=1; 
    M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D10080877197fd1ded939d5a32cac51e9200c47_-_main%26fid%3D10080877197fd1ded939d5a32cac51e9200c47_-_main%26uicode%3D10000011' 
-H 'origin: https://m.weibo.cn' 
-H 'accept-encoding: gzip, deflate, br' 
-H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7' 
-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' 
-H 'content-type: application/x-www-form-urlencoded' 
-H 'accept: application/json, text/plain, */*' 
-H 'referer: https://m.weibo.cn/p/10080877197fd1ded939d5a32cac51e9200c47' 
-H 'authority: m.weibo.cn' 
-H 'x-requested-with: XMLHttpRequest' 
--data 'st=fcc0da' --compressed
'''

# 获取签到信息


def get_sign_rank(cookie, page_id):

    url = "https://m.weibo.cn%s" % get_super_sign_info(cookie, page_id)

    st = get_config(cookie, page_id)
    post_data = {"st": st.encode("ascii")}

    headers = {
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
        "accept": "application/json, text/plain, */*",
        "referer": "https://m.weibo.cn/p/%s" % page_id,
        "authority": "m.weibo.cn",
        "x-requested-with": "XMLHttpRequest",
        "Cookie": cookie.get_cookie()
    }
    response = requests.post(url, headers=headers, data=post_data)
    data = json.loads(response.content)
    print(data)
    print(data["data"]["msg"])


# curl 'https://weibo.cn/1776448504?display=0&retcode=6102'
# -H 'authority: weibo.cn'
# -H 'cache-control: max-age=0'
# -H 'upgrade-insecure-requests: 1'
# -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
# -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
# -H 'accept-encoding: gzip, deflate, br'
# -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7'
# -H 'cookie: SCF=Aj52M7AisY2zemY_Am0nKcL71Og-kwj4KrbW9HkL8O51er4-8_hatNoK5GhMB9THAX-jLQ5lBb1bhJdL4-4FbCU.; SUHB=0U1Zf5YC5ZOjsN; SSOLoginState=1530191206; ALF=1532783206; _T_WM=4c148c3fdf2acdf922c47fca32e3f91b'
# --compressed
def get_followers(cookie, name, username):

    def retrive_followers_content(cookie, username):
        url = "https://weibo.cn/%s?display=0&retcode=6102" % username
        headers = {
            "authority": "weibo.cn",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "Cookie": cookie.get_cookie()
        }
        response = requests.get(url, headers=headers)
        return response

    def extract_follower_from_content(content):
        selector = etree.HTML(content)
        str_gz = selector.xpath("//div[@class='tip2']/a/text()")[1]
        pattern = r"\d+\.?\d*"
        guid = re.findall(pattern, str_gz, re.M)
        followers = int(guid[0])
        return followers

    #username = "caizicaixukun"
    response = retrive_followers_content(cookie, username)
    if response is None:
        return None
    #start_time = response.start_time.strftime("%Y%m%d,%H:%M:%S.%f")
    #finish_time = response.finish_time.strftime("%Y%m%d,%H:%M:%S.%f")
    followers = extract_follower_from_content(response.content)
    # return start_time, finish_time, name, username, followers
    return name, username, followers


def get_all_followers(cookie):
    def print_follower_count_header(f):
        print("date,time,name,username,followers", file=f)

    date = datetime.date.today().strftime("%Y%m%d")
    filename = "%s_follower_counts.csv" % date

    usernames = []
    with open("weibo_ids.csv") as f:
        for line in f.readlines():
            segs = line.strip().split(",")
            name = segs[0].decode("GB2312").encode("utf-8")
            #name = segs[0]
            username = segs[1]
            if username == "id":
                continue
            usernames.append((name, username))

    is_file = os.path.isfile(filename)
    with open(filename, "a") as f:
        if not is_file:
            print_follower_count_header(f)
        for name, username in usernames:
            utils.log_print("[** LOG **] Get followers %s" % name)
            res = get_followers(cookie, name, username)
            if res is None:
                utils.log_print(
                    "[** ERROR LOG **] Failed getting followers %s" % name)
                date = datetime.date.today().strftime("%Y%m%d")
                time = datetime.datetime.now().strftime("%Y%m%d,%H:%M:%S.%f")
                with open(".%s_error.log" % date, "a") as f_err:
                    print("Failed", time, name, username, file=f_err)
            else:
                utils.log_print(
                    "[** LOG **] Succeed getting followers %s" % name)
                name, username, followers = res
                time = datetime.datetime.now().strftime("%Y%m%d,%H:%M:%S.%f")
                print("%s,%s,%s,%s" % (time, name, username, followers), file=f)
    return filename


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

# 获取明星势力榜的信息


def get_chart(cookie):

    headers = {
        "Host": "chart.weibo.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
        "Cookie": cookie.get_cookie()
    }

    date = datetime.date.today().strftime("%Y%m%d")
    filename = "%s_chart.csv" % date
    is_file = os.path.isfile(filename)
    with open(filename, "a") as f:
        if not is_file:
            print("date,time,name,read_number,interaction_number,affection_number,loveness_number", file=f)

        for rank in [3, 5, 6]:
            for page in [1, 2]:
                url = "http://chart.weibo.com/chart?rank_type=%s&page=%s" % (
                    rank, page)
                response = requests.get(url, headers=headers)
                if not response:
                    utils.log_print(
                        "[** ERROR LOG **] Failed getting chart with rank=%s and page=%s" % (rank, page))
                    continue

                soup = BeautifulSoup(response.content, "lxml")
                name_divs = soup.find_all(
                    "div", class_=re.compile("sr_name S_func1"))
                read_num_divs = soup.find_all(
                    "li", class_=re.compile("arr1 clearfix"))
                interaction_num_divs = soup.find_all(
                    "li", class_=re.compile("arr2 clearfix"))
                affection_num_divs = soup.find_all(
                    "li", class_=re.compile("arr3 clearfix"))
                loveness_num_divs = soup.find_all(
                    "li", class_=re.compile("arr4 clearfix"))
                for name_div, read_div, inter_div, affect_div, loveness_div in zip(name_divs, read_num_divs, interaction_num_divs, affection_num_divs, loveness_num_divs):
                    name = name_div.text.encode("utf-8")
                    read_num = read_div.find_all("span", class_="pro_num")[
                        0].text.encode("utf-8")
                    interaction_num = inter_div.find_all("span", class_="pro_num")[
                        0].text.encode("utf-8")
                    affection_num = affect_div.find_all("span", class_="pro_num")[
                        0].text.encode("utf-8")
                    loveness_num = loveness_div.find_all("span", class_="pro_num")[
                        0].text.encode("utf-8")
                    time = datetime.datetime.now().strftime("%Y%m%d,%H:%M:%S.%f")
                    utils.log_print(
                        "[** LOG **] Succeed getting chart %s" % name)
                    print("%s,%s,%s,%s,%s,%s" % (time, name, read_num, interaction_num, affection_num, loveness_num), file=f)


# 从微博页面获取单条微博的评论，赞，转发数量和上头条价格
def get_post_data(cookie, username, name, f):

    url = "https://weibo.cn/%s" % username
    response = requests.get(url)
    if not response:
        utils.log_print("[** ERROR LOG**] Failed to get weibo page %s" % url)
        return

    soup = BeautifulSoup(response.content, "lxml")
    for div in soup.find_all("div", class_="c"):
        if div.get("id") is None:
            continue

        div_id = div.get("id")
        assert div_id.startswith("M_")
        weibo_url = "https://www.weibo.com/%s/%s" % (username, div_id[2:])
        mid = url_to_mid(div_id[2:])
        url = "https://pay.biz.weibo.com/aj/getprice/advance?mid=%s&touid=%s" % (
            mid, username)
        headers = {
            "Host": "pay.biz.weibo.com",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "Cookie": cookie.get_cookie()
        }
        data = requests.get(url, headers=headers)
        if not data:
            utils.log_print(
                "[** ERROR LOG**] Failed to get weibo details %s" % url)
            continue

        data = json.loads(data.content)

        for a in div.find_all("a"):
            if a.text.encode("utf-8").startswith("评论"):
                comment = "".join(re.findall(
                    "[(\d+)]", a.text.encode("utf-8")))
            if a.text.encode("utf-8").startswith("赞"):
                up = "".join(re.findall("[(\d+)]", a.text.encode("utf-8")))
            if a.text.encode("utf-8").startswith("转发"):
                forward = "".join(re.findall(
                    "[(\d+)]", a.text.encode("utf-8")))
        try:
            time = datetime.datetime.now().strftime("%Y%m%d,%H:%M:%S.%f")
            utils.log_print("[** LOG **] Succeed getting post data %s" % name)
            print("%s,%s,%s,%s,%s,%s,%s,%s,%s" % (time, name, username, mid, comment, up, forward, data["data"]["price"], weibo_url), file=f)
        except:
            utils.log_print(
                "[** ERROR LOG **] Price is not available %s with mid=%s" % (name, mid))


def get_all_post_data(cookie):

    date = datetime.date.today().strftime("%Y%m%d")
    filename = "%s_post_data.csv" % date

    usernames = []
    with open("weibo_ids.csv") as f:
        for line in f.readlines():
            segs = line.strip().split(",")
            name = segs[0].decode("GB2312").encode("utf-8")
            #name = segs[0]
            username = segs[1]
            if username == "id":
                continue
            usernames.append((name, username))
    is_file = os.path.isfile(filename)
    with open(filename, "a") as f:
        if not is_file:
            print("date,time,name,username,mid,comment,up,forward,price,address", file=f)
        for name, username in usernames:
            utils.log_print("[** LOG **] Get post data %s, %s, %s" %
                            (name, username, cookie.get_cookie()))
            res = get_post_data(cookie, username, name, f)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process weibo")
    parser.add_argument("-u", "--username", type=str, required=True)
    parser.add_argument("-p", "--password", type=str, required=True)
    parser.add_argument("-m", "--mode", type=str, required=True,
                        choices=["chart", "post", "followers"])
    args = parser.parse_args()

    cookie = get_cookie(args.username, args.password)

    if args.mode == "chart":
        get_chart(cookie)
    elif args.mode == "post":
        get_all_post_data(cookie)
    elif args.mode == "followers":
        get_all_followers(cookie)
    else:
        assert False

    # page_id = "10080877197fd1ded939d5a32cac51e9200c47"  # 超话的页面id
    #get_sign_rank(cookie, page_id)
