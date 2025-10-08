from app.utils.oracle_db import fetch_all, execute_query, fetch_one
from app.configs.oracle_conf import TABLE_SENSORS, TABLE_TASKS
from app.services.generator_service import generate_timestamps, run_generator_record, run_generator_predict
from datetime import datetime, timedelta

RECORD_TIME_PERIOD = 1440 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
PREDICT_TIME_PERIOD = 1440 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
UPLOAD_TIME_PERIOD = 1440 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
SENSOR_NAME_QUERY = "SKR1%"
PREDICT_UNIT = 1

# Membuat task untuk pemanggilan API Record tiap sensor
# Membuat task untuk menjalankan model predict
async def create_task_record():
    print("create_task_record")
    sensors = fetch_all("SELECT * FROM "+ TABLE_SENSORS +" WHERE NAME like +'" + SENSOR_NAME_QUERY + "'")
    now = datetime.now()
    start = now.strftime("%Y-%m-%d 00:00:00")
    end = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    # RECORD
    for sensor in sensors:
        print("Start sensor ", sensor["ID"])
        timestamps = generate_timestamps(start, end, RECORD_TIME_PERIOD, sensor["NORMAL_VALUE"])
        query, params = build_insert_many(timestamps, sensor["ID"], "record")
        execute_query(query, params)

async def create_task_predict():
    print("create_task_predict")
    now = datetime.now()
    start = now.strftime("%Y-%m-%d 00:00:00")
    end = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            
    # PREDICT
    predict_timestamps = generate_timestamps(start, end, PREDICT_TIME_PERIOD, 0)
    predict_query, predict_params = build_insert_many(predict_timestamps, PREDICT_UNIT, "predict")
    execute_query(predict_query, predict_params)

async def create_task_upload():
    print("create_task_upload")
    now = datetime.now()
    sensors = fetch_all("SELECT * FROM "+ TABLE_SENSORS +" WHERE NAME like +'" + SENSOR_NAME_QUERY + "'")
    start = now.strftime("%Y-%m-%d 00:00:00")
    end = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            
    # UPLOAD
    print("Total sensors ", len(sensors))
    for sensor in sensors:
        timestamps = generate_timestamps(start, end, RECORD_TIME_PERIOD, sensor["NORMAL_VALUE"])
        query, params = build_insert_many(timestamps, sensor["ID"], "upload")
        execute_query(query, params)

async def create_delete_task():
    print("create_delete_task")
    execute_query("DELETE FROM "+ TABLE_TASKS +" WHERE is_complete = 1")

def build_insert_many(timestamps, params, category):
    base = """
    INSERT INTO ugm25_tasks (category, params, start_at, is_complete, created_at, updated_at)
    """
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
               TO_TIMESTAMP_TZ(:{key}, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS start_at,
               0 AS is_complete,
               SYSDATE AS created_at,
               SYSDATE AS updated_at
        FROM dual
        WHERE NOT EXISTS (
            SELECT 1
            FROM ugm25_tasks t
            WHERE t.category = :category
              AND t.params = :params
              AND t.start_at = TO_TIMESTAMP_TZ(:{key}, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
        )
        """)
    
    sql = base + "\nUNION ALL\n".join(selects)
    return sql, params