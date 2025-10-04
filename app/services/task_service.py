from app.utils.oracle_db import fetch_all, execute_query, fetch_one
from app.configs.oracle_conf import TABLE_SENSORS, TABLE_TASKS
from app.services.generator_service import generate_timestamps, run_generator_record, run_generator_predict
from datetime import datetime, timedelta

RECORD_TIME_PERIOD = 60 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
PREDICT_TIME_PERIOD = 60 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
UPLOAD_TIME_PERIOD = 60 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
SENSOR_NAME_QUERY = "SKR1%"
PREDICT_UNIT = 1

# Membuat task untuk pemanggilan API Record tiap sensor
# Membuat task untuk menjalankan model predict
async def create_task():
    sensors = fetch_all("SELECT * FROM "+ TABLE_SENSORS +" WHERE NAME like +'" + SENSOR_NAME_QUERY + "'")
    now = datetime.now()
    start = now.strftime("%Y-%m-%d 00:00:00")
    end = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    # RECORD
    # for sensor in sensors:
    #     timestamps = generate_timestamps(start, end, RECORD_TIME_PERIOD, sensor["NORMAL_VALUE"])
    #     query, params = build_insert_many(timestamps, sensor["ID"], "record")
    #     execute_query(query, params)
            
    # # PREDICT
    # predict_timestamps = generate_timestamps(start, end, PREDICT_TIME_PERIOD, 0)
    # predict_query, predict_params = build_insert_many(predict_timestamps, PREDICT_UNIT, "predict")
    # execute_query(predict_query, predict_params)

    # # UPLOAD
    # upload_timestamps = generate_timestamps(start, end, UPLOAD_TIME_PERIOD, 0)
    # upload_query, upload_params = build_insert_many(upload_timestamps, PREDICT_UNIT, "upload")
    # execute_query(upload_query, upload_params)

    # DELETE TASK COMPLETED
    past_day = (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    delete_query = "DELETE FROM "+ TABLE_TASKS +" WHERE is_complete = 1 AND START_AT <  + TO_TIMESTAMP_TZ('" + past_day + "', 'YYYY-MM-DD HH24:MI:SS')"
    execute_query(delete_query)

    return 'OK'

async def execute_record_sample(date_from: str = None, date_to: str = None, period: int = None):
    if(date_from == None):
        date_from = datetime.now().strftime("%Y-%m-%d 00:00:00")
    if(date_to == None):
        date_to = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    if(period == None):
        period = 60

    # Run Over TASK
    # tasks = fetch_all("SELECT * FROM "+ TABLE_TASKS +" WHERE is_complete = 0 AND category = 'record' AND START_AT < SYSDATE FETCH FIRST 2 ROWS ONLY")
    # for task in tasks:
    #     await run_generator_record(task["PARAMS"])
    #     execute_query("UPDATE "+ TABLE_TASKS +" SET is_complete = 1 WHERE id = :id", {"id": task["ID"]})

    # Run Over SENSORS (Dev Mode)
    sensors = fetch_all("SELECT * FROM "+ TABLE_SENSORS +" WHERE NAME like +'" + SENSOR_NAME_QUERY + "'")
    for sensor in sensors:
        await run_generator_record(sensor["ID"], date_from, date_to, period)

    return 'Record completed'

async def execute_hit_api():
    pass

async def execute_predict_sample(date_from: str = None, date_to: str = None, period: int = None):
    if(date_from == None):
        date_from = datetime.now().strftime("%Y-%m-%d 00:00:00")
    if(date_to == None):
        date_to = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    if(period == None):
        period = 60

    # task = fetch_one("SELECT * FROM "+ TABLE_TASKS +" WHERE is_complete = 0 AND category = 'predict' AND START_AT < SYSDATE")
    # if(task):
    #     await run_generator_predict(date_from, date_to, period)
    #     execute_query("UPDATE "+ TABLE_TASKS +" SET is_complete = 1 WHERE id = :id", {"id": task["ID"]})

    await run_generator_predict(date_from, date_to, period)
    return 'Predict completed'

async def execute_predict():
    pass

async def execute_upload():
    pass

# Generate query to insert task, a sensor many timestamp in one query
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