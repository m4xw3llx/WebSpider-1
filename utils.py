# -*- coding: UTF-8 -*-
from __future__ import print_function
import requests
import json
import datetime
import sys


def log_print(string):

    date = datetime.date.today().strftime("%Y%m%d")
    time = datetime.datetime.now().strftime("%Y%m%d,%H:%M:%S.%f")

    filename = ".%s_simple_log.txt" % date
    with open(filename, "a") as f:
        print(time, string, file=f)
        print(time, string, file=sys.stderr)


def to_csv_line(*args):
    """Helper function to put outputs into ',' sperated csv format for future usage
    """

    return ",".join(str(v) for v in args)


def request(url, res_type, **kwargs):
    if "timeout" not in kwargs:
        kwargs["timeout"] = 10

    if res_type == "json":
        ResClass = JSONResponse
        request_behavior = requests.get
    elif res_type == "cookie":
        ResClass = CookieResponse
        request_behavior = requests.post
    elif res_type == "html":
        ResClass = HTMLResponse
        request_behavior = requests.get
    else:
        assert False, "wrong res_type %s" % res_type

    try:
        start_time = datetime.datetime.now()
        r = request_behavior(url, **kwargs)
        finish_time = datetime.datetime.now()
        result = ResClass(r, start_time, finish_time)
        log(result, r.url, res_type, kwargs)
    except requests.exceptions.ConnectTimeout as e:
        print("Timeout Error", e, file=sys.stderr)
        result = None
        log(result, url, res_type, kwargs)
    return result


def log(result, url, res_type, kwargs):
    date = datetime.date.today().strftime("%Y%m%d")
    filename = ".%s_log.txt" % date
    with open(filename, "a") as f:
        f.write("===== LOG ====\n")
        f.write("time: " + str(datetime.datetime.now()) + "\n")
        f.write("url: " + url + "\n")
        f.write("type: " + str(res_type) + "\n")
        for key, value in kwargs.items():
            f.write(key + ": " + str(value) + "\n")
        f.write("========================\n")
        if result is not None:
            f.write(result.r.content + "\n")
        else:
            f.write("FAILED!!!\n")


class Response(object):

    def __init__(self, r, start_time, finish_time):
        self.r = r
        self.start_time = start_time
        self.finish_time = finish_time


class JSONResponse(Response):

    def __init__(self, r, start_time, finish_time):
        super(JSONResponse, self).__init__(r, start_time, finish_time)

    def get_json_data(self):
        data = json.loads(self.r.content)

        if data["code"] == "A00000":
            data["start_time"] = self.start_time
            data["finish_time"] = self.finish_time
            return data
        else:
            print("Rejected request: ", self.r.url, file=sys.stderr)
            return None


class CookieResponse(Response):

    def __init__(self, r, start_time, finish_time):
        super(CookieResponse, self).__init__(r, start_time, finish_time)

    def get_cookie_data(self):
        cookies_infos = self.r.headers["Set-Cookie"]
        cookie_parts = []

        # The method to combine cookie info
        for info in cookies_infos.split():
            if info.startswith("SUB=") or info.startswith("SUHB=") or info.startswith("SCF=") or info.startswith("SSOLoginState="):
                cookie_parts.append(info)
        cookie = " ".join(cookie_parts)
        return {"Cookie": cookie}


class HTMLResponse(Response):

    def __init__(self, r, start_time, finish_time):
        super(HTMLResponse, self).__init__(r, start_time, finish_time)

    def get_html(self):
        return self.r.content
