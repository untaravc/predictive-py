from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.task_service import create_task_record, create_task_predict, create_task_upload, task_delete
from app.services.task_execute_service import execute_record_api, execute_record_sample
from dotenv import load_dotenv
import os

load_dotenv()
RUN_SCHEDULER = os.getenv("RUN_SCHEDULER")

scheduler = AsyncIOScheduler()

async def lifespan(app: FastAPI):
        scheduler.start()
        if RUN_SCHEDULER == "true":
            # if not scheduler.get_job("execute_record_api"):
            #     scheduler.add_job(
            #         execute_record_api,
            #         CronTrigger.from_crontab("* * * * *"), # daily
            #         id="execute_record_api",
            #         replace_existing=True
            #     )

            # if not scheduler.get_job("create_task_predict"):
            #     scheduler.add_job(
            #         create_task_predict,
            #         CronTrigger.from_crontab("* * * * *"),
            #         id="create_task_predict",
            #         replace_existing=True
            #     )

            # if not scheduler.get_job("create_task_upload"):
            #     scheduler.add_job(
            #         create_task_upload,
            #         CronTrigger.from_crontab("* * * * *"),
            #         id="create_task_upload",
            #         replace_existing=True
            #     )
            
            # if not scheduler.get_job("create_delete_task"):
            #     scheduler.add_job(
            #         create_delete_task,
            #         CronTrigger.from_crontab("* * * * *"),
            #         id="create_delete_task",
            #         replace_existing=True
            #     )
            
            # if not scheduler.get_job("execute_record_api"):
            #     scheduler.add_job(
            #         execute_record_api,
            #         CronTrigger.from_crontab("* * * * *"), # every minute
            #         id="execute_record_api",
            #         replace_existing=True
            #     )

            
            print("🚀 Scheduler started")

        yield
        # Shutdown
        scheduler.shutdown()
        print("🛑 Scheduler stopped")