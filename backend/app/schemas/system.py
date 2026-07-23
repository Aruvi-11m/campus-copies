from pydantic import BaseModel


class SystemHealthResponse(BaseModel):
    status: str
    uptime: str
    version: str
    database_status: str
    storage_status: str
    cache_status: str
    environment: str
    python_version: str


class SystemBackupResponse(BaseModel):
    schema_version: str
    migration_version: str
    application_version: str
    last_backup_timestamp: str
    database_size_estimate: str
