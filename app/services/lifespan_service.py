from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.task_service import create_task_record, create_task_predict, create_task_upload, task_delete
from app.services.task_execute_service import execute_record_api, execute_upload, execute_predict, execute_upload_max
from dotenv import load_dotenv
from app.configs.base_conf import settings

load_dotenv()
scheduler = AsyncIOScheduler()

def lifespan(app: FastAPI):
    scheduler.start()
    if settings.RUN_SCHEDULER == "true":
        # if not scheduler.get_job("create_task_record"):
        #     scheduler.add_job(
        #         create_task_record,
        #         CronTrigger.from_crontab(settings.CRON_CREATE_TASK_RECORD),
        #         id="create_task_record",
        #         replace_existing=True
        #     )

        # if not scheduler.get_job("create_task_predict"):
        #     scheduler.add_job(
        #         create_task_predict,
        #         CronTrigger.from_crontab(settings.CRON_CREATE_TASK_PREDICT),
        #         id="create_task_predict",
        #         replace_existing=True
        #     )

        # if not scheduler.get_job("create_task_upload"):
        #     scheduler.add_job(
        #         create_task_upload,
        #         CronTrigger.from_crontab(settings.CRON_CREATE_TASK_UPLOAD),
        #         id="create_task_upload",
        #         replace_existing=True
        #     )

        # EXECUTE TASK ===========================================================
        if not scheduler.get_job("execute_record_api"):
            scheduler.add_job(
                execute_record_api,
                CronTrigger.from_crontab(settings.CRON_EXECUTE_RECORD_API),
                id="execute_record_api",
                replace_existing=True
            )

        if not scheduler.get_job("execute_predict"):
            scheduler.add_job(
                execute_predict,
                CronTrigger.from_crontab(settings.CRON_EXECUTE_PREDICT),
                id="execute_predict",
                replace_existing=True
            )

        if not scheduler.get_job("execute_upload"):
            scheduler.add_job(
                execute_upload,
                CronTrigger.from_crontab(settings.CRON_EXECUTE_UPLOAD),
                id="execute_upload",
                replace_existing=True
            )

        
        if not scheduler.get_job("create_task_upload_max"):
            scheduler.add_job(
                execute_upload_max,
                CronTrigger.from_crontab(settings.CRON_EXECUTE_UPLOAD_MAX),
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