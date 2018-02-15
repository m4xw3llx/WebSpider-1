# -*- coding: UTF-8 -*-
from __future__ import print_function
import utils
import datetime
import os


def get_count_by_qipuId(qipuId, f):
    """Retrive title and playcounts given a qipuId
    """

    url_retrive_by_qipuId = "http://expand.video.iqiyi.com/api/album/info.json"
    apiKey = "71c300df4a7f4e89a43d8e19e5458e6f"
    params = {"apiKey": apiKey, "qipuId": str(qipuId)}

    response = utils.request(url_retrive_by_qipuId, "json", params=params)
    data = response.get_json_data()

    # r is None if the request failed.
    if data is not None:
        start_time = data["start_time"].strftime("%Y%m%d,%H:%M:%S.%f")
        finish_time = data["finish_time"].strftime("%Y%m%d,%H:%M:%S.%f")
        count = data["data"]["playcnt"]
        title = data["data"]["desc"].encode("utf-8").strip()  # encode utf-8 for chinese character strings

        print(utils.to_csv_line(start_time, finish_time, title, qipuId, count), file=f)


def print_header(f):
    print(utils.to_csv_line("start_date", "start_time", "finish_date", "finish_time", "title", "qipuId", "count"),
          file=f)


if __name__ == "__main__":
    time = datetime.date.today().strftime("%Y%m%d")
    filename = "%s_vedio_watch_counts.csv" % time
    is_file = os.path.isfile(filename)
    with open(filename, "a") as f:
        if not is_file:
            print_header(f)
        get_count_by_qipuId(922792900, f)
