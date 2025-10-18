from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.task_service import create_task_record, create_task_predict, create_task_upload, task_delete
from app.services.task_execute_service import execute_record_api, execute_upload, execute_predict
from app.controllers.ip_api_controller import point_search
from dotenv import load_dotenv
from app.configs.base_conf import settings

load_dotenv()
scheduler = AsyncIOScheduler()

async def lifespan(app: FastAPI):
    # await point_search()
    # await create_task_record()
    # await create_task_predict()
    scheduler.start()
    if settings.RUN_SCHEDULER == "true":
        if not scheduler.get_job("execute_record_api"):
            scheduler.add_job(
                execute_record_api,
                CronTrigger.from_crontab("* * * * *"), # every minute
                id="execute_record_api",
                replace_existing=True
            )

        if not scheduler.get_job("execute_upload"):
            scheduler.add_job(
                execute_upload,
                CronTrigger.from_crontab("* * * * *"), # every minute
                id="execute_upload",
                replace_existing=True
            )
        
        if not scheduler.get_job("execute_predict"):
            scheduler.add_job(
                execute_predict,
                CronTrigger.from_crontab("0 * * * *"), # every hours
                id="execute_predict",
                replace_existing=True
            )

        if not scheduler.get_job("create_task_record"):
            scheduler.add_job(
                create_task_record,
                CronTrigger.from_crontab("0 0 * * *"), # daily at 00:00
                id="create_task_record",
                replace_existing=True
            )

        if not scheduler.get_job("create_task_predict"):
            scheduler.add_job(
                create_task_predict,
                CronTrigger.from_crontab("0 0 * * *"), # daily at 00:00
                id="create_task_predict",
                replace_existing=True
            )

        if not scheduler.get_job("create_task_upload"):
            scheduler.add_job(
                create_task_upload,
                CronTrigger.from_crontab("0 0 * * *"), # daily at 00:00
                id="create_task_upload",
                replace_existing=True
            )
        
        # if not scheduler.get_job("create_delete_task"):
        #     scheduler.add_job(
        #         create_delete_task,
        #         CronTrigger.from_crontab("* * * * *"),
        #         id="create_delete_task",
        #         replace_existing=True
        #     )
        
        print("🚀 Scheduler started")

    yield
    # Shutdown
    scheduler.shutdown()
    print("🛑 Scheduler stopped")