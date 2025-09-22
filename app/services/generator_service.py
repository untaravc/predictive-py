from datetime import datetime, timedelta
import random
from app.utils.oracle_db import execute_query, fetch_all
from app.configs.oracle_conf import TABLE_SENSORS, TABLE_RECORDS, TABLE_PREDICTIONS
from app.repo.normal_value import normal_value_unit3, normal_value_unit1

async def run_generator():
    # get sensors
    sensors = fetch_all("SELECT ID, NORMAL_VALUE FROM "+ TABLE_SENSORS +" WHERE NAME like '%SKR1%'")

    for sensor in sensors:

        if(sensor["NORMAL_VALUE"] == None):
            continue

        data_generate = await generate_values("2025-09-12 00:00:00", "2025-09-20 00:00:00", 5, sensor["NORMAL_VALUE"])

        query, params = build_merge_query(TABLE_PREDICTIONS, sensor["ID"], data_generate['data'])

        execute_query(query, params)

    return sensors

async def generate_values(date_from: str, date_to, period, normal_value: float):
    data = generate_timestamps(date_from, date_to, period, normal_value)

    return {
        "from": date_from,
        "to": date_to,
        "period": period,
        "data": data
    }

def generate_timestamps(from_date: str, to_date: str, period: int, normal_value: float):
    start = datetime.fromisoformat(from_date)
    end = datetime.fromisoformat(to_date)
    step = timedelta(minutes=period)
    
    timestamps = []
    current = start
    while current <= end:
        value_applied = random_within_percent(normal_value)
        timestamps.append({
            "Timestamp": current.isoformat(),
            "Value": value_applied
            })
        current += step
    
    return timestamps

def random_within_percent(value: float, percent: int = 10) -> float:
    lower = value * ((100 - percent) / 100)
    upper = value * ((100 + percent) / 100)
    return round(random.uniform(lower, upper), 2)

def set_normal_value():
    unit_1 = normal_value_unit1()

    for item in unit_1:
        print("update", item["ID"], item["NORMAL_VALUE"])
        execute_query("UPDATE "+ TABLE_SENSORS +" SET NORMAL_VALUE = :value WHERE ID = :id", {"value": item["NORMAL_VALUE"], "id": item["ID"]})

    return unit_1

# UPDATE ugm25_sensors
#     SET NORMAL_VALUE = CASE 
#                 WHEN ID = 10 THEN 0.2
#                 WHEN ID = 10 THEN 0.1
#                 ELSE salary
#                 END;
def set_normal_values():
    units = normal_value_unit3()

    sql_update = "UPDATE "+ TABLE_SENSORS +" SET NORMAL_VALUE = CASE "
    for item in units:
        sql_update += "WHEN ID = "+ str(item["ID"]) +" THEN "+ str(item["NORMAL_VALUE"]) +" "
    sql_update += "ELSE NORMAL_VALUE END"

    execute_query(sql_update)

    return units

def build_merge_query(table_name, sensor_id, items):
    """
    Build a single MERGE query for Oracle upsert.
    :param table_name: target table name (e.g., 'RECORDS')
    :param sensor_id: sensor ID (same for all items in your example)
    :param items: list of dicts with {"Timestamp": "...", "Value": ...}
    :return: (sql_query, params)
    """
    subqueries = []
    params = {}

    for i, item in enumerate(items):
        val = item["Value"]
        value_num = val["Value"] if isinstance(val, dict) else val

        subqueries.append(
            f"""
            SELECT :sensor_id{i} AS sensor_id,
                   TO_TIMESTAMP_TZ(:record_time{i}, 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS record_time,
                   :value{i} AS value
            FROM dual
            """
        )

        params[f"sensor_id{i}"] = sensor_id
        params[f"record_time{i}"] = item["Timestamp"]
        params[f"value{i}"] = value_num

    unioned = " UNION ALL ".join(subqueries)

    sql = f"""
    MERGE INTO {table_name} r
    USING (
        {unioned}
    ) t
    ON (r.sensor_id = t.sensor_id AND r.record_time = t.record_time)
    WHEN MATCHED THEN
        UPDATE SET r.value = t.value,
                   r.updated_at = SYSDATE
    WHEN NOT MATCHED THEN
        INSERT (sensor_id, record_time, value, created_at, updated_at)
        VALUES (t.sensor_id, t.record_time, t.value, SYSDATE, SYSDATE)
    """

    return sql, params
