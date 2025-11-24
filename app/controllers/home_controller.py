from fastapi import Request
from app.utils.oracle_db import execute_query

def home():
    return {
        "success": True,
        "result": {
            "title": "Predictive Prescriptive PLN Indonesia Power - UGM 2025.",
            "model": "v2",
            "last_update": "2025-10-18",
            "features": [
                "Create tasks",
                "Prediksi 1 Minggu",
            ]
        },
    }

def sql_statement(request: Request):
    statement = request.query_params.get("s")
    result = execute_query(statement)
    return {
        "success": True,
        "result": result
    }