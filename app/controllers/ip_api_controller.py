from fastapi import Request
from app.archives.ip_api_service import fetch_data_with_basic_auth
# from app.configs.ind_power_conf import DATA_SERVER_WEB_ID, URL_POINT_SEARCH, URL_STREAM_INTERPOLATED
from app.configs.base_conf import settings
from app.utils.oracle_db import fetch_one, execute_query, fetch_all
from app.services.generator_service import run_generator_record
from app.archives.pi_vision_service import post_prediction_result
from collections import defaultdict
from app.configs.base_conf import settings
from app.statics.unit1_io import unit1_in

async def point_search(query: str = None):
    print("Point search...", query)

    base_url = settings.URL_POINT_SEARCH
    url = base_url +"?dataserverwebid="+settings.DATA_SERVER_WEB_ID+"&query=" + query

    response = await fetch_data_with_basic_auth(url)
    
    items = response['result']['Items']
    print("Items found: ", str(len(items)))
    for i in range(len(items)):
        status = 1
        if "prediksi" in items[i]["Name"].lower() or "tes" in items[i]["Name"].lower():
            status = 0
        # insert to db if not exist
        has_record = fetch_one("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE "+ settings.TABLE_SENSORS +".ID = :id", {"id": items[i]["Id"]})
        if(has_record == None):
            print("Inserting sensor ", items[i]["Name"])
            execute_query(
                "INSERT INTO "+ settings.TABLE_SENSORS +" (ID, WEB_ID, NAME, PATH, DESCRIPTOR, IS_ACTIVE, CREATED_AT, UPDATED_AT) VALUES (:id, :web_id, :name, :path, :descriptor, :status, SYSDATE, SYSDATE)",
                {"id": items[i]["Id"], "web_id": items[i]["WebId"], "name": items[i]["Name"], "path": items[i]["Path"] ,"descriptor": items[i]["Descriptor"], "status": status}
            )
        else:
            execute_query(
                "UPDATE "+ settings.TABLE_SENSORS +" SET WEB_ID = :web_id, NAME = :name, PATH = :path, DESCRIPTOR = :descriptor, UPDATED_AT = SYSDATE, IS_ACTIVE = :status WHERE ID = :id",
                {"id": items[i]["Id"], "web_id": items[i]["WebId"], "name": items[i]["Name"], "path": items[i]["Path"], "descriptor": items[i]["Descriptor"], "status": status}
            )

    unit1 = unit1_in()
    for i in range(len(unit1)):
        sensor = fetch_one("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE "+ settings.TABLE_SENSORS +".ID = :id", {"id": unit1[i]["id"]})
        if(sensor == None):
            print("Inserting sensor ", unit1[i]["name"])
            execute_query(
                "INSERT INTO "+ settings.TABLE_SENSORS +" (ID, WEB_ID, NAME, PATH, DESCRIPTOR, IS_ACTIVE, CREATED_AT, UPDATED_AT) VALUES (:id, :web_id, :name, :path, :descriptor, :status, SYSDATE, SYSDATE)",
                {"id": unit1[i]["id"], "web_id": "", "name": unit1[i]["name"], "path": "" ,"descriptor": "", "status": 1}
            )

    return {
            "success": True,
            "result": items
        }

async def point_interpolated_sample(request: Request):
    query = dict(request.query_params)

    base_url = settings.URL_STREAM_INTERPOLATED
    url = base_url + "/" + query["webId"] + "/interpolated?startTime=" + query["startTime"] + "&endTime=" + query["endTime"] + "&interval=" + query["interval"]

    sensor = fetch_one("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE "+ settings.TABLE_SENSORS +".WEB_ID = :web_id", {"web_id": query["webId"]})
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
            "SELECT * FROM " + settings.TABLE_RECORDS +
            " WHERE sensor_id = :sensor_id "
            "AND record_time = TO_DATE(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS')",
            {
                "sensor_id": sensor["ID"],
                "record_time": items[i]["Timestamp"]
            }
        )

        if(has_record == None):
            execute_query(
                "INSERT INTO " + settings.TABLE_RECORDS + 
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
                "UPDATE "+ settings.TABLE_RECORDS +" SET VALUE = :value, UPDATED_AT = SYSDATE WHERE ID = :id",
                {"value": value_num, "id": has_record["ID"]}
            )

    return {
        "success": True,
        "result": "Data updated"
    }

async def collect_interpolated(request: Request):
    # sensors = fetch_all("SELECT * FROM "+ TABLE_SENSORS +" FETCH FIRST 1 ROWS ONLY")
    sensors = fetch_all("SELECT * FROM "+ settings.TABLE_SENSORS +" WHERE WEB_ID = 'F1DP2dBunJOlC0ifiqTkEvHTBA3T0CAAUEkxXFNLUjEuVEhSVVNUIEJSRyAgTUVUQUwgMSBVMQ'")
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
        base_url = settings.URL_STREAM_INTERPOLATED
        url = base_url + "/" + sensor["WEB_ID"] + "/interpolated?startTime=" + startTime + "&endTime=" + endTime + "&interval=" + interval

        response = await fetch_data_with_basic_auth(url)

        items = response['result']['Items']

        for i in range(len(items)): 
            # insert to db if not exist
            val = items[i]['Value']
            value_num = val["Value"] if isinstance(val, dict) else val

            has_record = fetch_one(
                "SELECT * FROM " + settings.TABLE_RECORDS +
                " WHERE sensor_id = :sensor_id "
                "AND record_time = TO_DATE(:record_time, 'YYYY-MM-DD\"T\"HH24:MI:SS')",
                {
                    "sensor_id": sensor["ID"],
                    "record_time": items[i]["Timestamp"]
                }
            )

            if(has_record == None):
                execute_query(
                    "INSERT INTO " + settings.TABLE_RECORDS + 
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
                    "UPDATE "+ settings.TABLE_RECORDS +" SET VALUE = :value, UPDATED_AT = SYSDATE WHERE ID = :id",
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

async def sensor_list(request: Request):
    query = "SELECT * FROM "+ settings.TABLE_SENSORS

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

    query = "SELECT p.SENSOR_ID, p.RECORD_TIME, p.VALUE, s.NAME FROM "+ settings.TABLE_PREDICTIONS + " p left join "+ settings.TABLE_SENSORS +" s on p.SENSOR_ID = s.ID"

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
