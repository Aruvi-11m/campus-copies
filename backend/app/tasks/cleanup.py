"""
Campus Copies ERP - Background Cleanup Tasks

Task runner purging temporary file uploads older than 24 hours.
Grounding: docs/BackendSpecification.md §10
"""

from sqlalchemy.orm import Session
from app.core.logging import logger
from app.services.storage_service import StorageService


def run_temporary_file_cleanup(db: Session) -> int:
    """
    Executes garbage collection purging expired temporary file records (>24h old).
    """
    try:
        service = StorageService(db)
        purged_count = service.cleanup_expired_temporary_files()
        logger.info("background_temp_file_cleanup_completed", purged_count=purged_count)
        return purged_count
    except Exception as err:
        logger.error("background_temp_file_cleanup_failed", error=str(err))
        return 0
