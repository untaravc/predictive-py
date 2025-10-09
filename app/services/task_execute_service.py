from app.utils.oracle_db import fetch_all, execute_query, fetch_one
from app.configs.oracle_conf import TABLE_SENSORS, TABLE_TASKS
from app.services.generator_service import run_generator_record, run_generator_predict, build_merge_query
from datetime import datetime, timedelta
from app.services.ip_api_service import fetch_data_with_basic_auth
from app.configs.oracle_conf import TABLE_SENSORS, TABLE_RECORDS, TABLE_PREDICTIONS, TABLE_TASKS
import urllib3
from osisoft.pidevclub.piwebapi.pi_web_api_client import PIWebApiClient
from osisoft.pidevclub.piwebapi.models import PIAnalysis, PIItemsStreamValues, PIStreamValues, PITimedValue, PIRequest
from app.configs.osisof_conf import OSISOF_USER, OSISOF_PASSWORD, OSISOF_URL

RECORD_TIME_PERIOD = 1440 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
PREDICT_TIME_PERIOD = 1440 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
UPLOAD_TIME_PERIOD = 1440 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
SENSOR_NAME_QUERY = "SKR1%"
PREDICT_UNIT = 1
RECORD_BACK_DATE=7
INTERPOLATED_URL="https://pivision.plnindonesiapower.co.id/piwebapi/streams/"
UPLOAD_PREDICT_DAYS=50

async def execute_record_sample():
    # Run Over TASK
    tasks = fetch_all("SELECT * FROM "+ TABLE_TASKS +" WHERE is_complete = 0 AND category = 'record' AND START_AT < SYSDATE FETCH FIRST 1 ROWS ONLY")
    for task in tasks:
        date_from = task["START_AT"].strftime("%Y-%m-%d %H:%M:%S")
        date_to = (task["START_AT"] + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        period = 5
        await run_generator_record(task["PARAMS"], date_from, date_to, period)
        execute_query("UPDATE "+ TABLE_TASKS +" SET is_complete = 1 WHERE id = :id", {"id": task["ID"]})

    return 'Record completed'

async def execute_record_api():
    print('Start execute_record_api')
    tasks = fetch_all("SELECT * FROM "+ TABLE_TASKS +" WHERE is_complete = 0 AND category = 'record' AND PARAMS > 1000 AND START_AT < SYSDATE FETCH FIRST 1 ROWS ONLY")

    for task in tasks:
        try:
            sensor = fetch_one("SELECT * FROM "+ TABLE_SENSORS +" WHERE ID = :id", {"id": task["PARAMS"]})
            startTime = 't-'+ str(RECORD_BACK_DATE) +'d'
            endTime = '*'
            interval = '5m'

            url = INTERPOLATED_URL + sensor["WEB_ID"] + "/interpolated?startTime=" + startTime + "&endTime=" + endTime + "&interval=" + interval
            result = await fetch_data_with_basic_auth(url)
            items = result['result']['Items']
            print('Result api ' + sensor["NAME"] + ' ' + str(sensor['ID']) + ': '  + str(len(items)) + ' items')

            insert_data = []
            for i in range(len(items)):
                val = items[i]['Value']
                value_num = 0 if isinstance(val, dict) else val

                insert_data.append({
                    "Timestamp": items[i]["Timestamp"],
                    "Value": value_num
                })

            # chunk 500
            for i, chunk in enumerate(chunk_list(insert_data, 500), start=1):
                print(f"Processing batch {i} ({len(chunk)} records)")
                query, params = build_merge_query(TABLE_RECORDS, sensor["ID"], chunk)
                execute_query(query, params)
            execute_query("UPDATE "+ TABLE_TASKS +" SET is_complete = 1 WHERE id = :id", {"id": task["ID"]})
        except:
            continue

    return {
        "sensor" : tasks
    }

async def execute_predict_sample(date_from: str = None, date_to: str = None, period: int = None):
    pass

async def execute_predict():
    pass

async def execute_upload():
    print('Start execute_upload')
    # Run Over TASK
    tasks = fetch_all("SELECT * FROM "+ TABLE_TASKS +" WHERE is_complete = 0 AND category = 'upload' AND START_AT < SYSDATE FETCH FIRST 1 ROWS ONLY")

    for task in tasks:
        sensor = fetch_one("SELECT * FROM "+ TABLE_SENSORS +" WHERE ID = :id", {"id": task["PARAMS"]})
        startTime = (task["START_AT"] - timedelta(days=UPLOAD_PREDICT_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
        sensor["ID"] = 146867
        predictions = fetch_all("SELECT * FROM "+ TABLE_PREDICTIONS +" WHERE SENSOR_ID = "  + str(sensor["ID"]) + " AND RECORD_TIME >= TO_TIMESTAMP_TZ('" + startTime + "', 'YYYY-MM-DD HH24:MI:SS')")

        print(predictions[0:2])
        client = getPIWebApiClient(OSISOF_URL, OSISOF_USER, OSISOF_PASSWORD)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # path = f"\\\\PI1\{sensor['NAME']}.prediksi"
        # point1 = client.point.get_by_path(path, None)
        point1 = client.point.get_by_path("\\\\PI1\SKR1.PRED.tes.prediksi", None)
        
        total_data = len(predictions)

        streamValue1 = PIStreamValues()

        values1 = list()
        streamValue1.web_id = point1.web_id

        for i in range(len(predictions)):
            value1 = PITimedValue()
            value1.value = predictions[i]["VALUE"]
            value1.timestamp = predictions[i]["RECORD_TIME"].strftime("%Y-%m-%dT%H:%M:%SZ")
            print(value1.timestamp)
            values1.append(value1)

        streamValue1.items = values1

        streamValues = list()
        streamValues.append(streamValue1)

        response = client.streamSet.update_values_ad_hoc_with_http_info(streamValues, None, None)

        print(response)

# Functions ==========
def chunk_list(data, size):
    for i in range(0, len(data), size):
        yield data[i:i + size]

def getPIWebApiClient(webapi_url, usernme, psswrd):
    client = PIWebApiClient(webapi_url, False, 
                            username=usernme, password=psswrd, verifySsl=False)
    return client 