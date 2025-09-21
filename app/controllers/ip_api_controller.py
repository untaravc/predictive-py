from fastapi import Request
from app.services.ip_api_service import fetch_data_with_basic_auth
from app.configs.ind_power_conf import DATA_SERVER_WEB_ID, URL_POINT_SEARCH, URL_STREAM_INTERPOLATED
from app.configs.oracle_conf import TABLE_SENSORS, TABLE_RECORDS
from app.utils.oracle_db import fetch_one, execute_query, fetch_all
from app.services.generator_service import run_generator, set_normal_values

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
            "AND record_time = TO_TIMESTAMP_TZ(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')",
            {
                "sensor_id": sensor["ID"],
                "record_time": items[i]["Timestamp"]
            }
        )

        if(has_record == None):
            execute_query(
                "INSERT INTO " + TABLE_RECORDS + 
                " (SENSOR_ID, RECORD_TIME, VALUE, CREATED_AT, UPDATED_AT) " +
                "VALUES (:sensor_id, TO_TIMESTAMP_TZ(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"'), :value, SYSDATE, SYSDATE)",
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
                "AND record_time = TO_TIMESTAMP_TZ(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"')",
                {
                    "sensor_id": sensor["ID"],
                    "record_time": items[i]["Timestamp"]
                }
            )

            if(has_record == None):
                execute_query(
                    "INSERT INTO " + TABLE_RECORDS + 
                    " (SENSOR_ID, RECORD_TIME, VALUE, CREATED_AT, UPDATED_AT) " +
                    "VALUES (:sensor_id, TO_TIMESTAMP_TZ(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS\"Z\"'), :value, SYSDATE, SYSDATE)",
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
    result = await run_generator()
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