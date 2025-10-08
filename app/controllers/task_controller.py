from app.services.task_execute_service import execute_record_sample, execute_predict_sample
from fastapi import Request
async def action_create_task():
    # result = await create_task()
    return {
        "success": True,
        "result": "result"
    }

async def action_execute_record(request: Request):
    result = await execute_record_sample()
    return {
        "success": True,
        "result": result
    }

async def action_execute_predict(request: Request):
    result = await execute_predict_sample()
    return {
        "success": True,
        "result": result
    }