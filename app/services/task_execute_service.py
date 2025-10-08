from app.utils.oracle_db import fetch_all, execute_query, fetch_one
from app.configs.oracle_conf import TABLE_SENSORS, TABLE_TASKS
from app.services.generator_service import generate_timestamps, run_generator_record, run_generator_predict
from datetime import datetime, timedelta

RECORD_TIME_PERIOD = 1440 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
PREDICT_TIME_PERIOD = 1440 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
UPLOAD_TIME_PERIOD = 1440 # 60 = per jam, 24x per hari. 5 = per 5 menit, 288x per hari
SENSOR_NAME_QUERY = "SKR1%"
PREDICT_UNIT = 1

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