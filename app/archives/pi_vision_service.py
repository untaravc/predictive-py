import time

import pandas as pd 
from datetime import timedelta, datetime ,date
import urllib3
from osisoft.pidevclub.piwebapi.pi_web_api_client import PIWebApiClient
from osisoft.pidevclub.piwebapi.models import PIAnalysis, PIItemsStreamValues, PIStreamValues, PITimedValue, PIRequest
# from app.configs.osisof_conf import OSISOF_USER, OSISOF_PASSWORD, OSISOF_URL

webapi = "https://piwebapi.plnindonesiapower.co.id/piwebapi"
username = "pisystem"
password = "Abcd1234!"

def getPIWebApiClient(webapi_url, usernme, psswrd):
    client = PIWebApiClient(webapi_url, False, 
                            username=usernme, password=psswrd, verifySsl=False)
    return client   

# async def get_interpolated_data():
#     client = getPIWebApiClient(webapi, username, password)
    # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # raw string (paling ringkas)
    # path = "af:\\\\PIAF\\Indonesia Power Corporate\\SLA\\SLA1|Generator Gross Capacity"
    # # path = "pi:\\\\PI1?9c6ed0d9-a593-480b-9f8a-a4e412f1d304\\SKR1.110VDC Voltage Busbar A?146864"

    # print(path)
    # response = client.data.get_multiple_interpolated_values(
    #     [path],
    #     "2025-06-01",
    #     "2025-06-02",
    #     "1h"
    # )

    # point1 = client.point.get_by_path("\\\\PI1\SKR1.PRED.tes.prediksi", None)
    # point1 = client.point.get_by_path(r"\\PI1\SKR1.PRED.tes.prediksi", None)

    # print(point1)
    # return point1.web_id

    # parent = "af:\\\\PIAF\Indonesia Power Corporate\SLA\SLA1|"
    # # parent = "af:\\\\PIAF\Indonesia Power Corporate\\PI1|"

    # paths = []

    # sensor = ['Generator Gross Capacity', 
    #       'Generator Net Capacity'] 

    # paths = [parent + sensor[0],
    #      parent + sensor[1]]

    # print(paths)

    # # Konfigurasi waktu
    # # Patokan start = 1 Juni 2020
    # start_date = '2025-09-28'
    # n_days = 1   # hari

    # # check apakah n_days
    # days_before = (date.today()-timedelta(days=n_days)).isoformat()
    # if days_before < start_date:
    #     print("Ganti jumlah hari!")

    # interval = 60    # 5 menit  
    # n_point = int(60 / interval * 24) # jumlah data dalam 1 hari: 288

    # intervl = str(interval) + "m"
    # timestart = time.strftime("%d %b %Y %H:00:00")
    # start=timestart
    # end = '*'

    # df = client.data.get_multiple_interpolated_values(paths, start_time=start, end_time=end, interval=intervl)
    # df = df.sort_index(ascending=False)
    # df = df.reset_index()
    # df = df.drop(['index'], axis=1)

    # # ambil cukup 1 tanggal saja dan ambil value dari masing2 parameter
    # df.drop(columns=['Good1',
    #                     'Questionable1',
    #                     'Substituted1','UnitsAbbreviation1',
    #                     'Good2',
    #                     'Questionable2',
    #                     'Substituted2','UnitsAbbreviation2','Timestamp2'], inplace=True)
    # return df

def post_prediction_result():
    client = getPIWebApiClient(webapi, username, password)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # point1 = client.point.get_by_path("\\\\PI1\SKR1.PRED.tes.prediksi", None)
    point1 = client.point.get_by_path("\\\\PI1\SKR1.PRED.tes.prediksi", None)

    # total_data = len(df.index)
    total_data = 11

    streamValue1 = PIStreamValues()

    values1 = list()
    streamValue1.web_id = point1.web_id
    print(point1.web_id)

    for i in range(total_data):
        value1 = PITimedValue()
        value1.value = 67 + i
        time_minute_str = '00'
        if(i < 10):
            time_minute_str = '0' + str(i)
        else:
            time_minute_str = str(i)

        timestamp = '2025-09-29T' + time_minute_str + ':00:00.000Z'
        value1.timestamp = timestamp
        print(timestamp)
        values1.append(value1)

    streamValue1.items = values1

    streamValues = list()
    streamValues.append(streamValue1)

    print(streamValues)

    response = client.streamSet.update_values_ad_hoc_with_http_info(streamValues, None, None)

    print(response)
    return "values1"