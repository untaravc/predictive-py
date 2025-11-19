from app.utils.oracle_db import fetch_all, execute_query, fetch_one
from app.services.generator_service import generate_timestamps
from datetime import datetime, timedelta
from app.configs.lstm_conf import lstm_config
from app.configs.base_conf import settings
from app.services.vibration_proccess_service import process_excel
import os
import pandas as pd
import re

# Membuat task untuk pemanggilan API Record tiap sensor
# Membuat task untuk menjalankan model predict
async def create_task_record():
    print("Service: create_task_record", settings.TABLE_SENSORS, settings.SENSOR_NAME_QUERY)
    sensors = fetch_all("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE NAME like +'" + settings.SENSOR_NAME_QUERY + "' AND WEB_ID IS NOT NULL AND IS_ACTIVE = 1")
    now = datetime.now()

    if settings.TIME_PRETEND != "":
        now = datetime.strptime(settings.TIME_PRETEND, "%Y-%m-%d %H:%M:%S")

    start = now.strftime("%Y-%m-%d 00:00:00")
    end = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    for sensor in sensors:
        print("Start sensor ", sensor["ID"])
        timestamps = generate_timestamps(start, end, settings.RECORD_TIME_PERIOD, 0)
        query, params = build_insert_many(timestamps, sensor["ID"], "record")
        execute_query(query, params)

    return "Success"

async def create_task_predict():
    print("Service: create_task_predict")
    now = datetime.now()

    if settings.TIME_PRETEND != "":
        now = datetime.strptime(settings.TIME_PRETEND, "%Y-%m-%d %H:%M:%S")

    start = now.strftime("%Y-%m-%d 00:00:00")
    end = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    print("Start predict ", start, end, settings.PREDICT_TIME_PERIOD)
    predict_timestamps = generate_timestamps(start, end, settings.PREDICT_TIME_PERIOD, 0)

    for i in range(1, 5):
        predict_query, predict_params = build_insert_many(predict_timestamps, i, "predict")
        execute_query(predict_query, predict_params)

    return "Success"

async def update_vibration():
    folder_path = settings.VIBRATION_FOLDER_PATH

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            print("File: ", file)

            file_numbers = re.findall(r'\d+', file)  # find all digit groups
            if file_numbers:
                number_str = file_numbers[0]  # "202507"
                file_number = int(number_str)

            has_processed = fetch_one("SELECT * FROM "+ settings.TABLE_TASKS +" WHERE PARAMS = :file_number AND CATEGORY = 'vibration'", {"file_number": file_number})
            if has_processed is not None:
                print("File already processed")
                continue
            file_path = os.path.join(root, file)
            df = pd.read_excel(file_path)

            process_excel(df)

            query = "INSERT INTO " + settings.TABLE_TASKS + " (category, params, start_at, is_complete, created_at, updated_at) VALUES ('vibration', :file_number, SYSDATE, 1, SYSDATE, SYSDATE)"
            params = {"file_number": file_number}
            execute_query(query, params)

    return "Success"

async def create_task_upload():
    print("Service: create_task_upload")
    now = datetime.now()

    if settings.TIME_PRETEND != "":
        now = datetime.strptime(settings.TIME_PRETEND, "%Y-%m-%d %H:%M:%S")

    sensors = fetch_all("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE NAME like +'" + settings.SENSOR_NAME_QUERY + "'")
    start = now.strftime("%Y-%m-%d 00:00:00")
    end = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    for sensor in sensors:
        if sensor['NAME'] in UNIT1_TARGET_COLS:
            print(sensor['NAME'])
            timestamps = generate_timestamps(start, end, settings.UPLOAD_TIME_PERIOD, 0)
            query, params = build_insert_many(timestamps, sensor["ID"], "upload")

            execute_query(query, params)
            print("Upload task ", sensor["ID"])

    return "Success"

async def task_delete():
    print("Service: delete_task")
    execute_query("DELETE FROM "+ settings.TABLE_TASKS +" WHERE is_complete = 1")

def build_insert_many(timestamps, params, category):
    base = "INSERT INTO " + settings.TABLE_TASKS + " (category, params, start_at, is_complete, created_at, updated_at)"
    selects = []
    params = {"params": params, "category": category}

    for i, ts in enumerate(timestamps):
            key = f"ts{i}"
            if not ts["Timestamp"]:
                raise ValueError(f"Timestamp missing at index {i}")
            params[key] = ts["Timestamp"]
    
    for i, ts in enumerate(timestamps):
        key = f"ts{i}"
        params[key] = ts["Timestamp"]
        
        selects.append(f"""
        SELECT :category AS category,
               :params AS params,
               TO_DATE(:{key}, 'YYYY-MM-DD"T"HH24:MI:SS') AS start_at,
               0 AS is_complete,
               SYSDATE AS created_at,
               SYSDATE AS updated_at
        FROM dual
        WHERE NOT EXISTS (
            SELECT 1
            FROM {settings.TABLE_TASKS} t
            WHERE t.category = :category
              AND t.params = :params
              AND t.start_at = TO_DATE(:{key}, 'YYYY-MM-DD"T"HH24:MI:SS')
        )
        """)
    
    sql = base + "\nUNION ALL\n".join(selects)
    return sql, params