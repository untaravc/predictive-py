from fastapi import Request
from app.services.ip_api_service import fetch_data_with_basic_auth
from app.configs.ind_power_conf import DATA_SERVER_WEB_ID, URL_POINT_SEARCH, URL_STREAM_INTERPOLATED, SAMPLE_WEB_ID, TABLE_SENSORS
from app.utils.oracle_db import fetch_one, execute_query

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
                "INSERT INTO "+ TABLE_SENSORS +" (ID, WEB_ID, NAME, PATH, DESCRIPTOR) VALUES (:id, :web_id, :name, :path, :descriptor)",
                {"id": items[i]["Id"], "web_id": items[i]["WebId"], "name": items[i]["Name"], "path": items[i]["Path"] ,"descriptor": items[i]["Descriptor"]}
            )
        else:
            execute_query(
                "UPDATE "+ TABLE_SENSORS +" SET WEB_ID = :web_id, NAME = :name, PATH = :path, DESCRIPTOR = :descriptor WHERE ID = :id",
                {"id": items[i]["Id"], "web_id": items[i]["WebId"], "name": items[i]["Name"], "path": items[i]["Path"], "descriptor": items[i]["Descriptor"]}
            )

    return {
            "success": True,
            "result": items
        }

async def point_interpolated(request: Request):
    query = dict(request.query_params)

    base_url = URL_STREAM_INTERPOLATED
    url = base_url + "/" + SAMPLE_WEB_ID + "/interpolated?startTime=" + query["startTime"] + "&endTime=" + query["endTime"] + "&interval=" + query["interval"]

    return {
        "success": True,
        "result": url
    }