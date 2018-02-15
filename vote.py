# -*- coding: UTF-8 -*-
from __future__ import print_function
import utils
import datetime
import os
# import sys


def get_options(data):
    return data["data"][0]["childs"][0]["options"]


def extract_option(option):
    start_time = data["start_time"].strftime("%Y%m%d,%H:%M:%S.%f")
    finish_time = data["finish_time"].strftime("%Y%m%d,%H:%M:%S.%f")
    name = option["text"].encode("utf-8").strip()  # encode utf-8 for chinese character strings
    showNum = option["showNum"]
    vipJoins = option["vipJoins"]
    return start_time, finish_time, name, showNum, vipJoins


def print_header(f):
    print(utils.to_csv_line("start_date", "start_time", "finish_date", "finish_time", "name", "gift", "vip_gift"),
          file=f)

if __name__ == "__main__":

    url = "http://vote.i.iqiyi.com/eagle/outer/get_votes?uid=null&vids=0536210296010472&t=1518343644386"
    response = utils.request(url, "json")
    data = response.get_json_data()

    options = get_options(data)

    time = datetime.date.today().strftime("%Y%m%d")
    filename = "%s_gift_counts.csv" % time
    is_file = os.path.isfile(filename)
    with open(filename, "a") as f:
        if not is_file:
            print_header(f)
        for option in options:
            print(utils.to_csv_line(*extract_option(option)), file=f)
