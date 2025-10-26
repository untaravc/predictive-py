from app.utils.oracle_db import fetch_all, execute_query, fetch_one
from app.services.generator_service import run_generator_record, build_merge_query
from datetime import datetime, timedelta
from app.archives.ip_api_service import fetch_data_with_basic_auth
import urllib3
from osisoft.pidevclub.piwebapi.pi_web_api_client import PIWebApiClient
from osisoft.pidevclub.piwebapi.models import PIAnalysis, PIItemsStreamValues, PIStreamValues, PITimedValue, PIRequest
from app.configs.base_conf import settings
from app.utils.helper import chunk_list
from app.predictions.unit1_v1 import run_unit1_lstm_final

async def execute_record_sample():
    tasks = fetch_all("SELECT * FROM "+ settings.TABLE_TASKS +" WHERE is_complete = 0 AND category = 'record' AND START_AT < SYSDATE FETCH FIRST 5 ROWS ONLY")
    print('Start execute_record_sample ', str(len(tasks)))
    
    for task in tasks:
        print("Generating record for sensor ", task["PARAMS"])
        date_from = (task["START_AT"] - timedelta(days=settings.RECORD_BACK_DATE)).strftime("%Y-%m-%d %H:%M:%S")
        date_to = task["START_AT"].strftime("%Y-%m-%d %H:%M:%S")
        period = 5
        await run_generator_record(task["PARAMS"], date_from, date_to, period)
        execute_query("UPDATE "+ settings.TABLE_TASKS +" SET is_complete = 2 WHERE id = :id", {"id": task["ID"]})

    return 'Record completed'

async def execute_record_api():
    print('Start execute_record_api')
    tasks = fetch_all("SELECT * FROM "+ settings.TABLE_TASKS +" WHERE is_complete != 1 AND category = 'record' AND PARAMS > 1000 AND START_AT < SYSDATE FETCH FIRST " + str(settings.RECORD_PER_SESSION) + " ROWS ONLY")
    print("Task found ", str(len(tasks)))

    for task in tasks:
        try:
            sensor = fetch_one("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE ID = :id", {"id": task["PARAMS"]})
            startTime = 't-'+ str(settings.RECORD_BACK_DATE) +'d'
            endTime = '*'
            interval = '5m'

            if settings.TIME_PRETEND != "":
                target = datetime.strptime(settings.TIME_PRETEND, "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                selisih = now - target
                hari = selisih.days

                startTime = 't-' + str(hari + settings.RECORD_BACK_DATE) + 'd'
                endTime = 't-' + str(hari) + 'd'
                interval = '5m'

            print('Start time ' + startTime + ' end time ' + endTime + ' interval ' + interval)

            url = settings.INTERPOLATED_URL + sensor["WEB_ID"] + "/interpolated?startTime=" + startTime + "&endTime=" + endTime + "&interval=" + interval
            result = await fetch_data_with_basic_auth(url)
            items = result['result']['Items']
            print('Result api ' + sensor["NAME"] + ' ' + str(sensor['ID']) + ': '  + str(len(items)) + ' items')

            insert_data = []
            for item in items:
                val = item['Value']
                value_num = 0 if isinstance(val, dict) else val

                ts = item.get("Timestamp", "")
                if ts.endswith("Z"):
                    ts = ts[:-1]

                insert_data.append({
                    "Timestamp": ts,
                    "Value": value_num
                })

            for i, chunk in enumerate(chunk_list(insert_data, 500), start=1):
                print(f"Processing batch {i} ({len(chunk)} records)")
                query, params = build_merge_query(settings.TABLE_RECORDS, sensor["ID"], chunk)

                execute_query(query, params)
            execute_query("UPDATE "+ settings.TABLE_TASKS +" SET is_complete = 1, UPDATED_AT = SYSDATE WHERE id = :id", {"id": task["ID"]})
        except:
            continue

    return {
        "sensor" : tasks
    }

async def execute_predict():
    print('Start execute_predict')
    tasks = fetch_all("SELECT * FROM "+ settings.TABLE_TASKS +" WHERE is_complete = 0 AND category = 'predict' AND START_AT < SYSDATE FETCH FIRST 1 ROWS ONLY")
    print('Tasks', len(tasks))

    for task in tasks:
        print("Generating predict for sensor ", task["PARAMS"])
        await run_unit1_lstm_final()
        execute_query("UPDATE "+ settings.TABLE_TASKS +" SET is_complete = 1, UPDATED_AT = SYSDATE WHERE id = :id", {"id": task["ID"]})

    return 'Predict completed'

async def execute_upload():
    print('Start execute_upload')
    # Run Over TASK
    tasks = fetch_all("SELECT * FROM "+ settings.TABLE_TASKS +" WHERE is_complete = 0 AND category = 'upload' AND START_AT < SYSDATE ORDER BY START_AT FETCH FIRST " + str(settings.UPLOAD_PERSESION) + " ROWS ONLY")

    for task in tasks:
        sensor = fetch_one("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE ID = :id", {"id": task["PARAMS"]})
        startTime = task["START_AT"].strftime("%Y-%m-%d %H:%M:%S")
        endTime = (task["START_AT"] + timedelta(days=settings.UPLOAD_PREDICT_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
        print("Start time ", startTime, " end time ", endTime)
        predictions = fetch_all("SELECT * FROM "+ settings.TABLE_PREDICTIONS +" WHERE SENSOR_ID = "  + str(sensor["ID"]) + " AND RECORD_TIME >= TO_DATE('" + startTime + "', 'YYYY-MM-DD HH24:MI:SS') AND RECORD_TIME <= TO_DATE('" + endTime + "', 'YYYY-MM-DD HH24:MI:SS')")
        
        client = getPIWebApiClient(settings.OSISOF_URL, settings.OSISOF_USER, settings.OSISOF_PASSWORD)
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        path = f"\\\\PI1\{sensor['NAME']}.prediksi"
        point1 = client.point.get_by_path(path, None)
        # point1 = client.point.get_by_path("\\\\PI1\SKR1.PRED.tes.prediksi", None)

        streamValue1 = PIStreamValues()
        
        values1 = list()
        streamValue1.web_id = point1.web_id
        total_data = len(predictions)
        for i in range(total_data):
            value1 = PITimedValue()
            value1.value = predictions[i]["VALUE"]
            value1.timestamp = predictions[i]["RECORD_TIME"].strftime("%Y-%m-%dT%H:%M:%SZ")
            values1.append(value1)

        print("Sensor Name: ", sensor['NAME'], "| Prediction data: ", total_data, "| Items ",len(values1))
        streamValue1.items = values1

        streamValues = list()
        streamValues.append(streamValue1)

        response = client.streamSet.update_values_ad_hoc_with_http_info(streamValues, None, None)
        print(response)
        execute_query("UPDATE "+ settings.TABLE_TASKS +" SET is_complete = 1, UPDATED_AT = SYSDATE WHERE id = :id", {"id": task["ID"]})

# Functions ==========

def getPIWebApiClient(webapi_url, usernme, psswrd):
    client = PIWebApiClient(webapi_url, False, 
                            username=usernme, password=psswrd, verifySsl=False)
    return client 