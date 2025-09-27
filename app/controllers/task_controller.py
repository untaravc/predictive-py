from app.services.task_service import create_task, execute_record_sample, execute_predict_sample

async def action_create_task():
    result = await create_task()
    return {
        "success": True,
        "result": result
    }

async def action_execute_record():
    result = await execute_record_sample()
    return {
        "success": True,
        "result": result
    }

async def action_execute_predict():
    result = await execute_predict_sample()
    return {
        "success": True,
        "result": result
    }