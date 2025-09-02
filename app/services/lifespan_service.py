from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.ip_api_service import periodic_call_api_task

scheduler = AsyncIOScheduler()

async def lifespan(app: FastAPI):
    scheduler.start()
    if not scheduler.get_job("periodic_call_api_task"):
        scheduler.add_job(
            periodic_call_api_task,
            CronTrigger.from_crontab("* * * * *"),
            id="periodic_call_api_task",
            replace_existing=True
        )
    print("🚀 Scheduler started")
    yield
    # Shutdown
    scheduler.shutdown()
    print("🛑 Scheduler stopped")