"""
Campus Copies ERP - Structured Logging Module

Configures structlog for JSON structured logging with query param token redaction.
Grounding: docs/BackendSpecification.md §9, docs/SecuritySpecification.md §11
"""

import logging
import sys
import structlog
from app.config import settings


def redact_sensitive_params(logger: structlog.types.WrappedLogger, method_name: str, event_dict: structlog.types.EventDict) -> structlog.types.EventDict:
    """
    Processor to redact sensitive token or password fields from log events.
    """
    sensitive_keys = {"token", "password", "authorization", "jwt_secret", "service_role_key"}
    for key in list(event_dict.keys()):
        if key.lower() in sensitive_keys:
            event_dict[key] = "[REDACTED]"

    # Also redact sensitive query parameters from URLs in log events
    url = event_dict.get("url") or event_dict.get("path")
    if isinstance(url, str) and "token=" in url:
        import re
        event_dict["url"] = re.sub(r"token=[^&]+", "token=[REDACTED]", url)

    return event_dict


def setup_logging() -> None:
    """
    Initializes structlog logger configuration for application execution.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        redact_sensitive_params,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger("campus_copies")
