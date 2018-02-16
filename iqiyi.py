# -*- coding: UTF-8 -*-
from __future__ import print_function
import utils
import datetime
import os


def get_count_by_name(qipuId, f):
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
        title = data["data"]["albumName"].encode("utf-8").strip()  # encode utf-8 for chinese character strings
        print(utils.to_csv_line(start_time, finish_time, title, qipuId, count), file=f)


def print_header(f):
    print(utils.to_csv_line("start_date", "start_time", "finish_date", "finish_time", "title", "qipuId", "count"),
          file=f)


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
        title = data["data"]["albumName"].encode("utf-8").strip()  # encode utf-8 for chinese character strings

        print(utils.to_csv_line(start_time, finish_time, title, qipuId, count), file=f)


if __name__ == "__main__":
    qipuIds = [922792900, 922529400, 922799800, 922795500, 922857600, 922890500, 922793800, 922759200,
               922783900, 922770600, 922733300, 922781600, 912602100, 919527300, 906523400]
    descs = ["【直拍】小组对决《PPAP》蔡徐坤", "【直拍】小组对决《大艺术家》陈立农", "【直拍】小组对决《Can't stop》范丞丞",
             "【直拍】小组对决《PPAP》朱正廷", "【直拍】小组对决《Can't stop》Justin", "【直拍】小组对决《Can't stop》灵超",
             "【直拍】小组对决《PPAP》王子异", "【直拍】小组对决《Dance to the music》木子洋",
             "【直拍】小组对决《半兽人》卜凡", "【直拍】小组对决《SHAKE》岳岳", "【直拍】小组对决《Dance to the music》朱星杰",
             "【直拍】小组对决《代号魂斗罗》杨非同", "张艺兴忆练习生经历落泪 王思聪公司惊艳炸裂男团",
             "主题曲舞台拉响C位争夺战", "百名练习生青春首秀张艺兴升级严厉制作人"]
    time = datetime.date.today().strftime("%Y%m%d")
    filename = "%s_vedio_watch_counts.csv" % time
    is_file = os.path.isfile(filename)
    with open(filename, "a") as f:
        if not is_file:
            print_header(f)
        for qipuId, desc in zip(qipuIds, descs):
            utils.log_print("[** LOG **] Run get_count_by_qipuId with %s" % qipuId)
            try:
                get_count_by_qipuId(qipuId, f)
                utils.log_print("[** LOG **] Succeed running get_count_by_qipuId with %s" % qipuId)
            except:
                utils.log_print("[** ERROR LOG **] Failed running get_count_by_qipuId with %s" % qipuId)
    print(filename)
