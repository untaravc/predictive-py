from fastapi import Request
from app.services.ip_api_service import fetch_data_with_basic_auth
from app.configs.ind_power_conf import DATA_SERVER_WEB_ID, URL_POINT_SEARCH, URL_STREAM_INTERPOLATED
from app.configs.oracle_conf import TABLE_SENSORS, TABLE_RECORDS, TABLE_PREDICTIONS
from app.utils.oracle_db import fetch_one, execute_query, fetch_all
from app.services.generator_service import run_generator_record, set_normal_values
from app.services.unit3_service import run_unit3_lstm
from app.services.pi_vision_service import post_prediction_result
from tensorflow import keras
import numpy as np
from collections import defaultdict

async def point_seach(query: str):
    base_url = URL_POINT_SEARCH
    url = base_url +"?dataserverwebid="+DATA_SERVER_WEB_ID+"&query=" + query

    response = await fetch_data_with_basic_auth(url)

    if(response["success"] == False):
        return {
            "success": False,
            "error": response["error"]
        }
    
    items = response['result']['Items']

    for i in range(len(items)):
        # insert to db if not exist
        has_record = fetch_one("SELECT * FROM "+ TABLE_SENSORS +" WHERE "+ TABLE_SENSORS +".ID = :id", {"id": items[i]["Id"]})
        if(has_record == None):
            execute_query(
                "INSERT INTO "+ TABLE_SENSORS +" (ID, WEB_ID, NAME, PATH, DESCRIPTOR, IS_ACTIVE, CREATED_AT, UPDATED_AT) VALUES (:id, :web_id, :name, :path, :descriptor, 1, SYSDATE, SYSDATE)",
                {"id": items[i]["Id"], "web_id": items[i]["WebId"], "name": items[i]["Name"], "path": items[i]["Path"] ,"descriptor": items[i]["Descriptor"]}
            )
        else:
            execute_query(
                "UPDATE "+ TABLE_SENSORS +" SET WEB_ID = :web_id, NAME = :name, PATH = :path, DESCRIPTOR = :descriptor WHERE ID = :id, UPDATED_AT = SYSDATE",
                {"id": items[i]["Id"], "web_id": items[i]["WebId"], "name": items[i]["Name"], "path": items[i]["Path"], "descriptor": items[i]["Descriptor"]}
            )

    return {
            "success": True,
            "result": items
        }

async def point_interpolated_sample(request: Request):
    query = dict(request.query_params)

    base_url = URL_STREAM_INTERPOLATED
    url = base_url + "/" + query["webId"] + "/interpolated?startTime=" + query["startTime"] + "&endTime=" + query["endTime"] + "&interval=" + query["interval"]

    sensor = fetch_one("SELECT * FROM "+ TABLE_SENSORS +" WHERE "+ TABLE_SENSORS +".WEB_ID = :web_id", {"web_id": query["webId"]})
    if(sensor == None):
        return {
            "success": False,
            "error": "Sensor not found"
        }

    response = await fetch_data_with_basic_auth(url)

    items = response['result']['Items']

    for i in range(len(items)):
        
        val = items[i]['Value']
        value_num = val["Value"] if isinstance(val, dict) else val

        has_record = fetch_one(
            "SELECT * FROM " + TABLE_RECORDS +
            " WHERE sensor_id = :sensor_id "
            "AND record_time = TO_DATE(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS')",
            {
                "sensor_id": sensor["ID"],
                "record_time": items[i]["Timestamp"]
            }
        )

        if(has_record == None):
            execute_query(
                "INSERT INTO " + TABLE_RECORDS + 
                " (SENSOR_ID, RECORD_TIME, VALUE, CREATED_AT, UPDATED_AT) " +
                "VALUES (:sensor_id, TO_DATE(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS'), :value, SYSDATE, SYSDATE)",
                {
                    "sensor_id": sensor["ID"],
                    "record_time": items[i]["Timestamp"],
                    "value": value_num
                }
            )
        else:
            execute_query(
                "UPDATE "+ TABLE_RECORDS +" SET VALUE = :value, UPDATED_AT = SYSDATE WHERE ID = :id",
                {"value": value_num, "id": has_record["ID"]}
            )

    return {
        "success": True,
        "result": "Data updated"
    }

async def collect_interpolated(request: Request):
    # sensors = fetch_all("SELECT * FROM "+ TABLE_SENSORS +" FETCH FIRST 1 ROWS ONLY")
    sensors = fetch_all("SELECT * FROM "+ TABLE_SENSORS +" WHERE WEB_ID = 'F1DP2dBunJOlC0ifiqTkEvHTBA3T0CAAUEkxXFNLUjEuVEhSVVNUIEJSRyAgTUVUQUwgMSBVMQ'")
    startTime = "t-7d"
    endTime = "*"
    interval = "5m"

    if(request.query_params.get("startTime") != None):
        startTime = request.query_params.get("startTime")
    if(request.query_params.get("endTime") != None):
        endTime = request.query_params.get("endTime")
    if(request.query_params.get("interval") != None):
        interval = request.query_params.get("interval")

    for sensor in sensors:
        base_url = URL_STREAM_INTERPOLATED
        url = base_url + "/" + sensor["WEB_ID"] + "/interpolated?startTime=" + startTime + "&endTime=" + endTime + "&interval=" + interval

        response = await fetch_data_with_basic_auth(url)

        items = response['result']['Items']

        for i in range(len(items)): 
            # insert to db if not exist
            val = items[i]['Value']
            value_num = val["Value"] if isinstance(val, dict) else val

            has_record = fetch_one(
                "SELECT * FROM " + TABLE_RECORDS +
                " WHERE sensor_id = :sensor_id "
                "AND record_time = TO_DATE(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS')",
                {
                    "sensor_id": sensor["ID"],
                    "record_time": items[i]["Timestamp"]
                }
            )

            if(has_record == None):
                execute_query(
                    "INSERT INTO " + TABLE_RECORDS + 
                    " (SENSOR_ID, RECORD_TIME, VALUE, CREATED_AT, UPDATED_AT) " +
                    "VALUES (:sensor_id, TO_DATE(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS'), :value, SYSDATE, SYSDATE)",
                    {
                        "sensor_id": sensor["ID"],
                        "record_time": items[i]["Timestamp"],
                        "value": value_num
                    }
                )
            else:
                execute_query(
                    "UPDATE "+ TABLE_RECORDS +" SET VALUE = :value, UPDATED_AT = SYSDATE WHERE ID = :id",
                    {"value": value_num, "id": has_record["ID"]}
                )

    return {
            "success": True,
            "result": sensors
            }

async def generate_value_record():
    result = await run_generator_record(146888)
    return {
        "success": True,
        "result": result
    }

async def set_normal_value():
    result = set_normal_values()
    return {
        "success": True,
        "result": result
    }

async def consume_unit3_lstm():

    result = await run_unit3_lstm()

    for t, time in enumerate(result['timestamps']):
        for c, col in enumerate(result['columns']):
            val = result['values'][t][c]
            print(time, col, val)

    return {
        "success": True,
        "result": result
    }

async def sensor_list(request: Request):
    query = "SELECT * FROM "+ TABLE_SENSORS

    if(request.query_params.get("q") != None):
        query += " WHERE NAME like :q"
        q = request.query_params.get("q")
        sensors = fetch_all(query, {"q": q})
    else:
        sensors = fetch_all(query)

    return {
        "success": True,
        "result": sensors
    }

async def predictions(request: Request):

    query = "SELECT p.SENSOR_ID, p.RECORD_TIME, p.VALUE, s.NAME FROM "+ TABLE_PREDICTIONS + " p left join "+ TABLE_SENSORS +" s on p.SENSOR_ID = s.ID"

    query_where = []
    # if(request.query_params.get("sensorId") != None):
    #     query_where.append("sensor_id = :sensorId")

    if(request.query_params.get("startTime") != None):
        query_where.append("p.record_time >= TO_DATE(:startTime, 'YYYY-MM-DD\"T\"HH24:MI:SS')")

    if(request.query_params.get("endTime") != None):
        query_where.append("p.record_time <= TO_DATE(:endTime, 'YYYY-MM-DD\"T\"HH24:MI:SS')")

    if(request.query_params.get("sensorIds") != None):
        query_where.append("p.sensor_id IN (" + request.query_params.get("sensorIds") + ")")

    if(len(query_where) > 0):
        query += " WHERE " + " AND ".join(query_where)

    predictions = fetch_all(query, {
        # "sensorId": request.query_params.get("sensorId"),
        "startTime": request.query_params.get("startTime"),
        "endTime": request.query_params.get("endTime")
    })

    # group by RECORD_TIME
    grouped = defaultdict(list)

    for item in predictions:
        grouped[item["RECORD_TIME"]].append({
            "SENSOR_ID": item["SENSOR_ID"],
            "VALUE": item["VALUE"],
            "NAME": item["NAME"]
        })

# restructure
    result = []
    for time, sensors in grouped.items():
        result.append({
            "RECORD_TIME": time,
            "DATA": sensors
        })
    
    return {
        "success": True,
        "result": result
    }

async def access_interpolated_data_ip():
    # result = await get_interpolated_data()

    return {
        "success": True,
        "result": "result"
    }

async def post_interpolated_data_ip():
    result = await post_prediction_result()

    return {
        "success": True,
        "result": result
    }