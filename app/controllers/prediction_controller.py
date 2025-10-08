from app.predictions.unit1_v1 import run_unit1_lstm_final, prepare_data_input
from fastapi import Request
async def consume_unit1_lstm(request: Request):
    days = request.query_params.get("days")

    result = await run_unit1_lstm_final(int(days))
    return {
        "success": True,
        "result": result
    }