from app.services.task_service import create_task, execute_record_sample, execute_predict_sample
from fastapi import Request
async def action_create_task():
    result = await create_task()
    return {
        "success": True,
        "result": result
    }

async def action_execute_record(request: Request):
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")
    period = request.query_params.get("period")

    result = await execute_record_sample(date_from, date_to, int(period))
    return {
        "success": True,
        "result": result
    }

async def action_execute_predict(request: Request):
    date_from = request.query_params.get("date_from")
    date_to = request.query_params.get("date_to")
    period = request.query_params.get("period")

    result = await execute_predict_sample(date_from, date_to, int(period))
    return {
        "success": True,
        "result": result
    }