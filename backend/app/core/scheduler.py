import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore

logger = logging.getLogger(__name__)

jobstores = {
    'default': MemoryJobStore()
}

scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="UTC")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shut down")

# Import the actual cleanup job from app.tasks.cleanup
from app.tasks.cleanup import cleanup_temporary_files

def setup_jobs():
    # Run everyday at midnight
    scheduler.add_job(
        cleanup_temporary_files, 
        'cron', 
        hour=0, 
        minute=0, 
        id='cleanup_temporary_files',
        replace_existing=True
    )
    logger.info("Configured job: cleanup_temporary_files")
