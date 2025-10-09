from app.services.task_execute_service import execute_record_sample, execute_predict_sample, execute_record_api, execute_upload
from app.services.task_service import create_task_record, create_task_predict, create_task_upload, create_task_delete
from fastapi import Request
async def action_create_task_record():
    result = await create_task_record()
    return {
        "success": True,
        "result": result
    }

async def action_create_task_predict():
    result = await create_task_predict()
    return {
        "success": True,
        "result": result
    }

async def action_create_task_upload():
    result = await create_task_upload()
    return {
        "success": True,
        "result": result
    }

async def action_create_task_delete():
    result = await create_task_delete()
    return {
        "success": True,
        "result": result
    }

async def action_execute_record_sample(request: Request):
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
async def action_execute_record_api():
    result = await execute_record_api()
    return {
        "success": True,
        "result": result
    }

async def action_execute_upload():
    result = await execute_upload()
    return {
        "success": True,
        "result": result
    }