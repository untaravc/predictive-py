from app.services.task_execute_service import execute_record_sample, execute_predict, execute_record_api, execute_upload
from app.services.task_service import create_task_record, create_task_predict, create_task_upload, task_delete, update_vibration
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

async def action_task_delete():
    result = await task_delete()
    return {
        "success": True,
        "result": result
    }

async def action_execute_record_sample():
    result = await execute_record_sample()
    return {
        "success": True,
        "result": result
    }

async def action_execute_predict():
    result = await execute_predict()
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

async def action_update_vibration():
    result = await update_vibration()
    return {
        "success": True,
        "result": result
    }