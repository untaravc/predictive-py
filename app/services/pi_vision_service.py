import time
# start = time.time()
# print("job DEPLOY SURALAYA8 FEGT PREDICTION FINALE mulai pada...",time.strftime("%d %b %Y %H:%M:%S"))

import pandas as pd 
from datetime import timedelta, datetime ,date
import urllib3
from osisoft.pidevclub.piwebapi.pi_web_api_client import PIWebApiClient
from osisoft.pidevclub.piwebapi.models import PIAnalysis, PIItemsStreamValues, PIStreamValues, PITimedValue, PIRequest
from app.configs.osisof_conf import OSISOF_USER, OSISOF_PASSWORD, OSISOF_URL

webapi = OSISOF_URL
username = OSISOF_USER
password = OSISOF_PASSWORD

def getPIWebApiClient(webapi_url, usernme, psswrd):
    client = PIWebApiClient(webapi_url, False, 
                            username=usernme, password=psswrd, verifySsl=False)
    return client

client = getPIWebApiClient(webapi, username, password)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# parent = "af:\\\\PIAF\Indonesia Power Corporate\BKT\SKR\SKR1|"
parent = "af:\\\\PIAF\Indonesia Power Corporate\SLA\SLA1|"

sensor = ['Generator Gross Capacity', 
          'Generator Net Capacity'] 
#           'BSR.FSH #94 ROW #1 TUBE WALL TEMP',
#           'BSR.FSH #02 ROW #1 TUBE WALL TEMP',
#           'BSR_COALFLOW.REAL', 
#           'BSR1.HP Turbine.Inlet Steam Temperature', 
#           'BSR1.HP Turbine.Inlet Steam Flow', 
#           'BSR_APHBINFLUEGAST.REAL', 
#           'BSR_APHAINFLUEGAST.REAL',  
#           'BSR.TOTAL AIRFLOW', 
#           'BSR1.HP Turbine.Inlet Steam Pressure', 
#           'Suralaya.8.1. Actual Water Spray to DeSH.5eb66636-c6f7-46e9-8803-c441a87a25a2',
#           'BSR.Furnace Exit Gas Temp']


paths = [parent + sensor[0],
         parent + sensor[1]]
#          parent + sensor[2],
#          parent + sensor[3],
#          parent + sensor[4],
#          parent + sensor[5],
#          parent + sensor[6],
#          parent + sensor[7],
#          parent + sensor[8],
#          parent + sensor[9],
#          parent + sensor[10],
#          parent + sensor[11],
#          parent + sensor[12]
#         ]

# Konfigurasi waktu
# Patokan start = 1 Juni 2020
start_date = '2019-01-01'

n_days = 1    # hari

# check apakah n_days
days_before = (date.today()-timedelta(days=n_days)).isoformat()
if days_before < start_date:
    print("Ganti jumlah hari!")

interval = 1    # 5 menit  
n_point = int(60 / interval * 24) # jumlah data dalam 1 hari

intervl = str(interval) + "m"
timestart = time.strftime("%d %b %Y %H:00:00")
start=timestart
end = '*'

df = client.data.get_multiple_interpolated_values(paths, start_time=start, end_time=end, interval=intervl)
df = df.sort_index(ascending=False)
df = df.reset_index()
df = df.drop(['index'], axis=1)

# ambil cukup 1 tanggal saja dan ambil value dari masing2 parameter
df.drop(columns=['Good1',
                      'Questionable1',
                      'Substituted1','UnitsAbbreviation1',
                      'Good2',
                      'Questionable2',
                      'Substituted2','UnitsAbbreviation2','Timestamp2'], inplace=True)
#                       'Good3',
#                       'Questionable3',
#                       'Substituted3','UnitsAbbreviation3','Timestamp3',
#                       'Good4',
#                       'Questionable4',
#                       'Substituted4','UnitsAbbreviation4','Timestamp4',
#                       'Good5',
#                       'Questionable5',
#                       'Substituted5','UnitsAbbreviation5','Timestamp5',
#                       'Good6',
#                       'Questionable6',
#                       'Substituted6','UnitsAbbreviation6','Timestamp6',
#                       'Good6',
#                       'Questionable7',
#                       'Substituted7','UnitsAbbreviation7','Timestamp7',
#                       'Good7',
#                       'Questionable8',
#                       'Substituted8','UnitsAbbreviation8','Timestamp8',
#                       'Good8',
#                       'Good9',
#                       'Questionable9',
#                       'Substituted9','UnitsAbbreviation9','Timestamp9',
#                       'Good10',
#                       'Questionable10',
#                       'Substituted10','UnitsAbbreviation10','Timestamp10',
#                       'Good11',
#                       'Questionable11',
#                       'Substituted11','UnitsAbbreviation11','Timestamp11',
#                       'Good12',
#                       'Questionable12',
#                       'Substituted12','UnitsAbbreviation12','Timestamp12',
#                       'Good13',
#                       'Questionable13',
#                       'Substituted13','UnitsAbbreviation13','Timestamp13'], inplace=True)
df

#proses upload data
# ==================

total_data = len(df.index)

def upload_prediksi(total_data,df):
    streamValue1 = PIStreamValues()
    
    values1 = list()

    for i in range(total_data):
        value1 = PITimedValue()
        value1.value = df_tes['predict'][i] 
        value1.timestamp = df_tes['current_time'][i] 
        streamValue1.web_id = point1.web_id
        values1.append(value1)

    streamValue1.items = values1

    streamValues = list()
    streamValues.append(streamValue1)

    response = client.streamSet.update_values_ad_hoc_with_http_info(streamValues, None, None)

    return response
    
point1 = client.point.get_by_path("\\\\PI1\SKR1.PRED.tes.prediksi", None)
upload_prediksi(total_data,df_tes)
result_upload_predict = upload_prediksi(total_data,df_tes)

print('\n -->  response upload predict PI 1: ', 'Deploy Success ' if result_upload_predict[1] == 202 else 'gagal')