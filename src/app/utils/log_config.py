import logging
from logging.config import dictConfig
from typing import Dict, Any
import os

# Default logging configuration
DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "class": "app.utils.log_config.JsonFormatter",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": "logs/kma_chat_api.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "kma_chat_api": {"handlers": ["console", "file"], "level": "INFO"},
        "uvicorn": {"handlers": ["console"], "level": "INFO"},
        "uvicorn.access": {"handlers": ["console"], "level": "INFO"},
    },
    "root": {"level": "INFO", "handlers": ["console"], "propagate": True},
}


class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format"""
    import json
    
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "props"):
            log_record.update(record.props)
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return self.json.dumps(log_record)


def setup_logging(config: Dict[str, Any] = None) -> None:
    """Setup logging configuration"""
    
    # Ensure the logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Use the provided config or the default one
    config = config or DEFAULT_LOGGING_CONFIG
    
    # Apply the configuration
    dictConfig(config) 